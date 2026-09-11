# MatOne

Material-code identity resolution and governance workflow.

## Local setup

Create a Python 3.11+ virtual environment, install `requirements.txt`, then start the API with:

```powershell
python -m uvicorn ml.api.main:app --reload
```

For the frontend, copy `frontend/.env.example` to `frontend/.env.local`, install dependencies in `frontend`, and run `npm run dev`.

## Configuration

- `MATONE_FRONTEND_ORIGIN` sets the backend CORS origin.
- `NEXT_PUBLIC_API_BASE_URL` sets the frontend API origin.

The recommendation endpoint requires local model artifacts and the configured training CSV.
