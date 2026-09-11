"""
Phase E: Retrieval Evaluation
Evaluates Recall@5, 10, 20, 50 of the FAISS index using true identity clusters.
"""
import pandas as pd
from collections import defaultdict
from ml.embeddings.embedder import get_embedder
from ml.retrieval.faiss_index import MaterialIndex
from ml.config import TRAIN_16K_CSV

def main():
    print("=" * 60)
    print("Retrieval Evaluation (Recall@K)")
    print("=" * 60)
    
    # 1. Load data to get true clusters
    df = pd.read_csv(TRAIN_16K_CSV)
    
    # Map each true material ID to a list of its material codes
    clusters = defaultdict(list)
    code_to_true_id = {}
    code_to_desc = {}
    
    for _, row in df.iterrows():
        code = str(row["material_code"])
        tid = str(row["_true_material_id"])
        clusters[tid].append(code)
        code_to_true_id[code] = tid
        code_to_desc[code] = str(row["material_description"])
        
    # We only care about materials that have at least one OTHER material in the same cluster
    eval_codes = [c for c in df["material_code"] if len(clusters[code_to_true_id[str(c)]]) > 1]
    
    # Take a sample for evaluation speed
    import random
    random.seed(42)
    sample_codes = random.sample(eval_codes, min(2000, len(eval_codes)))
    
    # 2. Load FAISS and embedder
    index = MaterialIndex()
    index.load("training_16k")
    embedder = get_embedder()
    
    # 3. Evaluate Recall@K
    recalls = {5: 0, 10: 0, 20: 0, 50: 0}
    total = len(sample_codes)
    
    print(f"Evaluating {total} items with known matches...")
    
    # Encode all queries at once
    queries = [code_to_desc[c] for c in sample_codes]
    query_embeddings = embedder.embed(queries)
    
    for i, code in enumerate(sample_codes):
        true_id = code_to_true_id[code]
        expected_matches = set(clusters[true_id]) - {code}
        
        # Search for top 50
        results = index.search(query_embeddings[i], top_k=50)
        retrieved_codes = [r["material_code"] for r in results]
        
        # We consider a "hit" if AT LEAST ONE expected match is retrieved
        for k in recalls.keys():
            top_k_retrieved = set(retrieved_codes[:k])
            if len(expected_matches.intersection(top_k_retrieved)) > 0:
                recalls[k] += 1
                
        if (i+1) % 500 == 0:
            print(f"  Processed {i+1}/{total}...")
            
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for k in sorted(recalls.keys()):
        acc = recalls[k] / total
        print(f"Recall@{k:2d}: {acc:.4f} ({recalls[k]}/{total})")

if __name__ == "__main__":
    main()
