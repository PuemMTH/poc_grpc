# Sample Service

gRPC service for processing sample data from api-consumer.

## Usage

```bash
# Run the service
uv run main.py

# Run on custom port
uv run main.py --port 50053
```

## API

- `ProcessSample`: Process sample data with image_uuid and image_path
- `GetSampleStatus`: Get processing status by process_id
- `Health`: Health check endpoint