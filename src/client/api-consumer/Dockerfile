FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock* ./
COPY . .

# Install dependencies using uv sync
RUN uv sync --frozen

# Run the application
CMD ["uv", "run", "main.py"]