import grpc
import click
import sys
import os
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text
import time
from pathlib import Path

from protos import image_service_pb2
from protos import image_service_pb2_grpc

console = Console()


def get_channel(host='localhost', port=50051):
    """Create a gRPC channel to the server."""
    return grpc.insecure_channel(f'{host}:{port}')


@click.group()
def cli():
    """gRPC Image Service Client"""
    pass


@cli.command()
@click.option('--host', default='localhost', help='Server host')
@click.option('--port', default=50051, help='Server port')
def health(host, port):
    """Check server health status."""
    try:
        with get_channel(host, port) as channel:
            stub = image_service_pb2_grpc.ImageServiceStub(channel)

            console.print("[bold yellow]Checking server health...[/bold yellow]")

            request = image_service_pb2.HealthRequest()
            response = stub.Health(request, timeout=5.0)

            if response.status == "healthy":
                console.print(Panel(
                    f"[bold green]✓ Server is healthy[/bold green]\n{response.message}",
                    title="Health Check",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    f"[bold red]✗ Server unhealthy[/bold red]\n{response.message}",
                    title="Health Check",
                    border_style="red"
                ))

    except grpc.RpcError as e:
        console.print(Panel(
            f"[bold red]✗ Connection failed[/bold red]\nError: {e.details()}",
            title="Health Check",
            border_style="red"
        ))
    except Exception as e:
        console.print(Panel(
            f"[bold red]✗ Unexpected error[/bold red]\nError: {str(e)}",
            title="Health Check",
            border_style="red"
        ))


@cli.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--host', default='localhost', help='Server host')
@click.option('--port', default=50051, help='Server port')
@click.option('--format', 'image_format', help='Image format (auto-detected if not specified)')
def test_image(image_path, host, port, image_format):
    """Test image processing with the server."""
    try:
        image_path = Path(image_path)

        # Auto-detect format if not provided
        if not image_format:
            image_format = image_path.suffix.lower().lstrip('.')
            if image_format == 'jpg':
                image_format = 'jpeg'

        # Read image file
        console.print(f"[bold yellow]Reading image file: {image_path}[/bold yellow]")
        with open(image_path, 'rb') as f:
            image_data = f.read()

        file_size = len(image_data)
        console.print(f"Image size: {file_size:,} bytes")

        # Connect to server and send request
        with get_channel(host, port) as channel:
            stub = image_service_pb2_grpc.ImageServiceStub(channel)

            console.print(f"[bold yellow]Sending image to server (format: {image_format})...[/bold yellow]")

            request = image_service_pb2.TestImageRequest(
                image_data=image_data,
                image_format=image_format
            )

            start_time = time.time()
            response = stub.TestImage(request, timeout=30.0)
            end_time = time.time()

            processing_time = (end_time - start_time) * 1000  # Convert to milliseconds

            # Display results
            if response.status == "success":
                console.print(Panel(
                    f"[bold green]✓ Image processed successfully[/bold green]\n"
                    f"{response.message}\n"
                    f"Processing time: {processing_time:.2f}ms",
                    title="Image Test Result",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    f"[bold red]✗ Image processing failed[/bold red]\n{response.message}",
                    title="Image Test Result",
                    border_style="red"
                ))

    except grpc.RpcError as e:
        console.print(Panel(
            f"[bold red]✗ gRPC Error[/bold red]\nCode: {e.code()}\nDetails: {e.details()}",
            title="Image Test Result",
            border_style="red"
        ))
    except FileNotFoundError:
        console.print(Panel(
            f"[bold red]✗ File not found[/bold red]\nPath: {image_path}",
            title="Image Test Result",
            border_style="red"
        ))
    except Exception as e:
        console.print(Panel(
            f"[bold red]✗ Unexpected error[/bold red]\nError: {str(e)}",
            title="Image Test Result",
            border_style="red"
        ))


@cli.command()
@click.option('--host', default='localhost', help='Server host')
@click.option('--port', default=50051, help='Server port')
@click.option('--count', default=1, help='Number of health checks to perform')
def monitor(host, port, count):
    """Monitor server health over time."""
    console.print(f"Monitoring server health [yellow]{count}[/yellow] checks")

    results = []
    for i in range(count):
        with get_channel(host, port) as channel:
            stub = image_service_pb2_grpc.ImageServiceStub(channel)
            start_time = time.time()
            request = image_service_pb2.HealthRequest()
            response = stub.Health(request, timeout=5.0)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            results.append({
                'check': i + 1,
                'status': response.status,
                'response_time': response_time,
                'timestamp': time.strftime('%H:%M:%S')
            })

    if results:
        total_time = sum(r['response_time'] for r in results if r['status'] == 'healthy')
        avg_time = total_time / len([r for r in results if r['status'] == 'healthy']) if total_time > 0 else 0
        console.print(f"Average response time for [yellow]{count}[/yellow] [reset]Check(s):[/reset] [yellow]{avg_time:.2f}ms[/yellow]")
    else:
        console.print("[bold red]No results to calculate average response time.[/bold red]")


def main():
    cli()


if __name__ == '__main__':
    main()