"""FastAPI route handlers for ImageService"""

import os
from fastapi import APIRouter, HTTPException, File, UploadFile
from .client import ImageServiceClient
from .models import TestImageResponse, HealthResponse, ErrorResponse
import grpc

router = APIRouter(prefix="/image-service", tags=["Image Service"])

# กำหนด gRPC server address จาก environment variable
GRPC_SERVER = os.getenv("GRPC_SERVER_ADDRESS", "localhost:50051")


@router.post("/test-image", response_model=TestImageResponse)
async def test_image(
    file: UploadFile = File(...)
):
    """Test image processing via gRPC"""
    try:
        image_data = await file.read()
        image_format = file.content_type.split("/")[1]

        # เชื่อมต่อกับ gRPC server
        with ImageServiceClient(GRPC_SERVER) as client:
            response = client.test_image(image_data, image_format)

        return TestImageResponse(
            status=response.status,
            message=response.message
        )

    except grpc.RpcError as e:
        raise HTTPException(
            status_code=503,
            detail=f"gRPC service unavailable: {e.details()}"
        )

    except grpc.RpcError as e:
        raise HTTPException(
            status_code=503,
            detail=f"gRPC service unavailable: {e.details()}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health():
    """Check service health via gRPC"""
    try:
        # เชื่อมต่อกับ gRPC server
        with ImageServiceClient(GRPC_SERVER) as client:
            response = client.health()

        return HealthResponse(
            status=response.status,
            message=response.message
        )

    except grpc.RpcError as e:
        raise HTTPException(
            status_code=503,
            detail=f"gRPC service unavailable: {e.details()}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )