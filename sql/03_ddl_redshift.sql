-- Redshift DDL (target warehouse). Local DuckDB recreates the intent in run_before_after.py.

CREATE TABLE dim_payer (
    payer_id    VARCHAR(16),
    payer_name  VARCHAR(64)
)
DISTSTYLE ALL
SORTKEY (payer_id);

CREATE TABLE dim_provider (
    provider_id   VARCHAR(16),
    provider_name VARCHAR(64),
    specialty     VARCHAR(32)
)
DISTSTYLE ALL
SORTKEY (provider_id);

-- BEFORE (anti-pattern)
CREATE TABLE fact_claim_line_even (
    claim_line_id   VARCHAR(32),
    payer_id        VARCHAR(16),
    provider_id     VARCHAR(16),
    service_date    DATE,
    allowed_amount  NUMERIC(18,2),
    paid_amount     NUMERIC(18,2)
)
DISTSTYLE EVEN;

-- AFTER
CREATE TABLE fact_claim_line (
    claim_line_id   VARCHAR(32),
    payer_id        VARCHAR(16),
    provider_id     VARCHAR(16),
    service_date    DATE,
    allowed_amount  NUMERIC(18,2),
    paid_amount     NUMERIC(18,2)
)
DISTSTYLE KEY
DISTKEY (payer_id)
COMPOUND SORTKEY (service_date, payer_id);
