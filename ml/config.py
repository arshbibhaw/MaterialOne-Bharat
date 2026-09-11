import os
from pathlib import Path

# Project Roots
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ML_ROOT = PROJECT_ROOT / "ml"
DATA_ROOT = ML_ROOT / "data"

# Data Directories
RAW_DATA_DIR = DATA_ROOT / "raw"
PROCESSED_DATA_DIR = DATA_ROOT / "processed"
PAIRS_DATA_DIR = DATA_ROOT / "pairs"
SPLITS_DIR = DATA_ROOT / "splits"
REPORTS_DIR = DATA_ROOT / "reports"

# Model Artifacts
MODELS_ROOT = PROJECT_ROOT / "models"
EMBEDDINGS_MODEL_DIR = MODELS_ROOT / "embeddings"
MATCHER_MODEL_DIR = MODELS_ROOT / "matcher"
FAISS_INDEX_DIR = MODELS_ROOT / "faiss_index"
EXPORTS_DIR = PROJECT_ROOT / "exports"

# Ensure directories exist
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, PAIRS_DATA_DIR, SPLITS_DIR, REPORTS_DIR,
          EMBEDDINGS_MODEL_DIR, MATCHER_MODEL_DIR, FAISS_INDEX_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Default Datasets
TRAIN_16K_CSV = RAW_DATA_DIR / "cpse_material_master_16000_training.csv"
TEST_5K_CSV = RAW_DATA_DIR / "cpse_material_master_5500plus-2.csv"

# Model Configurations
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
FAISS_TOP_K = 20

# Feature settings
SIMILARITY_THRESHOLD = 0.65

# Runtime configuration.  These defaults keep local development simple while
# allowing deployments to move the frontend without editing source code.
FRONTEND_ORIGIN = os.getenv("MATONE_FRONTEND_ORIGIN", "http://localhost:3000")
