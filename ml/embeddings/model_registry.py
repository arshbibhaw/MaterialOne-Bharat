import json
from pathlib import Path
from typing import Dict, Any

from ml.config import EMBEDDING_MODEL_NAME, EMBEDDINGS_MODEL_DIR

def save_model_metadata(version: str, description: str):
    """
    Saves metadata about the embedding model being used.
    """
    metadata = {
        "model_name": EMBEDDING_MODEL_NAME,
        "version": version,
        "description": description,
        "framework": "sentence-transformers"
    }
    
    out_path = EMBEDDINGS_MODEL_DIR / f"metadata_v{version}.json"
    with open(out_path, "w") as f:
        json.dump(metadata, f, indent=2)
        
def load_model_metadata(version: str) -> Dict[str, Any]:
    path = EMBEDDINGS_MODEL_DIR / f"metadata_v{version}.json"
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {}
