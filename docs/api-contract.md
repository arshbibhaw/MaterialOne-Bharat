# API Contract

## Backend REST API
- `POST /api/auth/login` -> { token }
- `POST /api/upload` (multipart/form-data) -> { batchId }
- `GET /api/materials` -> { materials: [] }
- `GET /api/clusters` -> { clusters: [] }
- `POST /api/clusters/:id/approve` -> { success: true }
- `POST /api/erp-mock/push` -> { success: true }

## ML Service Internal API
- `POST /ml/ingest` -> { status: 'processing' }
- `POST /ml/match` -> { matches: [] }
- `POST /ml/cluster` -> { clusters: [] }
- `POST /ml/generate-cnmc` -> { cnmc: string }
- `GET /ml/metrics` -> { precision, recall, f1 }
