import grpc
import click
import sys
import os
from rich.console import Console
from rich.table import Table
from rich import print as rprint

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'generated'))

console = Console()

@click.group()
def cli():
    """gRPC Model Service Client"""
    pass