import re
import yaml
import unicodedata
from pathlib import Path

# Load abbreviations
ABBREVIATIONS_PATH = Path(__file__).parent / "abbreviations.yaml"
with open(ABBREVIATIONS_PATH, "r") as f:
    RAW_ABBREVS = yaml.safe_load(f)

# Flatten abbreviations into a single dict for fast lookup
ABBREV_MAP = {}
for category, abbrevs in RAW_ABBREVS.items():
    if isinstance(abbrevs, dict):
        for k, v in abbrevs.items():
            ABBREV_MAP[k.lower()] = v.lower()

def normalize_text(text: str) -> str:
    """
    Core normalization pipeline for material descriptions.
    """
    if not isinstance(text, str):
        return ""
        
    # 1. Unicode normalization (NFKD to separate characters and diacritics)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    
    # 2. Lowercase
    text = text.lower()
    
    # 3. Punctuation normalization
    # Replace common separators with spaces
    text = re.sub(r'[_\-\.,;:/\|]', ' ', text)
    # Ensure space around dimensions "x" or "X"
    text = re.sub(r'(\d)\s*x\s*(\d)', r'\1 x \2', text)
    
    # 4. Whitespace collapse
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 5. Abbreviation expansion
    tokens = text.split()
    expanded_tokens = [ABBREV_MAP.get(token, token) for token in tokens]
    text = ' '.join(expanded_tokens)
    
    # 6. Numeric/Unit normalization (basic string level)
    # e.g. "4 inch" -> "4 in", "4mm" -> "4 mm"
    text = re.sub(r"(\d+)\s*(inch|in|\")\b", r"\1 in", text)
    text = re.sub(r"(\d+)(mm|cm|m)\b", r"\1 \2", text)
    
    return text

if __name__ == "__main__":
    # Test cases
    test_cases = [
        "M8 BOLT ZP 40MM",
        "HEX BOLT M8X40 ZINC",
        "PIPE ASTM A106 GR.B 4 IN SCH40",
        "GLOBE VALVE SS316 8\" CL 300 API 6D"
    ]
    for case in test_cases:
        print(f"Original: {case}")
        print(f"Normalized: {normalize_text(case)}\n")
