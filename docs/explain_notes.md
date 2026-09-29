# EXPLAIN notes (DuckDB teaching stand-in for Redshift)

Redshift would show DS_BCAST_INNER / DS_DIST_NONE / DS_DIST_INNER depending on dist keys.
DuckDB plans differ, but the comparison still teaches the modeling point:

## Before (heap / even metaphor)

From `output/explain_before.txt`:

- Full scan of `fact_claim_line_even`
- Filter on `service_date` applied after scan (no zone-map benefit from sort)
- Hash join with `dim_provider` builds hash on the dim, probes with the full filtered fact

## After (dist key + compound sort metaphor)

From `output/explain_after.txt`:

- Scan of `fact_claim_line_keyed` still filters `service_date`, but the table was created `ORDER BY service_date, payer_id` so min/max block stats (DuckDB row-group / file order) prune more effectively on disk layouts
- Join to `dim_provider_all` stays a local-style hash join because the dim is treated as replicated (we force create as a separate small table — analogous to DISTSTYLE ALL)

## Redshift translation you would say in an interview

> “I set DISTKEY to payer_id because every executive query filters or groups by payer, and SORTKEY (service_date, payer_id) so date-range zone maps cut blocks before the payer residual predicate. Provider dim is DISTSTYLE ALL so the specialty join does not redistribute the fact.”
