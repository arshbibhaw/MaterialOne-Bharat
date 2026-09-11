import xgboost as xgb
import numpy as np
from typing import Dict, Any, List

class HybridMatcher:
    def __init__(self):
        self.model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='logloss',
            max_depth=6,
            learning_rate=0.1,
            n_estimators=200,
            min_child_weight=3,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=1.0
        )
        self.is_trained = False
        
        self.feature_names = [
            'embedding_cosine_similarity',
            'normalized_description_similarity',
            'long_text_similarity',
            'overall_attribute_agreement',
            'attribute_conflict_count',
            'missing_attribute_count',
            'same_family',
            'manufacturer_similarity'
        ]
        
    def _vectorize_features(self, features_dict: Dict[str, float]) -> np.ndarray:
        return np.array([features_dict.get(f, 0.0) for f in self.feature_names]).reshape(1, -1)
        
    def train(self, X_dicts: List[Dict[str, float]], y: List[int]):
        X = np.vstack([self._vectorize_features(d) for d in X_dicts])
        y_arr = np.array(y)
        print(f"  Label distribution: match={np.sum(y_arr==1)}, no-match={np.sum(y_arr==0)}")
        self.model.fit(X, y_arr)
        self.is_trained = True
        
    def predict(self, features_dict: Dict[str, float]) -> Dict[str, Any]:
        if not self.is_trained:
            # Fallback heuristic if not trained
            score = features_dict.get("embedding_cosine_similarity", 0.0)
            if score > 0.9: cls = "IDENTICAL"
            elif score > 0.8: cls = "NEAR_DUPLICATE"
            elif score > 0.7: cls = "FUNCTIONALLY_EQUIVALENT"
            else: cls = "DISTINCT"
            return {"classification": cls, "confidence": score, "match_probability": score}
            
        X = self._vectorize_features(features_dict)
        match_prob = float(self.model.predict_proba(X)[0][1])  # P(match)
        is_match = match_prob >= 0.5
        
        # Refine binary into 5-class using feature thresholds
        if is_match:
            cosine = features_dict.get("embedding_cosine_similarity", 0.0)
            attr_agree = features_dict.get("overall_attribute_agreement", 0.0)
            
            if cosine > 0.92 and attr_agree > 0.8:
                classification = "IDENTICAL"
            elif cosine > 0.80 and attr_agree > 0.5:
                classification = "NEAR_DUPLICATE"
            else:
                classification = "FUNCTIONALLY_EQUIVALENT"
        else:
            classification = "DISTINCT"
        
        return {
            "classification": classification,
            "confidence": match_prob if is_match else (1.0 - match_prob),
            "match_probability": match_prob,
            "probabilities": {"MATCH": match_prob, "NO_MATCH": 1.0 - match_prob}
        }

