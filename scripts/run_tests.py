"""Run full test suite and write a summary report."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs" / "TEST_REPORT.md"
JUNIT_PATH = ROOT / "docs" / "test-results.xml"


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "--tb=short",
        f"--junitxml={JUNIT_PATH}",
        "-m",
        "not e2e",
    ]
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)

    status = "PASSED" if proc.returncode == 0 else "FAILED"
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Test Report",
                "",
                f"- **Generated:** {datetime.now(timezone.utc).isoformat()}",
                f"- **Status:** {status}",
                f"- **JUnit XML:** `{JUNIT_PATH.relative_to(ROOT)}`",
                "",
                "## Command",
                "",
                "```bash",
                "python scripts/run_tests.py",
                "```",
                "",
                "## Output (last run)",
                "",
                "```",
                proc.stdout[-8000:] if len(proc.stdout) > 8000 else proc.stdout,
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"\nReport written to {REPORT_PATH}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
