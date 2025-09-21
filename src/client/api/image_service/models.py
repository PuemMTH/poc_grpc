"""Pydantic models for API requests and responses"""

from pydantic import BaseModel
from typing import Optional


class TestImageRequest(BaseModel):
    """Request model for test image endpoint"""
    image_format: str
    # Note: image_data will be handled as file upload in FastAPI


class TestImageResponse(BaseModel):
    """Response model for test image endpoint"""
    status: str
    message: str


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    message: str


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None