import os
import pika

class WorkerQueueClient(object):
    def __init__(self, queue_name):
        self.queue_name = queue_name
        url = os.environ.get('CLOUDAMQP_URL')
        params = pika.URLParameters(url)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        # Declare the queue as durable for persistence
        self.channel.queue_declare(queue=self.queue_name, durable=False)

    def send_task(self, body):
        """Send a task to the worker queue"""
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        print(f"Task sent to queue: {self.queue_name}")

    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
