# Phase 10: Operations Runbook

## 1. System Health & Observability
- **Health Check Endpoint**: Hit `GET /health` to verify that the FastAPI server is running.
- **Audit Logs**: Review `backend/app/refusal_audit.log` weekly to analyze which queries are frequently triggering refusal flows. Adjust the query classifier taxonomy if valid factual questions are being falsely refused.

## 2. Ingestion & Freshness Scheduling
- The ingestion pipeline is triggered by sending a request to `POST /ingest/run` or executing the `ingest.py` script.
- **GitHub Actions Integration**: Set up a `.github/workflows/ingest.yml` cron job to hit the `POST /ingest/run` endpoint (or execute the script directly) on a daily basis to meet the data freshness SLO.

## 3. Vector Store Maintenance
- The Chroma DB is stored locally in `backend/chroma_db/`.
- If the embeddings become stale or corrupted, delete the `chroma_db` folder and run `POST /ingest/run` to perform a full weekly re-index.

## 4. Incident Response
- **Symptom**: Fast LLM timeout or Groq API key failure.
  - **Action**: Verify `GROQ_API_KEY` is set correctly. The API uses a safe fallback if generation fails.
- **Symptom**: Missing data for an approved scheme.
  - **Action**: Verify the scheme's URL inside `backend/data/registry/source_registry.json`. Re-run ingestion.
