from fastapi import APIRouter, HTTPException, File, UploadFile
import redis, os, json, uuid, time
from pathlib import Path
from rich.console import Console
from .WorkerQueueClient import WorkerQueueClient

print = Console().print

print(f"""
[bold green]Image Service[/bold green]
[bold blue]Redis Host:[/bold blue] [red]{os.getenv("REDIS_HOST")}[reset]
[bold blue]Redis Port:[/bold blue] [red]{os.getenv("REDIS_PORT")}[reset]
[bold blue]Redis DB:[/bold blue] [red]{os.getenv("REDIS_DB", 0)}[reset]
[bold blue]CloudAMQP URL:[/bold blue] [red]{os.getenv("CLOUDAMQP_URL")}[reset]
""")
# export REDIS_HOST=localhost REDIS_PORT=6379 CLOUDAMQP_URL='amqp://guest:guest@localhost:5672/%2f' && uv run main.py
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=int(os.getenv("REDIS_DB", 0))
)
router = APIRouter(prefix="/image-service", tags=["Image Service"])

@router.post("/test-image")
async def test_image(
    file: UploadFile = File(...)
):
    try:
        print(f"[yellow]Creating Worker Queue Client with CLOUDAMQP_URL: {os.environ.get('CLOUDAMQP_URL')}[/yellow]")
        worker_client = WorkerQueueClient('image_queue')
        print("[green]Worker Queue Client created successfully[/green]")

        # Generate unique filename
        image_uuid = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix if file.filename else '.jpg'
        filename = f"{image_uuid}{file_extension}"

        # Create uploads directory if not exists
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)

        # Save file locally
        date_path = time.strftime("%Y/%m/%d")
        upload_dir = upload_dir / date_path
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / filename
        file_content = await file.read()
        with open(file_path, "wb") as f:
            f.write(file_content)

        print(f"[blue]File saved to: {file_path}[/blue]")

        # Prepare message with file path and UUID
        message = {
            "image_path": str(file_path.absolute()),
            "image_uuid": image_uuid
        }

        # Send message to worker queue
        worker_client.send_task(json.dumps(message))
        worker_client.close()
        
        redis_client.hset("image_tasks", image_uuid, json.dumps({
            "status": "queued",
            "path": str(file_path.absolute()),
            "timestamp": int(time.time())
        }))

        return {
            "status": "ok",
            "message": "Task sent to worker queue successfully",
            "queue": "image_queue",
            "image_uuid": image_uuid,
            "image_path": str(file_path.absolute()),
            "file_size": len(file_content)
        }
    except Exception as e:
        print(f"[red]Error in test_image: {type(e).__name__}: {str(e)}[/red]")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    try:
        redis_client.ping()
        return {
            "status": "ok",
            "redis": "connected",
            "message": {
                "store_keys": redis_client.dbsize(),
                "memory_usage": f"{redis_client.info(section='memory')['used_memory_human']}/{redis_client.info(section='memory')['maxmemory_human']}"
            }
        }
    except redis.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Redis service is unavailable")

@router.get("/tasks")
async def get_all_tasks():
    try:
        tasks = redis_client.hgetall("image_tasks")
        result = {}
        for key, value in tasks.items():
            task_id = key.decode('utf-8')
            task_data = json.loads(value.decode('utf-8'))
            result[task_id] = task_data

        return {
            "status": "ok",
            "total_tasks": len(result),
            "tasks": result
        }
    except Exception as e:
        print(f"[red]Error in get_all_tasks: {type(e).__name__}: {str(e)}[/red]")
        raise HTTPException(status_code=500, detail=str(e))

