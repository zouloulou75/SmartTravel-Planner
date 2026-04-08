# Travel ML Project

End-to-end travel application with:
- FastAPI backend
- React/Vite dashboard frontend
- PostgreSQL persistence
- pgAdmin administration UI
- MLflow experiment tracking
- Random Forest POI recommendation
- Groq-backed itinerary generation

## Stack

- Backend: FastAPI, SQLAlchemy, pandas, scikit-learn, category-encoders
- Frontend: React 19, Vite
- Database: PostgreSQL
- Admin UI: pgAdmin
- Experiment Tracking: MLflow
- Containers: Docker Compose

## Dataset Layout

- `dataset/interaction_5.csv`: large POI interaction dataset used for model training
- `../projet ml/train.xls`
- `../projet ml/validation.xls`
- `../projet ml/test.xls`

The `*.xls` trip files are CSV-formatted and are imported into PostgreSQL by the bootstrap service.

## Environment

Copy `.env.example` to `.env` and set at least:

```bash
cp .env.example .env
```

Important variables:
- `DATABASE_URL`
- `GROQ_API_KEY`
- `MLFLOW_TRACKING_URI`
- `MLFLOW_BACKEND_STORE_URI`
- `MLFLOW_EXPERIMENT_NAME`
- `MLFLOW_REGISTERED_MODEL_NAME`
- `INTERACTION_DATA_PATH`
- `TRIP_DATA_DIR`
- `MODEL_ARTIFACT_PATH`

## Run With Docker

```bash
docker compose up --build
```

Available services:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000/api/v1/health`
- pgAdmin: `http://localhost:5050`
- MLflow UI: `http://localhost:5001`

The `bootstrap` service imports the trip datasets, trains the recommender once, stores the model artifact in a named Docker volume, logs the training run to MLflow, and registers the trained model in the MLflow Model Registry.

## Local Backend

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Local Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `GET /api/v1/health`
- `POST /api/v1/recommendations/pois`
- `POST /api/v1/trips/plan`
- `POST /api/v1/pipeline/plan`
- `GET /api/v1/metrics/summary`
- `POST /api/v1/evaluations/run`

## Notes

- POI recommendations use numeric `poi_id` values because no POI metadata lookup file is present.
- The UI displays the dominant inferred region for each recommended `poi_id` to keep recommendations readable.
- Trip generation accepts arbitrary destinations and uses dataset examples for few-shot guidance.
- The large interaction dataset stays file-based; only derived stats, model artifacts, and run history are persisted.
- MLflow stores run metadata in a dedicated PostgreSQL database on the same server (`mlflow_tracking` by default) and artifacts in the `mlflow_artifacts` Docker volume.
- The MLflow tracking database should use a `postgresql+psycopg2://...` URI to avoid driver issues with experiment ID lookups.
- Successful training runs automatically create or update a registered model (`poi_recommender` by default) and maintain `candidate` and `champion` aliases based on the logged `accuracy`.
