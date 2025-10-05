FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock* ./
COPY . .

# Install dependencies using uv sync
RUN uv sync --frozen

# Create directory for processed samples
RUN mkdir -p processed_samples

# Expose gRPC port
EXPOSE 50052

# Set environment variable
ENV SAMPLE_SERVICE_PORT=50052

# Run the application
CMD ["uv", "run", "main.py"]