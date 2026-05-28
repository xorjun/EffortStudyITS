# Standalone Docker image — backend + pre-built frontend in one container.
#
# Build:
#   docker build -t effortstudy-its .
#
# Run (with external MongoDB):
#   docker run -d -p 8080:8000 \
#     -e ITS_ENV=standalone \
#     -e DATABASE_HOST=host.docker.internal \
#     -e DB_SERVICE_PW=yourpassword \
#     -e JWT_SECRET=changeme \
#     -e USER_VERIFICATION_SECRET=changeme \
#     -e RESET_PWD_SECRET=changeme \
#     effortstudy-its
#
# Or use docker-compose.standalone.yml for a one-command MongoDB + app setup.

# ── Stage 1: Build Angular frontend ──────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/its_ui/package.json frontend/its_ui/package-lock.json ./
RUN npm ci
COPY frontend/its_ui/ ./
RUN npm run build -- --configuration production

# ── Stage 2: Final image ─────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy backend dependency files for layer caching
COPY api/pyproject.toml api/uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy backend source
COPY api/ ./
RUN uv sync --frozen

# Copy pre-built frontend
COPY --from=frontend-build /app/dist/its_ui /app/static

# Copy course content
COPY courses/ /app/courses/

ENV PATH="/app/.venv/bin:$PATH"
ENV STATIC_DIR=/app/static
ENV ITS_ENV=standalone

EXPOSE 8000
CMD ["python", "main.py"]
