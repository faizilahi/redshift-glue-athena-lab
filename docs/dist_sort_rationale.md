# Dist and sort rationale (worked example)

## Query shape
Date-bounded payer daily paid, plus occasional provider specialty rollup.

## DISTKEY = payer_id
Co-locates fact rows that share a payer so `GROUP BY payer_id` avoids a network redistribute for the common path.

## COMPOUND SORTKEY (service_date, payer_id)
Zone maps skip blocks outside the date window first; residual payer filter rides the second sort column.

## DISTSTYLE ALL on dims
`dim_payer` and `dim_provider` are small. Replicating them makes the specialty join `DS_DIST_NONE` on the fact side.

## What EVEN cost us
Full block scans on every date filter and a redistribute into the provider hash join — visible as longer `return` time in the before run and a wider scan node in the DuckDB EXPLAIN stand-in.
