import grpc
from concurrent import futures
import sys
import os
import logging
import time
from PIL import Image
import io

from protos import image_service_pb2
from protos import image_service_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageServiceServicer(image_service_pb2_grpc.ImageServiceServicer):
    def TestImage(self, request, context):
        """Test image processing functionality."""
        try:
            logger.info(f"Received image test request with format: {request.image_format}")

            # Validate image format
            supported_formats = ['jpeg', 'jpg', 'png', 'gif', 'bmp']
            if request.image_format.lower() not in supported_formats:
                return image_service_pb2.TestImageResponse(
                    status="error",
                    message=f"Unsupported image format: {request.image_format}. Supported: {', '.join(supported_formats)}"
                )

            # Try to open and validate the image
            try:
                image_bytes = io.BytesIO(request.image_data)
                with Image.open(image_bytes) as img:
                    width, height = img.size
                    mode = img.mode
                    actual_format = img.format

                    logger.info(f"Image processed successfully: {width}x{height}, mode={mode}, format={actual_format}")

                    return image_service_pb2.TestImageResponse(
                        status="success",
                        message=f"Image processed successfully. Size: {width}x{height}, Mode: {mode}, Format: {actual_format}"
                    )

            except Exception as img_error:
                logger.error(f"Image processing error: {img_error}")
                return image_service_pb2.TestImageResponse(
                    status="error",
                    message=f"Failed to process image: {str(img_error)}"
                )

        except Exception as e:
            logger.error(f"Unexpected error in TestImage: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return image_service_pb2.TestImageResponse(
                status="error",
                message="Internal server error"
            )

    def Health(self, request, context):
        """Health check endpoint."""
        logger.info("Health check requested")
        return image_service_pb2.HealthResponse(
            status="healthy",
            message=f"Image service is running. Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )


def serve(port=50051):
    """Start the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_service_pb2_grpc.add_ImageServiceServicer_to_server(ImageServiceServicer(), server)

    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)

    logger.info(f"Starting gRPC server on {listen_addr}")
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        server.stop(grace=5)


if __name__ == '__main__':
    serve()