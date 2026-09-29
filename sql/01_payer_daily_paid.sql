-- Workload query used for before/after comparison
SELECT
    f.payer_id,
    p.payer_name,
    f.service_date,
    COUNT(*) AS claim_lines,
    SUM(f.paid_amount) AS paid_amount,
    SUM(f.allowed_amount) AS allowed_amount
FROM fact_claim_line f
JOIN dim_payer p ON f.payer_id = p.payer_id
WHERE f.service_date BETWEEN DATE '2025-07-01' AND DATE '2025-07-15'
GROUP BY f.payer_id, p.payer_name, f.service_date
ORDER BY f.service_date, paid_amount DESC;
