import os, pika, time
import random
from rich import print

def on_request(ch, method, properties, body: bytes):
    job_data = body.decode()
    job_data = eval(job_data)  # Convert string representation of dict back to dict
    print(f"[reset][yellow][~] {str(job_data['image_uuid'])} \n[reset][yellow][~] {str(job_data['image_path'])}")
    time.sleep(2)
    if random.choice([True, False]):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("[green][✓] Job processed successfully[/green]")
    else:
        ch.basic_nack(delivery_tag=method.delivery_tag)
        print("[red][✗] Job processing failed[/red]")

if __name__ == "__main__":
    # export RABBITMQ_HOST=localhost RABBITMQ_PORT=5672 RABBITMQ_QUEUE=image_queue CLOUDAMQP_URL='amqp://guest:guest@localhost:5672/%2f' && uv run main.py
    url = os.environ.get('CLOUDAMQP_URL')
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=os.environ.get('RABBITMQ_QUEUE'), durable=False) # Declare the queue if it doesn't exist
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=os.environ.get('RABBITMQ_QUEUE'), on_message_callback=on_request)
    print(" [>>] Awaiting RPC requests")
    channel.start_consuming()