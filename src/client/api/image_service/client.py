"""gRPC Client wrapper for ImageService"""

import grpc
import sys
import os
from typing import Optional

# Add protos to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'protos'))
import image_service_pb2
import image_service_pb2_grpc


class ImageServiceClient:
    """gRPC client wrapper for ImageService"""

    def __init__(self, server_address: str = None):
        if server_address is None:
            server_address = os.getenv("GRPC_SERVER_ADDRESS", "localhost:50051")
        self.server_address = server_address
        self.channel: Optional[grpc.Channel] = None
        self.stub: Optional[image_service_pb2_grpc.ImageServiceStub] = None

    def connect(self):
        """Connect to gRPC server"""
        self.channel = grpc.insecure_channel(self.server_address)
        self.stub = image_service_pb2_grpc.ImageServiceStub(self.channel)

    def disconnect(self):
        """Disconnect from gRPC server"""
        if self.channel:
            self.channel.close()
            self.channel = None
            self.stub = None

    def test_image(self, image_data: bytes, image_format: str) -> image_service_pb2.TestImageResponse:
        """Test image processing"""
        if not self.stub:
            raise RuntimeError("Client not connected. Call connect() first.")

        request = image_service_pb2.TestImageRequest(
            image_data=image_data,
            image_format=image_format
        )
        return self.stub.TestImage(request)

    def health(self) -> image_service_pb2.HealthResponse:
        """Check service health"""
        if not self.stub:
            raise RuntimeError("Client not connected. Call connect() first.")

        request = image_service_pb2.HealthRequest()
        return self.stub.Health(request)

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()