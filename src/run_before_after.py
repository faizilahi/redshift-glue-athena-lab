"""Load even vs keyed tables, run the same query, capture EXPLAIN plans."""
from __future__ import annotations

import time
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)


def main() -> None:
    con = duckdb.connect(str(ROOT / "redshift_sim.duckdb"))
    con.execute(
        f"""
        CREATE OR REPLACE TABLE dim_payer AS
        SELECT * FROM read_csv_auto('{(DATA / 'dim_payer.csv').as_posix()}');
        CREATE OR REPLACE TABLE dim_provider_all AS
        SELECT * FROM read_csv_auto('{(DATA / 'dim_provider.csv').as_posix()}');
        """
    )
    # BEFORE: unordered insert (even / heap metaphor)
    con.execute("DROP TABLE IF EXISTS fact_claim_line_even")
    con.execute(
        f"""
        CREATE TABLE fact_claim_line_even AS
        SELECT * FROM read_csv_auto('{(DATA / 'fact_claim_line.csv').as_posix()}')
        """
    )
    # AFTER: ordered by sort key columns (compound sort metaphor)
    con.execute("DROP TABLE IF EXISTS fact_claim_line_keyed")
    con.execute(
        """
        CREATE TABLE fact_claim_line_keyed AS
        SELECT * FROM fact_claim_line_even
        ORDER BY service_date, payer_id
        """
    )

    query_body = """
        SELECT
            f.payer_id,
            p.payer_name,
            f.service_date,
            COUNT(*) AS claim_lines,
            SUM(f.paid_amount) AS paid_amount,
            SUM(f.allowed_amount) AS allowed_amount
        FROM {fact} f
        JOIN dim_payer p ON f.payer_id = p.payer_id
        WHERE CAST(f.service_date AS DATE) BETWEEN DATE '2025-07-01' AND DATE '2025-07-15'
        GROUP BY f.payer_id, p.payer_name, f.service_date
        ORDER BY f.service_date, paid_amount DESC
    """

    for label, table in [("before", "fact_claim_line_even"), ("after", "fact_claim_line_keyed")]:
        sql = query_body.format(fact=table)
        plan = con.execute("EXPLAIN " + sql).fetchall()
        (OUT / f"explain_{label}.txt").write_text(
            "\n".join(str(r[0]) if isinstance(r, tuple) else str(r) for r in plan),
            encoding="utf-8",
        )
        # Also capture EXPLAIN ANALYZE if available
        try:
            plan_a = con.execute("EXPLAIN ANALYZE " + sql).fetchall()
            (OUT / f"explain_analyze_{label}.txt").write_text(
                "\n".join(str(r[0]) if isinstance(r, tuple) else str(r) for r in plan_a),
                encoding="utf-8",
            )
        except Exception as exc:
            (OUT / f"explain_analyze_{label}.txt").write_text(f"unavailable: {exc}", encoding="utf-8")

        t0 = time.perf_counter()
        rows = con.execute(sql).fetchall()
        elapsed = time.perf_counter() - t0
        print(f"{label}: rows={len(rows)} elapsed_sec={elapsed:.4f}")
        if rows:
            print(f"  sample={rows[0]}")

    # Specialty rollup (ALL dim metaphor)
    spec = con.execute(
        """
        SELECT d.specialty, COUNT(*) AS claim_lines, ROUND(SUM(f.paid_amount),2) AS paid_amount
        FROM fact_claim_line_keyed f
        JOIN dim_provider_all d ON f.provider_id = d.provider_id
        WHERE CAST(f.service_date AS DATE) BETWEEN DATE '2025-07-01' AND DATE '2025-07-31'
        GROUP BY d.specialty
        ORDER BY paid_amount DESC
        """
    ).fetchall()
    print("specialty_rollup:")
    for r in spec:
        print(" ", r)

    print("EXPLAIN plans written under output/ (DuckDB stand-in for Redshift EXPLAIN)")


if __name__ == "__main__":
    main()
