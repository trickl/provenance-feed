# GitHub instructions (repo overview + best practices)

## High-level overview

This repository contains a minimal content feed:

- `backend/`: a FastAPI service that ingests (mock) items, normalises into a canonical internal model, persists to SQLite, and exposes a read-only feed API.
- `frontend/`: a React + Vite UI that displays the feed and includes a placeholder area for a future “provenance badge”.

The design goal is **clean foundations**: explicit boundaries, simple code, and tests.

## Key principles

- The feed is a **consumer surface**, not the source of truth.
- Do **not** add trust/provenance logic here.
- Prefer **explicitness over cleverness**.
- Avoid premature optimisation and unnecessary abstraction.
- Keep boundaries clear: ingestion → domain → persistence → API.

## Coding standards

- Keep domain models stable and small.
- Avoid leaking persistence concerns (SQL, schemas) into the API layer.
- Prefer pure functions for normalisation.
- Keep dependencies minimal and boring.

## Testing expectations

- Unit tests should cover:
  - stable content identifiers
  - normalisation behaviour
  - repository persistence + ordering
  - API contract for `/api/feed`

## Pull request checklist

- [ ] Tests added/updated
- [ ] Linting passes
- [ ] No provenance/trust logic introduced
- [ ] README updated if behaviour/config changes
