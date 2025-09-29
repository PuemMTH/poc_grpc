import grpc
from concurrent import futures
import sys
import os
import logging
import time
import uuid
from datetime import datetime
from rich.console import Console
print = Console().print

# Add the image_service directory to Python path to import generated protobuf files
sys.path.append(os.path.join(os.path.dirname(__file__), 'protos'))

import sample_service_pb2
import sample_service_pb2_grpc

class SampleServiceServicer(sample_service_pb2_grpc.SampleServiceServicer):
    def __init__(self):
        # In-memory storage for demonstration (in production, use a database)
        self.processing_jobs = {}

    def ProcessSample(self, request, context):
        """Process sample data from api-consumer."""
        try:
            print(f"Received sample processing request:")
            print(f"  Image UUID: {request.image_uuid}")
            print(f"  Image Path: {request.image_path}")
            print(f"  Metadata: {dict(request.metadata)}")

            # Generate a unique process ID
            process_id = str(uuid.uuid4())
            timestamp = int(time.time())

            # Validate input
            if not request.image_uuid or not request.image_path:
                return sample_service_pb2.ProcessSampleResponse(
                    status="error",
                    message="Both image_uuid and image_path are required",
                    process_id=process_id,
                    timestamp=timestamp
                )

            # Check if image path exists (simulate processing)
            if not os.path.exists(request.image_path):
                print(f"Warning: Image path does not exist: {request.image_path}")
                # Continue processing anyway for demonstration

            # Store processing job info
            self.processing_jobs[process_id] = {
                'image_uuid': request.image_uuid,
                'image_path': request.image_path,
                'metadata': dict(request.metadata),
                'status': 'processing',
                'created_at': timestamp,
                'completed_at': None,
                'result_path': None
            }

            # Simulate some processing time
            import random
            processing_success = random.choice([True, True, True, False])  # 75% success rate

            if processing_success:
                # Simulate successful processing
                result_dir = f"processed_samples/{datetime.fromtimestamp(timestamp).strftime('%Y/%m/%d')}"
                os.makedirs(result_dir, exist_ok=True)
                result_path = os.path.join(result_dir, f"{request.image_uuid}_processed.json")

                # Create a dummy result file
                with open(result_path, 'w') as f:
                    import json
                    result_data = {
                        'original_uuid': request.image_uuid,
                        'original_path': request.image_path,
                        'processed_at': timestamp,
                        'metadata': dict(request.metadata),
                        'processing_result': 'Sample processing completed successfully'
                    }
                    json.dump(result_data, f, indent=2)

                # Update job status
                self.processing_jobs[process_id].update({
                    'status': 'completed',
                    'completed_at': int(time.time()),
                    'result_path': result_path
                })

                print(f"✅ Sample processing completed successfully. Result saved to: {result_path}")

                return sample_service_pb2.ProcessSampleResponse(
                    status="success",
                    message=f"Sample processing completed. Result available at: {result_path}",
                    process_id=process_id,
                    timestamp=timestamp
                )
            else:
                # Simulate processing failure
                self.processing_jobs[process_id].update({
                    'status': 'failed',
                    'completed_at': int(time.time())
                })

                print(f"❌ Sample processing failed for UUID: {request.image_uuid}")

                return sample_service_pb2.ProcessSampleResponse(
                    status="error",
                    message="Sample processing failed due to internal error",
                    process_id=process_id,
                    timestamp=timestamp
                )

        except Exception as e:
            print(f"Unexpected error in ProcessSample: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return sample_service_pb2.ProcessSampleResponse(
                status="error",
                message="Internal server error",
                process_id=str(uuid.uuid4()),
                timestamp=int(time.time())
            )

    def GetSampleStatus(self, request, context):
        """Get the status of a sample processing job."""
        try:
            print(f"Status request for process ID: {request.process_id}")

            if not request.process_id:
                return sample_service_pb2.SampleStatusResponse(
                    status="error",
                    message="Process ID is required"
                )

            job = self.processing_jobs.get(request.process_id)
            if not job:
                return sample_service_pb2.SampleStatusResponse(
                    status="not_found",
                    message=f"No job found with process ID: {request.process_id}"
                )

            print(f"Found job: {job['status']}")

            return sample_service_pb2.SampleStatusResponse(
                status=job['status'],
                message=f"Job {job['status']}",
                image_uuid=job['image_uuid'],
                result_path=job.get('result_path', ''),
                created_at=job['created_at'],
                completed_at=job.get('completed_at', 0)
            )

        except Exception as e:
            print(f"Unexpected error in GetSampleStatus: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return sample_service_pb2.SampleStatusResponse(
                status="error",
                message="Internal server error"
            )

    def Health(self, request, context):
        """Health check endpoint."""
        print("Health check requested for SampleService")
        return sample_service_pb2.HealthResponse(
            status="healthy",
            message=f"Sample service is running. Time: {time.strftime('%Y-%m-%d %H:%M:%S')}. Active jobs: {len(self.processing_jobs)}"
        )


def serve(port: int):
    """Start the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sample_service_pb2_grpc.add_SampleServiceServicer_to_server(SampleServiceServicer(), server)

    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)

    print(f"🚀 Starting Sample Service gRPC server on {listen_addr}")
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Server interrupted by user")
        server.stop(grace=5)


if __name__ == '__main__':
    import os
    port = int(os.getenv('SAMPLE_SERVICE_PORT'))
    if not port:
        print("❌ SAMPLE_SERVICE_PORT environment variable is not set.")
        exit(1)
    serve(port=port)