"""Confirm synthetic fact CSV is present."""
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "data" / "fact_claim_line.csv"
print("fact_exists", p.exists(), "bytes", p.stat().st_size if p.exists() else 0)
