import numpy as np
from rapidfuzz import fuzz
from typing import Dict, Any, List

def calculate_similarity_features(profile_a: Dict[str, Any], profile_b: Dict[str, Any], embedder=None) -> Dict[str, float]:
    """
    Generate pairwise similarity features for ML model.
    """
    features = {}
    
    # 1. Semantic (if embedder is available)
    if embedder:
        text_a = embedder.create_embedding_text(profile_a)
        text_b = embedder.create_embedding_text(profile_b)
        
        emb_a = embedder.embed(text_a)
        emb_b = embedder.embed(text_b)
        
        # Dot product of normalized vectors = cosine similarity
        features['embedding_cosine_similarity'] = float(np.dot(emb_a, emb_b))
    else:
        features['embedding_cosine_similarity'] = 0.0
        
    # 2. Text similarity
    desc_a = profile_a.get("normalized_description", "")
    desc_b = profile_b.get("normalized_description", "")
    
    features['normalized_description_similarity'] = fuzz.token_sort_ratio(desc_a, desc_b) / 100.0
    
    long_a = profile_a.get("material_long_text", "")
    long_b = profile_b.get("material_long_text", "")
    if long_a and long_b:
        features['long_text_similarity'] = fuzz.partial_ratio(long_a, long_b) / 100.0
    else:
        features['long_text_similarity'] = 0.0
        
    # 3. Attribute Agreement
    attrs_a = profile_a.get("attributes", {})
    attrs_b = profile_b.get("attributes", {})
    
    common_keys = set(attrs_a.keys()).intersection(set(attrs_b.keys()))
    all_keys = set(attrs_a.keys()).union(set(attrs_b.keys()))
    
    if all_keys:
        agree = sum(1 for k in common_keys if attrs_a[k].get("normalized") == attrs_b[k].get("normalized"))
        conflict = sum(1 for k in common_keys if attrs_a[k].get("normalized") != attrs_b[k].get("normalized"))
        
        features['overall_attribute_agreement'] = agree / len(all_keys)
        features['attribute_conflict_count'] = float(conflict)
        features['missing_attribute_count'] = float(len(all_keys) - len(common_keys))
    else:
        features['overall_attribute_agreement'] = 0.0
        features['attribute_conflict_count'] = 0.0
        features['missing_attribute_count'] = 0.0
        
    # 4. Taxonomy
    features['same_family'] = float(profile_a.get("family", "A") == profile_b.get("family", "B"))
    
    # 5. Metadata
    mfr_a = profile_a.get("manufacturer", "")
    mfr_b = profile_b.get("manufacturer", "")
    
    if mfr_a and mfr_b:
        features['manufacturer_similarity'] = fuzz.ratio(str(mfr_a).lower(), str(mfr_b).lower()) / 100.0
    else:
        features['manufacturer_similarity'] = 0.0
        
    return features
