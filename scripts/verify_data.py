import sys
from pathlib import Path
import pandas as pd

def verify_datasets():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    required_files = [
        "bhopal_ghats_2023_2025.csv",
        "cpcb_water_quality_criteria.csv",
        "sample_bhopal_2025.csv",
        "mp_immersion_sites_2023_2025.csv"
    ]
    
    passed = True
    for fname in required_files:
        fpath = data_dir / fname
        if not fpath.exists():
            print(f"[FAIL] Missing {fname}")
            passed = False
            continue
        try:
            df = pd.read_csv(fpath)
            print(f"[PASS] {fname}: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            print(f"[FAIL] Error reading {fname}: {e}")
            passed = False
            
    if not passed:
        sys.exit(1)
    print("All datasets verified successfully.")

if __name__ == "__main__":
    verify_datasets()
