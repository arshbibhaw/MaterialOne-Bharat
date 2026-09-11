"""
Phase D: Build FAISS Index
Computes embeddings for all 16,000 materials and builds the vector index.
"""
import pandas as pd
from ml.embeddings.embedder import get_embedder
from ml.api.main import generate_profile
from ml.api.schemas import MaterialRecord
from ml.retrieval.faiss_index import MaterialIndex
from ml.config import TRAIN_16K_CSV

def main():
    print("=" * 60)
    print("Building FAISS Index (16K Training Set)")
    print("=" * 60)
    
    df = pd.read_csv(TRAIN_16K_CSV)
    embedder = get_embedder()
    index = MaterialIndex()
    
    batch_size = 500
    material_codes = []
    families = []
    texts = []
    
    total = len(df)
    
    for i, row in df.iterrows():
        p = generate_profile(MaterialRecord(
            cpse_id=str(row.get("cpse_id", "")), material_code=str(row.get("material_code", "")),
            material_description=str(row.get("material_description", "")),
            material_long_text=str(row.get("material_long_text", "")),
            material_group_code=str(row.get("material_group_code", "")),
            uom=str(row.get("uom", "")), manufacturer=str(row.get("manufacturer", ""))
        ))
        
        # We index the full rich profile text (including attributes)
        texts.append(embedder.create_embedding_text(p))
        material_codes.append(p["source_material_code"])
        families.append(p["family"])
        
        if len(texts) >= batch_size or i == total - 1:
            embeddings = embedder.embed(texts)
            index.add_items(embeddings, material_codes, families)
            print(f"  Indexed {index.current_idx}/{total} records...")
            
            texts = []
            material_codes = []
            families = []
            
    print("\nSaving index...")
    index.save("training_16k")
    print("Done!")

if __name__ == "__main__":
    main()
