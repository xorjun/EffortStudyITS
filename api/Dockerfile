FROM python:3.11

WORKDIR /app

# Install uv for fast, reproducible dependency installs
RUN pip install uv

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1
# Use copy mode for Docker (avoid hardlinks across layers)
ENV UV_LINK_MODE=copy

# Copy dependency files first for Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual env (cached layer)
RUN uv sync --frozen --no-install-project

# Copy application source
COPY . /app/

# Install the project itself
RUN uv sync --frozen

# Put the venv Python on PATH so compose's "python main.py" picks it up
ENV PATH="/app/.venv/bin:$PATH"
