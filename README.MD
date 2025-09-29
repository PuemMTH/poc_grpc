# gRPC Image Service POC

## Quick Run Commands
```bash
# gRPC Server (port 50052)
export SAMPLE_SERVICE_PORT=50052 && cd src/server/sample_service/ && uv run main.py

# API Consumer
export RABBITMQ_HOST=localhost RABBITMQ_PORT=5672 RABBITMQ_QUEUE=image_queue CLOUDAMQP_URL='amqp://guest:guest@localhost:5672/%2f' SAMPLE_SERVICE_ADDRESS='localhost:50052' && cd src/client/api-consumer && uv run main.py

# API Producer (port 8000)
export REDIS_HOST=localhost REDIS_PORT=6379 CLOUDAMQP_URL='amqp://guest:guest@localhost:5672/%2f' && cd src/client/api-producer && uv run main.py
```

## Project Structure

```mermaid
graph TB
    subgraph "Client Layer"
        PRODUCER[API Producer<br/>src/client/api-producer<br/>Redis + RabbitMQ]
        CONSUMER[API Consumer<br/>src/client/api-consumer<br/>RabbitMQ + gRPC]
    end

    subgraph "Server Layer"
        GRPC[gRPC Server<br/>src/server/sample_service<br/>Sample Service]
    end

    subgraph "Message Queue"
        REDIS[Redis<br/>Task Queue]
        RABBITMQ[RabbitMQ<br/>Message Broker]
    end

    subgraph "Protocol"
        PROTO[Protocol Buffers<br/>src/protos<br/>sample_service.proto]
    end

    subgraph "Tools"
        TOOLS[Code Generation<br/>src/tools<br/>protobuf generators]
    end

    PRODUCER -->|Publish| REDIS
    PRODUCER -->|Publish| RABBITMQ
    CONSUMER -->|Subscribe| RABBITMQ
    CONSUMER -->|gRPC| GRPC
    PROTO --> TOOLS
    TOOLS --> CONSUMER
    TOOLS --> GRPC
```

## Architecture

```mermaid
sequenceDiagram
    participant User
    participant Producer as API Producer<br/>(Port 8000)
    participant Redis as Redis Queue
    participant RabbitMQ as RabbitMQ Broker
    participant Consumer as API Consumer
    participant gRPC as gRPC Server<br/>(Sample Service)

    User->>Producer: HTTP Request
    Producer->>Redis: Publish Task
    Producer->>RabbitMQ: Publish Message
    Producer-->>User: Task Queued Response

    Consumer->>RabbitMQ: Subscribe/Consume
    RabbitMQ-->>Consumer: Message Received
    Consumer->>gRPC: Process Request
    gRPC-->>Consumer: Response
    Consumer->>Consumer: Handle Result
```
