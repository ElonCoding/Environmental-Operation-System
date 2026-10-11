import json
from pathlib import Path
import pandas as pd

def export_json():
    root = Path(__file__).resolve().parent.parent
    csv_file = root / "data" / "bhopal_ghats_2023_2025.csv"
    out_file = root / "data" / "bhopal_ghats_summary.json"
    
    if csv_file.exists():
        df = pd.read_csv(csv_file)
        summary = {
            "total_records": len(df),
            "columns": list(df.columns),
            "sample": df.head(5).to_dict(orient="records")
        }
        with open(out_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Exported summary to {out_file}")

if __name__ == "__main__":
    export_json()
