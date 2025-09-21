from fastapi import FastAPI
from image_service.handlers import router as image_service_router

app = FastAPI(
    title="Image Service API",
    description="REST API Gateway for gRPC Image Service",
    version="1.0.0"
)

# Include image service routes
app.include_router(image_service_router)

@app.get("/")
async def read_root():
    return {
        "message": "Image Service API Gateway",
        "version": "1.0.0",
        "endpoints": {
            "health": "/image-service/health",
            "test_image": "/image-service/test-image"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
