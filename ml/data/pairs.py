import pandas as pd
import json
import numpy as np
from pathlib import Path
from itertools import combinations
from tqdm import tqdm
from ml.config import TRAIN_16K_CSV, SPLITS_DIR, PAIRS_DATA_DIR

def generate_pairs():
    print("Loading 16K dataset...")
    df = pd.read_csv(TRAIN_16K_CSV)
    
    # Load splits
    splits = {}
    for split_name in ["train", "val", "test"]:
        with open(SPLITS_DIR / f"{split_name}_ids.json", "r") as f:
            splits[split_name] = set(json.load(f))
            
    # Process each split
    for split_name, split_ids in splits.items():
        print(f"\nGenerating pairs for {split_name} split...")
        df_split = df[df['_true_material_id'].isin(split_ids)].copy()
        
        pairs = []
        
        # Group by true identity for positive pairs
        groups = df_split.groupby('_true_material_id')
        
        # 1. Positive pairs (IDENTICAL / NEAR_DUPLICATE / FUNCTIONALLY_EQUIVALENT based on similarity, but structurally all positive for same ID)
        for material_id, group in tqdm(groups, desc=f"Positive pairs ({split_name})"):
            if len(group) > 1:
                # All combinations within the cluster
                indices = group.index.tolist()
                for i1, i2 in combinations(indices, 2):
                    rec1 = group.loc[i1]
                    rec2 = group.loc[i2]
                    
                    is_cross_cpse = int(rec1['cpse_id'] != rec2['cpse_id'])
                    pairs.append({
                        'id_a': rec1['material_code'],
                        'id_b': rec2['material_code'],
                        'label': 1,
                        'pair_type': 'cross_cpse_positive' if is_cross_cpse else 'same_cpse_positive'
                    })
        
        num_positives = len(pairs)
        print(f"Generated {num_positives} positive pairs.")
        
        # 2. Hard Negatives (Same material group, different identity)
        # We want roughly 2x hard negatives compared to positives
        hard_neg_target = num_positives * 2
        hard_negatives = []
        
        group_codes = df_split['material_group_code'].unique()
        for group_code in tqdm(group_codes, desc=f"Hard negative pairs ({split_name})"):
            df_group = df_split[df_split['material_group_code'] == group_code]
            id_clusters = df_group.groupby('_true_material_id')
            cluster_keys = list(id_clusters.groups.keys())
            
            if len(cluster_keys) > 1:
                # Sample random pairs between different clusters in the same material group
                samples_for_this_group = int(hard_neg_target * (len(df_group) / len(df_split)))
                
                attempts = 0
                while len(hard_negatives) < sum([int(hard_neg_target * (len(df_split[df_split['material_group_code'] == g]) / len(df_split))) for g in group_codes[:list(group_codes).index(group_code)+1]]) and attempts < samples_for_this_group * 5:
                    attempts += 1
                    c1, c2 = np.random.choice(cluster_keys, 2, replace=False)
                    idx1 = np.random.choice(id_clusters.groups[c1])
                    idx2 = np.random.choice(id_clusters.groups[c2])
                    
                    # Avoid duplicates
                    hard_negatives.append({
                        'id_a': df_group.loc[idx1]['material_code'],
                        'id_b': df_group.loc[idx2]['material_code'],
                        'label': 0,
                        'pair_type': 'hard_negative'
                    })
                    
        pairs.extend(hard_negatives)
        print(f"Generated {len(hard_negatives)} hard negative pairs.")
        
        # 3. Random Negatives (Different material group)
        # We want roughly 1x random negatives compared to positives
        random_neg_target = num_positives
        random_negatives = []
        
        attempts = 0
        while len(random_negatives) < random_neg_target and attempts < random_neg_target * 5:
            attempts += 1
            idx1, idx2 = np.random.choice(df_split.index, 2, replace=False)
            rec1 = df_split.loc[idx1]
            rec2 = df_split.loc[idx2]
            
            if rec1['material_group_code'] != rec2['material_group_code']:
                random_negatives.append({
                    'id_a': rec1['material_code'],
                    'id_b': rec2['material_code'],
                    'label': 0,
                    'pair_type': 'random_negative'
                })
                
        pairs.extend(random_negatives)
        print(f"Generated {len(random_negatives)} random negative pairs.")
        
        # Shuffle and save
        df_pairs = pd.DataFrame(pairs).drop_duplicates(subset=['id_a', 'id_b'])
        df_pairs = df_pairs.sample(frac=1, random_state=42).reset_index(drop=True)
        
        out_path = PAIRS_DATA_DIR / f"{split_name}_pairs.csv"
        df_pairs.to_csv(out_path, index=False)
        print(f"Saved {len(df_pairs)} total pairs to {out_path}\n")

if __name__ == "__main__":
    np.random.seed(42)
    generate_pairs()
