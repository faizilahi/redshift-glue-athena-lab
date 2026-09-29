# Redshift Dist/Sort Key Choice on a Synthetic Claim Fact: Before, After, and EXPLAIN Notes

Faiz Elahi — [LinkedIn](https://www.linkedin.com/in/faizilahi) — [pendataco.com](https://pendataco.com) — [GitHub](https://github.com/faizilahi)

Claim-line facts and payer/provider dims in this lab are generated.

## The modeling decision

`fact_claim_line` is queried constantly as:

```sql
SELECT payer_id, service_date, SUM(paid_amount)
FROM fact_claim_line
WHERE service_date BETWEEN ... AND ...
GROUP BY payer_id, service_date
```

and joined to `dim_provider` on `provider_id` for specialty rollups.

### Keys chosen

| Table | DISTSTYLE / DISTKEY | SORTKEY | Why |
|-------|---------------------|---------|-----|
| `fact_claim_line` | KEY on `payer_id` | COMPOUND (`service_date`, `payer_id`) | Predicate + group both hit payer; date range zone-maps via sort |
| `dim_provider` | ALL | `provider_id` | Small dim — replicate to every node to avoid redistribute on join |
| `dim_payer` | ALL | `payer_id` | Same |

### What was wrong before

Fact was `DISTSTYLE EVEN` with no sort key. The payer filter scanned every block; the provider join redistributed the fact on every run.

## Before / after query

Same SQL in `sql/01_payer_daily_paid.sql`. Runner executes against:

1. **Heap-style table** (no sort, even distribution metaphor)  
2. **Keyed + sorted table**

Wall times and row counts print side by side. EXPLAIN-style notes in `docs/explain_notes.md` are written from the **actual DuckDB `EXPLAIN` plan** for each shape — clearly labeled as the teaching stand-in for Redshift `EXPLAIN` / `SVL_QUERY_REPORT`.

## Glue + Athena adjacent path

`glue_catalog.json` and `s3standin/` show how the same fact lands in S3 for Athena ad-hoc while Redshift Spectrum / exported Parquet shares the partition layout `service_date=...`.

## Run

```powershell
cd redshift-glue-athena-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/generate_fact.py
python src/run_before_after.py
```
