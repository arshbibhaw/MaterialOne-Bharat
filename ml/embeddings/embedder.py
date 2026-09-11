import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from ml.config import EMBEDDING_MODEL_NAME

class MaterialEmbedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        # Load the SBERT model. This downloads it if not cached.
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        
    def create_embedding_text(self, profile: dict) -> str:
        """
        Creates the text representation to be embedded from a material profile.
        Concatenates category, normalized description, and key attributes.
        """
        family = profile.get("family", "")
        norm_desc = profile.get("normalized_description", "")
        
        attrs = []
        for k, v in profile.get("attributes", {}).items():
            val = v.get("normalized", "")
            unit = v.get("unit", "")
            attrs.append(f"{k}: {val} {unit}".strip())
            
        attr_text = " | ".join(attrs)
        
        # Format: [FAMILY] normalized description [ATTRS]
        text = f"[{family}] {norm_desc} {attr_text}".strip()
        return text
        
    def embed(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a single text or list of texts.
        Returns L2-normalized embeddings for cosine similarity via inner product.
        """
        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]
            
        # normalize_embeddings=True makes inner product equivalent to cosine similarity
        embeddings = self.model.encode(texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=len(texts)>100)
        
        if is_single:
            return embeddings[0]
        return embeddings

# Singleton instance
_embedder = None

def get_embedder() -> MaterialEmbedder:
    global _embedder
    if _embedder is None:
        _embedder = MaterialEmbedder()
    return _embedder
