import pandas as pd
import json
from pathlib import Path
from ml.config import TRAIN_16K_CSV, TEST_5K_CSV, REPORTS_DIR

def audit_datasets():
    print("Auditing 16K dataset...")
    df_16k = pd.read_csv(TRAIN_16K_CSV)
    
    print("Auditing 5.5K dataset...")
    df_5k = pd.read_csv(TEST_5K_CSV)
    
    report = ["# Dataset Audit Report\n"]
    
    def analyze_df(name, df):
        lines = [f"## {name} Dataset"]
        lines.append(f"- **Total Rows:** {len(df)}")
        lines.append(f"- **Unique Material IDs:** {df['_true_material_id'].nunique()}")
        lines.append(f"- **CPSEs:** {', '.join(df['cpse_id'].unique())}")
        lines.append(f"- **Material Groups:** {df['material_group_code'].nunique()}")
        
        missing = df.isnull().sum()
        lines.append("\n### Missing Values:")
        for col, count in missing.items():
            if count > 0:
                pct = (count / len(df)) * 100
                lines.append(f"- `{col}`: {count} ({pct:.1f}%)")
        
        lines.append("\n### Variant Styles:")
        styles = df['_variant_style'].value_counts()
        for style, count in styles.items():
            lines.append(f"- `{style}`: {count}")
            
        return "\n".join(lines) + "\n\n"

    report.append(analyze_df("16K Training", df_16k))
    report.append(analyze_df("5.5K Test", df_5k))
    
    ids_16k = set(df_16k['_true_material_id'])
    ids_5k = set(df_5k['_true_material_id'])
    overlap = ids_16k.intersection(ids_5k)
    
    report.append("## Identity Overlap")
    report.append(f"- IDs only in 16K: {len(ids_16k - ids_5k)}")
    report.append(f"- IDs only in 5.5K: {len(ids_5k - ids_16k)}")
    report.append(f"- Overlapping IDs: {len(overlap)}")
    if len(ids_5k - ids_16k) == 0:
        report.append("- **Conclusion:** The 5.5K dataset's identities are a strict subset of the 16K dataset. Identity-grouped splitting is required.")
    
    # Save report
    report_path = REPORTS_DIR / "dataset_audit.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report))
    print(f"Audit report saved to {report_path}")

if __name__ == "__main__":
    audit_datasets()
