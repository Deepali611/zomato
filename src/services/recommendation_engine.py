from __future__ import annotations

import json
import time
from typing import Dict, List, Optional

from src.observability import get_logger, log_event
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationItem, RecommendationResult
from src.models.restaurant import Restaurant
from src.services.llm_client import LLMClient, LLMClientError, LLMTimeoutError
from src.services.prompt_builder import build_recommendation_prompt

logger = get_logger(__name__)


def _deterministic_fallback(
    candidates: List[Restaurant],
    *,
    top_k: int,
    warning: str,
) -> RecommendationResult:
    ordered = sorted(
        candidates,
        key=lambda r: (r.rating is not None, r.rating or -1.0),
        reverse=True,
    )[:top_k]
    items = [
        RecommendationItem(
            restaurant_id=r.id,
            rank=idx + 1,
            explanation="Ranked by deterministic fallback (rating and filters) due to AI unavailability.",
            name=r.name,
            cuisines=r.cuisines,
            rating=r.rating,
            cost_for_two=r.cost_for_two,
        )
        for idx, r in enumerate(ordered)
    ]
    return RecommendationResult(
        summary=None,
        recommendations=items,
        degraded=True,
        warnings=[warning],
    )


def _parse_json_response(raw_text: str) -> Optional[dict]:
    try:
        payload = json.loads(raw_text)
    except (TypeError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    if "recommendations" not in payload or not isinstance(payload["recommendations"], list):
        return None
    return payload


def _build_repair_prompt(raw_text: str) -> str:
    return (
        "Reformat the following content into valid JSON with keys "
        "`summary` and `recommendations` where recommendations is a list of "
        "objects containing `restaurant_id`, `rank`, `explanation`. "
        "Return only JSON.\n\n"
        f"Content:\n{raw_text}"
    )


def _safe_int(value: object, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _merge_recommendations(
    parsed: dict,
    candidate_map: Dict[str, Restaurant],
    *,
    top_k: int,
) -> RecommendationResult:
    raw_items = parsed.get("recommendations", [])
    merged: List[RecommendationItem] = []
    dropped = 0
    seen = set()

    for idx, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            continue
        restaurant_id = str(raw.get("restaurant_id", "")).strip()
        if not restaurant_id or restaurant_id in seen:
            continue
        if restaurant_id not in candidate_map:
            dropped += 1
            continue
        seen.add(restaurant_id)
        restaurant = candidate_map[restaurant_id]
        merged.append(
            RecommendationItem(
                restaurant_id=restaurant_id,
                rank=_safe_int(raw.get("rank"), idx + 1),
                explanation=str(raw.get("explanation", "")).strip() or "No explanation provided.",
                name=restaurant.name,
                cuisines=restaurant.cuisines,
                rating=restaurant.rating,
                cost_for_two=restaurant.cost_for_two,
            )
        )
        if len(merged) >= top_k:
            break

    warnings: List[str] = []
    if dropped:
        warnings.append(f"Dropped {dropped} hallucinated recommendation(s) not in candidates.")

    # If model returns fewer than top_k, backfill deterministically from remaining candidates.
    if len(merged) < top_k:
        remainder = [
            r
            for r in sorted(
                candidate_map.values(),
                key=lambda rr: (rr.rating is not None, rr.rating or -1.0),
                reverse=True,
            )
            if r.id not in seen
        ]
        for r in remainder:
            merged.append(
                RecommendationItem(
                    restaurant_id=r.id,
                    rank=len(merged) + 1,
                    explanation="Backfilled by deterministic ranking due to short AI output.",
                    name=r.name,
                    cuisines=r.cuisines,
                    rating=r.rating,
                    cost_for_two=r.cost_for_two,
                )
            )
            if len(merged) >= top_k:
                break
        if remainder:
            warnings.append("Some items were backfilled because AI returned fewer than TOP_K.")

    summary_raw = parsed.get("summary")
    summary = str(summary_raw).strip() if summary_raw is not None else None
    return RecommendationResult(
        summary=summary or None,
        recommendations=merged,
        degraded=False,
        warnings=warnings,
    )


def generate_recommendations(
    preferences: UserPreferences,
    candidates: List[Restaurant],
    llm_client: LLMClient,
    *,
    top_k: int = 5,
    max_retries: int = 1,
) -> RecommendationResult:
    """
    Generate ranked recommendations with explanations using LLM + validation.
    """
    if not candidates:
        log_event(logger, "llm_skipped", reason="no_candidates")
        return RecommendationResult(
            summary=None,
            recommendations=[],
            degraded=False,
            warnings=["No candidates available; LLM was not called."],
        )

    prompt_payload = build_recommendation_prompt(preferences, candidates, top_k=top_k)
    candidate_map = {r.id: r for r in candidates}
    log_event(
        logger,
        "llm_request_start",
        candidate_count=len(candidates),
        top_k=top_k,
        location=preferences.location,
    )

    started = time.perf_counter()
    try:
        raw_response = llm_client.complete(prompt_payload.prompt)
    except LLMTimeoutError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        log_event(logger, "llm_timeout", latency_ms=round(elapsed_ms, 2), error=str(exc))
        return _deterministic_fallback(
            candidates,
            top_k=top_k,
            warning="LLM timeout. Used deterministic fallback.",
        )
    except LLMClientError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        log_event(logger, "llm_client_error", latency_ms=round(elapsed_ms, 2), error=str(exc))
        return _deterministic_fallback(
            candidates,
            top_k=top_k,
            warning=f"LLM client error ({exc}). Used deterministic fallback.",
        )

    elapsed_ms = (time.perf_counter() - started) * 1000
    log_event(logger, "llm_response_received", latency_ms=round(elapsed_ms, 2))

    parsed = _parse_json_response(raw_response)
    if parsed is None:
        log_event(logger, "llm_parse_failed", attempt=1)
        for attempt in range(1, max_retries + 1):
            try:
                repaired = llm_client.complete(_build_repair_prompt(raw_response))
                parsed = _parse_json_response(repaired)
                if parsed is not None:
                    log_event(logger, "llm_parse_repaired", attempt=attempt)
                    break
            except LLMClientError as exc:
                log_event(logger, "llm_repair_failed", attempt=attempt, error=str(exc))
                parsed = None

    if parsed is None:
        log_event(logger, "llm_parse_failed_final", latency_ms=round(elapsed_ms, 2))
        return _deterministic_fallback(
            candidates,
            top_k=top_k,
            warning="Invalid LLM JSON output. Used deterministic fallback.",
        )

    result = _merge_recommendations(parsed, candidate_map, top_k=top_k)
    log_event(
        logger,
        "llm_recommendations_ready",
        result_count=len(result.recommendations),
        degraded=result.degraded,
        warning_count=len(result.warnings),
        latency_ms=round(elapsed_ms, 2),
    )
    return result

