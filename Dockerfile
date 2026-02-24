FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency metadata first (better Docker layer caching)
COPY app/pyproject.toml app/uv.lock /app/

# Create venv + install locked deps
RUN uv sync --frozen --no-dev

# Copy the server code after deps
COPY app/server.py /app/server.py

ENV PAPER_ROOT=/data
EXPOSE 8000

# Run server directly inside uv-managed environment
CMD ["uv", "run", "python", "server.py"]
