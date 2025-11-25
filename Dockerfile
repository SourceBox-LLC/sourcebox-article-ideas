FROM python:3.11-slim

# Install curl to fetch uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --yes
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Copy dependency metadata first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (respecting uv.lock)
RUN uv sync --frozen --no-dev

# Copy the rest of the application code
COPY . .

# Default command: run the script via uv
CMD ["uv", "run", "scheduler.py"]
