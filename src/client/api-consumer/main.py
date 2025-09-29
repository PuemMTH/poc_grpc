import os, pika, time
import random
import sys
import grpc
from rich import print

# Add the server directory to Python path to import generated protobuf files
sys.path.append(os.path.join(os.path.dirname(__file__), 'protos'))

import sample_service_pb2
import sample_service_pb2_grpc

def process_via_grpc(image_uuid, image_path, metadata=None):
    """Process sample data via gRPC sample_service."""
    grpc_server_address = os.environ.get('SAMPLE_SERVICE_ADDRESS', 'localhost:50052')

    try:
        with grpc.insecure_channel(grpc_server_address) as channel:
            stub = sample_service_pb2_grpc.SampleServiceStub(channel)

            # Create request
            request = sample_service_pb2.ProcessSampleRequest(
                image_uuid=image_uuid,
                image_path=image_path,
                metadata=metadata or {}
            )

            print(f"📡 Sending gRPC request to {grpc_server_address}")
            print(f"   Image UUID: {image_uuid}")
            print(f"   Image Path: {image_path}")

            # Call the service
            response = stub.ProcessSample(request)

            print(f"📨 gRPC Response:")
            print(f"   Status: {response.status}")
            print(f"   Message: {response.message}")
            print(f"   Process ID: {response.process_id}")

            return response.status == "success", response

    except grpc.RpcError as e:
        print(f"[red]❌ gRPC Error: {e.code()} - {e.details()}[/red]")
        return False, None
    except Exception as e:
        print(f"[red]❌ Unexpected error: {str(e)}[/red]")
        return False, None

def on_request(ch, method, properties, body: bytes):
    job_data = body.decode()
    job_data = eval(job_data)  # Convert string representation of dict back to dict
    print(f"[reset][yellow][~] Received job: {str(job_data['image_uuid'])} \n[reset][yellow][~] Path: {str(job_data['image_path'])}")

    # Process via gRPC instead of random simulation
    success, response = process_via_grpc(
        image_uuid=job_data['image_uuid'],
        image_path=job_data['image_path'],
        metadata={'source': 'rabbitmq', 'consumer': 'api-consumer'}
    )

    if success:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("[green][✓] Job processed successfully via gRPC[/green]")
    else:
        ch.basic_nack(delivery_tag=method.delivery_tag)
        print("[red][✗] Job processing failed via gRPC[/red]")

def test_grpc_connection():
    """Test connection to sample_service."""
    grpc_server_address = os.environ.get('SAMPLE_SERVICE_ADDRESS', 'localhost:50052')

    try:
        with grpc.insecure_channel(grpc_server_address) as channel:
            stub = sample_service_pb2_grpc.SampleServiceStub(channel)

            # Test health check
            health_request = sample_service_pb2.HealthRequest()
            health_response = stub.Health(health_request)

            print(f"[green]✅ gRPC Health Check: {health_response.status}[/green]")
            print(f"   Message: {health_response.message}")
            return True

    except grpc.RpcError as e:
        print(f"[red]❌ gRPC Health Check Failed: {e.code()} - {e.details()}[/red]")
        return False
    except Exception as e:
        print(f"[red]❌ gRPC Connection Error: {str(e)}[/red]")
        return False

if __name__ == "__main__":
    print("🚀 Starting API Consumer with gRPC integration")

    # Test gRPC connection first
    grpc_server_address = os.environ.get('SAMPLE_SERVICE_ADDRESS', 'localhost:50052')
    print(f"📡 Testing connection to Sample Service at {grpc_server_address}")

    if not test_grpc_connection():
        print("[red]❌ Failed to connect to Sample Service. Please ensure it's running.[/red]")
        print(f"[yellow]💡 Start the service with: cd src/server/sample_service && uv run main.py[/yellow]")
        sys.exit(1)

    # Setup RabbitMQ (existing code)
    # export RABBITMQ_HOST=localhost RABBITMQ_PORT=5672 RABBITMQ_QUEUE=image_queue CLOUDAMQP_URL='amqp://guest:guest@localhost:5672/%2f' SAMPLE_SERVICE_ADDRESS='localhost:50052' && uv run main.py
    url = os.environ.get('CLOUDAMQP_URL')
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=os.environ.get('RABBITMQ_QUEUE'), durable=False) # Declare the queue if it doesn't exist
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=os.environ.get('RABBITMQ_QUEUE'), on_message_callback=on_request)
    print(" [>>] Awaiting RPC requests (will process via gRPC)")
    channel.start_consuming()