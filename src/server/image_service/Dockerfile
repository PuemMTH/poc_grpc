FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Create images directory for file storage with proper permissions
RUN mkdir -p images && chmod 755 images

# Expose the gRPC port
EXPOSE 50051

# Run the application
CMD ["uv", "run", "python", "main.py"]