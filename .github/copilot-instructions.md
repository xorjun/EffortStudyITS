# Project Guidelines

## Code Style

- Match the existing module layout: FastAPI route handlers live in `api/<domain>/handle_*.py`, request and response models live in `schemas.py`, and shared domain logic belongs under `api/models/` or `api/services/` instead of inside routers.
- Preserve the current async backend style and the existing Angular Material patterns on the frontend; avoid broad refactors or formatting-only churn unless the task requires it.
- When adding backend tests, follow the async pytest and `httpx.AsyncClient` style used in [api/tests/test_handle_submissions.py](../api/tests/test_handle_submissions.py).

## Architecture

- [api/main.py](../api/main.py) wires the FastAPI app, middleware, and route registration. Keep feature changes inside the owning package under `api/`.
- [api/config.py](../api/config.py) is the source of truth for environment-specific behavior, service hosts, Judge0 mode, and email enablement. Keep deployment and environment branching there.
- [frontend/its_ui](../frontend/its_ui) contains the Angular client. [docker-compose.yml](../docker-compose.yml) and [start_app.py](../start_app.py) are the main entry points for containerized and local development.
- Course and task content is data-driven under [courses](../courses); prefer updating course data or parsers over adding hardcoded feature-specific branches.

## Build and Test

- Use [README.md](../README.md) as the primary setup and deployment reference; link to it rather than copying its instructions into code or docs.
- Full stack in containers: run `docker-compose up` from the repo root after creating the required `.env` file.
- Local development: run `python start_app.py` from the repo root to start the backend and frontend together.
- Backend validation: run `pytest` from `api/`, starting with the narrowest affected test file.
- Frontend validation: run `npm start`, `npm run build`, or `npm test` from `frontend/its_ui` depending on the change.

## Conventions

- `JUDGE0_MODE` must be set to `local` or `remote`; startup fails during config loading when it is missing or invalid. Check [api/config.py](../api/config.py) before changing execution or submission flows.
- Keep environment wiring and service URLs centralized in [api/config.py](../api/config.py) and [docker-compose.yml](../docker-compose.yml); do not duplicate host or secret logic inside feature code.
- Frontend styling should follow the existing theme decisions in [frontend/THEME_DOCUMENTATION.md](../frontend/THEME_DOCUMENTATION.md) instead of introducing a separate visual system.