# provenance-feed

A minimal, production-quality **news/content feed**.

This repository intentionally treats the feed as a **consumer surface**:
it ingests content from placeholder/mocked sources, normalises it into a canonical internal model, persists it, and serves it via a read-only API and a small UI.

## What this is

- A **backend API** that:
  - ingests content (currently from mocked/placeholder sources)
  - normalises items into a canonical internal model
  - persists items locally (SQLite)
  - serves a **read-only** feed API
- A **frontend UI** that:
  - displays a chronological feed
  - shows title/source/timestamp clearly
  - reserves UI space for a future **“provenance badge”**

## What this intentionally does *not* do

- No authentication/authorisation
- No scoring, ranking, or trust logic
- No provenance verification or algorithms
- No attempts to be the source of truth

## Repository layout

- `backend/` — FastAPI service (ingestion/domain/persistence/api layers)
- `frontend/` — React + Vite UI
- `.github/` — contributor instructions + CI

## Local development

### Backend

1) Create a virtualenv and install deps:

- Create/activate your venv however you prefer.
- Install the backend in editable mode:
  - `cd backend`
  - `python -m pip install -e ".[dev]"`

2) (Optional) Ingest mock items once:

- `cd backend`
- `python -m provenance_feed.ingestion.run`

3) Run the API server:

- `cd backend`
- `uvicorn provenance_feed.main:app --reload`

The backend reads configuration from environment variables. For local dev, copy `.env.example` to `.env` in the repo root (or set env vars in your shell).

Stable content identifiers are of the form:

- `content_id = "{source}:{source_item_id}"`

This value is intended to be used later when querying an external provenance system.

Real-world feeds are often messy: if a source does not provide a stable `source_item_id`, the intended escape hatch (not implemented yet) is to derive one by hashing a **canonicalised source URL** (e.g., normalised scheme/host/path and a consistent query policy) and using that hash as the `source_item_id`.

### Current ingestion sources (intentionally incomplete)

This project intentionally ingests from a **small curated set** of sources (3–5 max). Coverage is deliberately incomplete; the goal is to validate the architecture under real data, not to ingest “everything”.

Sources are intentionally **heterogeneous** (mainstream outlets, public media, a science/government publisher, plus some sources with thinner/indirect provenance such as think-tank posts, advocacy updates, and aggregation). Inclusion here is about epistemic stress-testing ingestion and presentation.

**Inclusion ≠ endorsement.** The feed treats all sources identically and does not label sources as “good” or “bad”, and it does not implement trust logic.

Currently ingested RSS sources:

- BBC News (World) — stable, mainstream international reporting
- NPR (News) — reputable public media, different editorial profile
- The Guardian (World) — another major outlet with heterogeneous feed shape
- NASA (Breaking News) — reputable non-outlet source (science/government) to increase heterogeneity

Additional legitimate-but-thinner-provenance sources (still treated identically by the feed):

- Brookings (Research/Commentary) — think-tank commentary and research posts
- EFF (Updates) — advocacy/NGO updates
- ReliefWeb (Updates) — aggregation across many upstream publishers

### Content identifiers with real RSS feeds

For the current RSS sources, `source_item_id` is derived from a **hash of a best-effort canonicalised URL**, so that:

- duplicates caused by tracking query parameters collapse to one item
- title updates overwrite the existing record (via upsert)

Known limitations (documented on purpose):

- TODO: URL canonicalisation is source- and site-specific; a general rule may still produce duplicates.
- TODO: if publishers change canonical URLs over time, the derived ID changes and the item may appear as “new”.

Backend endpoints:

- `GET /healthz`
- `GET /api/feed`

The database defaults to SQLite at `backend/data/feed.db`.
For convenience, the backend can auto-ingest mocked items on startup.

### Frontend

The frontend expects the backend running at `VITE_API_BASE_URL` (default `http://localhost:8000`).

1) Install and run:

- `cd frontend`
- `npm install`
- `npm run dev`

2) Configure environment (optional):

- Copy `frontend/.env.example` → `frontend/.env` and adjust values.

The “provenance badge” is a placeholder UI element that links to an external URL base (`VITE_PROVENANCE_URL_BASE`), but does not implement provenance logic.

## CI

CI runs:

- Backend lint + tests
- Frontend typecheck + build
