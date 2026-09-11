from typing import List, Dict, Any
from ml.embeddings.embedder import MaterialEmbedder
from ml.retrieval.faiss_index import MaterialIndex
from ml.config import FAISS_TOP_K

class CandidateGenerator:
    def __init__(self, embedder: MaterialEmbedder, index: MaterialIndex):
        self.embedder = embedder
        self.index = index
        
    def generate_candidates(self, profile: Dict[str, Any], top_k: int = FAISS_TOP_K) -> List[Dict[str, Any]]:
        """
        Generate candidates for a given material profile.
        """
        # Create text representation
        text = self.embedder.create_embedding_text(profile)
        
        # Embed
        embedding = self.embedder.embed(text)
        
        # Search index
        family = profile.get("family")
        # We can optionally disable the strict family filter if we want cross-family matches
        candidates = self.index.search(embedding, top_k=top_k, family_filter=family)
        
        return candidates
