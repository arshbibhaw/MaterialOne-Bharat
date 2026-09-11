import pandas as pd
import json
from sklearn.model_selection import GroupShuffleSplit
from ml.config import TRAIN_16K_CSV, SPLITS_DIR

def create_splits(random_state=42):
    print("Loading 16K dataset for splitting...")
    df = pd.read_csv(TRAIN_16K_CSV)
    
    # We need an identity-safe split based on _true_material_id
    # Target: 70% train, 15% val, 15% test
    
    groups = df['_true_material_id'].values
    
    # First split: 70% train, 30% temp (val+test)
    gss1 = GroupShuffleSplit(n_splits=1, train_size=0.7, random_state=random_state)
    train_idx, temp_idx = next(gss1.split(df, groups=groups))
    
    df_train = df.iloc[train_idx]
    df_temp = df.iloc[temp_idx]
    
    # Second split: split the 30% temp into 50/50 for val/test (which gives 15% overall each)
    groups_temp = df_temp['_true_material_id'].values
    gss2 = GroupShuffleSplit(n_splits=1, train_size=0.5, random_state=random_state)
    val_idx_temp, test_idx_temp = next(gss2.split(df_temp, groups=groups_temp))
    
    df_val = df_temp.iloc[val_idx_temp]
    df_test = df_temp.iloc[test_idx_temp]
    
    print(f"Train rows: {len(df_train)} (IDs: {df_train['_true_material_id'].nunique()})")
    print(f"Val rows: {len(df_val)} (IDs: {df_val['_true_material_id'].nunique()})")
    print(f"Test rows: {len(df_test)} (IDs: {df_test['_true_material_id'].nunique()})")
    
    # Validate no leakage
    train_ids = set(df_train['_true_material_id'])
    val_ids = set(df_val['_true_material_id'])
    test_ids = set(df_test['_true_material_id'])
    
    assert len(train_ids.intersection(val_ids)) == 0, "Leakage between train and val"
    assert len(train_ids.intersection(test_ids)) == 0, "Leakage between train and test"
    assert len(val_ids.intersection(test_ids)) == 0, "Leakage between val and test"
    print("Validation passed: No ID leakage across splits.")
    
    # Save split definitions (just the material IDs to keep it clean)
    splits = {
        "train": list(train_ids),
        "val": list(val_ids),
        "test": list(test_ids)
    }
    
    for split_name, split_ids in splits.items():
        out_path = SPLITS_DIR / f"{split_name}_ids.json"
        with open(out_path, "w") as f:
            json.dump(split_ids, f)
        print(f"Saved {len(split_ids)} IDs to {out_path}")

if __name__ == "__main__":
    create_splits()
