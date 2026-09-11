import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Any

from ml.config import FAISS_INDEX_DIR

class MaterialIndex:
    def __init__(self, dimension: int = 384):
        # IndexFlatIP uses Inner Product. Since vectors are L2 normalized, IP == Cosine Similarity
        self.index = faiss.IndexFlatIP(dimension)
        self.id_map = {}  # Maps FAISS index (int) to material_code (str)
        self.metadata = {} # Stores material family for pre-filtering
        self.current_idx = 0
        
    def add_items(self, embeddings: np.ndarray, material_codes: List[str], families: List[str] = None):
        """Add items to the FAISS index."""
        if len(embeddings) != len(material_codes):
            raise ValueError("Embeddings and material_codes must have same length")
            
        self.index.add(np.array(embeddings, dtype=np.float32))
        
        for i, code in enumerate(material_codes):
            self.id_map[self.current_idx + i] = code
            if families:
                self.metadata[code] = {"family": families[i]}
                
        self.current_idx += len(embeddings)
        
    def search(self, query_embedding: np.ndarray, top_k: int = 20, family_filter: str = None) -> List[Dict[str, Any]]:
        """Search the index. Supports post-filtering by family."""
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        # Retrieve more candidates if we are filtering, to ensure we get top_k after filter
        search_k = top_k * 5 if family_filter else top_k
        
        scores, indices = self.index.search(np.array(query_embedding, dtype=np.float32), search_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx == -1: continue # Not enough results
            
            code = self.id_map[idx]
            
            if family_filter:
                item_family = self.metadata.get(code, {}).get("family")
                if item_family and item_family != family_filter:
                    continue
                    
            results.append({
                "material_code": code,
                "score": float(score),
                "rank": len(results) + 1
            })
            
            if len(results) >= top_k:
                break
                
        return results
        
    def save(self, name: str = "default"):
        path = FAISS_INDEX_DIR / name
        path.mkdir(exist_ok=True)
        
        faiss.write_index(self.index, str(path / "index.faiss"))
        with open(path / "mapping.pkl", "wb") as f:
            pickle.dump({"id_map": self.id_map, "metadata": self.metadata, "current_idx": self.current_idx}, f)
            
    def load(self, name: str = "default"):
        path = FAISS_INDEX_DIR / name
        self.index = faiss.read_index(str(path / "index.faiss"))
        with open(path / "mapping.pkl", "rb") as f:
            data = pickle.load(f)
            self.id_map = data["id_map"]
            self.metadata = data["metadata"]
            self.current_idx = data["current_idx"]
