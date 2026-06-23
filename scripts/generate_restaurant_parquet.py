"""Generate data/restaurant.parquet from the Hugging Face Zomato dataset."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.parquet_exporter import export_restaurants_parquet


def main() -> None:
    output = ROOT / "data" / "restaurant.parquet"
    out_path, success, failed = export_restaurants_parquet(output)
    print(f"Wrote {success} restaurants to {out_path}")
    if failed:
        print(f"Skipped {failed} rows due to preprocessing errors.")


if __name__ == "__main__":
    main()
