"""CLI entrypoint for restaurant recommendations."""

from __future__ import annotations

import argparse
import sys

from src.models.preferences import PreferenceValidationError
from src.presentation.formatters import format_service_result
from src.services.recommendation_service import create_default_service


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Zomato-style AI restaurant recommendations (Groq-powered)."
    )
    parser.add_argument("--location", required=True, help="City or area, e.g. Bangalore")
    parser.add_argument(
        "--budget",
        required=True,
        choices=["low", "medium", "high"],
        help="Budget tier",
    )
    parser.add_argument(
        "--cuisine",
        required=True,
        help="Preferred cuisine(s), comma-separated",
    )
    parser.add_argument(
        "--min-rating",
        type=float,
        required=True,
        help="Minimum rating (0-5)",
    )
    parser.add_argument(
        "--additional",
        default="",
        help="Optional preferences, e.g. family-friendly, quick service",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = build_parser().parse_args(argv)

    raw = {
        "location": args.location,
        "budget": args.budget,
        "cuisine": args.cuisine,
        "min_rating": args.min_rating,
        "additional_preferences": args.additional or None,
    }

    try:
        service = create_default_service()
        result = service.recommend(raw)
    except (ValueError, PreferenceValidationError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(format_service_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
