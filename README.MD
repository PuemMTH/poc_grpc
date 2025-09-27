# gRPC Image Service POC

Proof of Concept project for gRPC Image Service with REST API Gateway

## Project Structure

```mermaid
graph TB
    subgraph "Client Layer"
        CLI[CLI Client<br/>src/client/cli]
        API[API Gateway<br/>src/client/api<br/>FastAPI + REST]
    end

    subgraph "Server Layer"
        GRPC[gRPC Server<br/>src/server/image_service<br/>Image Processing]
    end

    subgraph "Protocol"
        PROTO[Protocol Buffers<br/>src/protos<br/>*.proto files]
    end

    subgraph "Tools"
        TOOLS[Code Generation<br/>src/tools<br/>protobuf generators]
    end

    CLI -->|gRPC| GRPC
    API -->|gRPC| GRPC
    PROTO --> TOOLS
    TOOLS --> CLI
    TOOLS --> API
    TOOLS --> GRPC
```

## Architecture

```mermaid
sequenceDiagram
    participant User
    participant API as API Gateway<br/>(FastAPI)
    participant gRPC as gRPC Server<br/>(Image Service)
    participant Storage as File Storage

    User->>API: POST /image-service/test-image
    API->>gRPC: TestImage(image_data, format)
    gRPC->>gRPC: Process & Validate Image
    gRPC->>Storage: Save to images/YYYY/MM/DD/
    Storage-->>gRPC: File saved
    gRPC-->>API: TestImageResponse
    API-->>User: JSON Response
```

## Docker Architecture

```mermaid
graph LR
    subgraph "Docker Compose"
        subgraph "api-service container"
            FASTAPI[FastAPI Server<br/>Port 8000]
        end

        subgraph "image-service container"
            GRPCSERV[gRPC Server<br/>Port 50051]
        end

        subgraph "Host"
            STORAGE[File Storage<br/>./images volume]
        end
    end

    FASTAPI -->|GRPC_SERVER_ADDRESS<br/>image-service:50051| GRPCSERV
    GRPCSERV --> STORAGE

    User -->|HTTP :8000| FASTAPI
```

## Usage

### Prerequisites
- Python 3.12+
- uv (Python package manager)
- Docker & Docker Compose

### Quick Start

```bash
# 1. Install dependencies
make install

# 2. Generate protobuf files
make generate-proto

# 3. Run with Docker (recommended)
make monitor

# 4. Test the API
curl http://localhost:8000/image-service/health
```

### Available Commands

```bash
make help                 # Show available commands
make install             # Install all dependencies
make generate-proto      # Generate Python files from proto
make run-server          # Run gRPC server locally
make run-client          # Run CLI client
make run-client-api      # Run API Gateway locally
make monitor             # Start Docker services with logs
make clean               # Clean generated files
```

## API Endpoints

### REST API (Port 8000)

- `GET /` - API information
- `GET /image-service/health` - Health check
- `POST /image-service/test-image` - Upload and process image

### gRPC Service (Port 50051)

- `Health()` - Service health check
- `TestImage(image_data, image_format)` - Process image

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GRPC_SERVER_ADDRESS` | `localhost:50051` | gRPC server address for API Gateway |

## Development

### Local Development
```bash
# Terminal 1: Run gRPC server
make run-server

# Terminal 2: Run API Gateway
make run-client-api
```

### Docker Development
```bash
# Start all services
make monitor

# Stop services
cd src/server && docker-compose down
```