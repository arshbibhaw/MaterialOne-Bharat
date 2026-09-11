import pandas as pd
import numpy as np
from typing import List, Dict, Any
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def tfidf_cosine_baseline(texts_a: List[str], texts_b: List[str]) -> np.ndarray:
    """
    Standard TF-IDF + Cosine Similarity baseline.
    """
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
    all_texts = list(set(texts_a + texts_b))
    vectorizer.fit(all_texts)
    
    vecs_a = vectorizer.transform(texts_a)
    vecs_b = vectorizer.transform(texts_b)
    
    # Pairwise cosine similarity
    scores = np.array([cosine_similarity(vecs_a[i], vecs_b[i])[0][0] for i in range(len(texts_a))])
    return scores

def fuzzy_matching_baseline(texts_a: List[str], texts_b: List[str]) -> np.ndarray:
    """
    Fuzzy string matching baseline (Token Sort Ratio).
    """
    scores = []
    for a, b in zip(texts_a, texts_b):
        scores.append(fuzz.token_sort_ratio(a, b) / 100.0)
    return np.array(scores)

def sbert_cosine_baseline(embedder, texts_a: List[str], texts_b: List[str]) -> np.ndarray:
    """
    SBERT embeddings + Cosine Similarity baseline.
    """
    emb_a = embedder.embed(texts_a)
    emb_b = embedder.embed(texts_b)
    
    # Since embeddings are L2 normalized, dot product = cosine similarity
    scores = np.sum(emb_a * emb_b, axis=1)
    return scores
