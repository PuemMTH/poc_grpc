# gRPC Image Service POC

## Overview
```mermaid
graph TB
    Client[Client/User<br/>HTTP/REST<br/>Port: 8000] -->|POST /process<br/>JSON Payload| Producer[API Producer<br/>FastAPI + Uvicorn<br/>python:3.12-slim]

    Producer -->|SET task_id:result<br/>redis-py| Redis[(Redis 7.0<br/>Port: 6379<br/>In-Memory Cache)]
    Producer -->|PUBLISH exchange:image_queue<br/>pika/AMQP 0-9-1| RabbitMQ[RabbitMQ 3.13<br/>Port: 5672 AMQP<br/>Port: 15672 Management<br/>Message Broker]

    RabbitMQ -->|CONSUME queue:image_queue<br/>Basic.Consume| Consumer[API Consumer<br/>Python Consumer<br/>pika + grpcio]

    Consumer -->|UnaryCall: ProcessSample<br/>HTTP/2 + Protobuf<br/>gRPC Channel| LB{Docker Internal DNS<br/>sample-service<br/>Client-Side LB}

    LB -->|Round Robin<br/>gRPC Stream| SS1[Sample Service 1<br/>Python gRPC Server<br/>Port: 50052<br/>Replica 1/3]
    LB -->|Round Robin<br/>gRPC Stream| SS2[Sample Service 2<br/>Python gRPC Server<br/>Port: 50052<br/>Replica 2/3]
    LB -->|Round Robin<br/>gRPC Stream| SS3[Sample Service 3<br/>Python gRPC Server<br/>Port: 50052<br/>Replica 3/3]

    SS1 -.->|Write Binary<br/>File I/O| Vol[/Docker Volume<br/>./processed_samples<br/>Persistent Storage/]
    SS2 -.->|Write Binary<br/>File I/O| Vol
    SS3 -.->|Write Binary<br/>File I/O| Vol
```

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
