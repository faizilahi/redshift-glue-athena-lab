-- Join that benefits from DISTSTYLE ALL on dim_provider
SELECT
    d.specialty,
    COUNT(*) AS claim_lines,
    SUM(f.paid_amount) AS paid_amount
FROM fact_claim_line f
JOIN dim_provider d ON f.provider_id = d.provider_id
WHERE f.service_date BETWEEN DATE '2025-07-01' AND DATE '2025-07-31'
GROUP BY d.specialty
ORDER BY paid_amount DESC;
