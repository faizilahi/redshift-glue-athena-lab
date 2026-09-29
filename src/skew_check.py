"""Payer distkey skew report — interview talking point for DIST_STYLE KEY."""
from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def main() -> None:
    con = duckdb.connect()
    con.execute(
        f"CREATE TABLE fact AS SELECT * FROM read_csv_auto('{(DATA / 'fact_claim_line.csv').as_posix()}')"
    )
    rows = con.execute(
        """
        SELECT payer_id,
               COUNT(*) AS rows,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
        FROM fact
        GROUP BY 1
        ORDER BY rows DESC
        """
    ).fetchall()
    print("payer_skew:")
    for r in rows:
        print(" ", r)
    max_pct = max(r[2] for r in rows)
    print(f"max_slice_pct={max_pct} (watch for >30% on a KEY dist)")


if __name__ == "__main__":
    main()
