-- Redshift Spectrum overlay on the same S3 export Athena reads
CREATE EXTERNAL SCHEMA spectrum_rs
FROM DATA CATALOG
DATABASE 'rs_export'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftSpectrumRole'
CREATE EXTERNAL DATABASE IF NOT EXISTS;

-- Validate Spectrum vs local fact for one day
SELECT COUNT(*) FROM spectrum_rs.fact_claim_line
WHERE service_date = DATE '2025-07-01';
