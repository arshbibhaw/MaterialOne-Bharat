# Unified Material Master

Unified Material Master is an AI-driven system designed to standardize and harmonize material codes across Central Public Sector Enterprises (CPSEs). It tackles the problem of heterogeneous ERP data (different naming conventions, abbreviations, units) by using machine learning for deduplication and generating a Common National Material Code (CNMC).

This monorepo contains the complete implementation across a Next.js App Router frontend, a Node.js/Express backend, and a Python FastAPI ML service, all backed by MongoDB. The system relies entirely on free/open-source tools (e.g., sentence-transformers, scikit-learn, spaCy) and requires zero paid APIs.

### Capabilities Implemented (MVP)
- [x] AI matching
- [x] Standardization / classification
- [x] Duplicate detection
- [x] CNMC generation
- [x] CPSE code mapping/migration
- [x] Dashboard / analytics
- [x] Audit trail / governance
- [x] SAP / ERP integration (Mock)

### Setup Instructions
1. Ensure Docker and Docker Compose are installed.
2. Clone this repository.
3. Run `docker-compose up --build` at the root.
4. Access Frontend at `http://localhost:3000`
5. Access Backend API at `http://localhost:3001`
6. Access ML Service at `http://localhost:8000`
