#!/usr/bin/env python3
"""Fix imports in generated protobuf files"""

import json
import re
from pathlib import Path

def fix_grpc_imports(file_path):
    """Fix relative imports in generated grpc files"""
    with open(file_path, 'r') as f:
        content = f.read()

    # Fix import statements
    content = re.sub(
        r'^import (.+_pb2) as (.+)$',
        r'from . import \1 as \2',
        content,
        flags=re.MULTILINE
    )

    with open(file_path, 'w') as f:
        f.write(content)

    print(f"Fixed imports in {file_path}")

def main():
    # Load config to find output folders
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    config_file = script_dir / "protogen.json"

    with open(config_file) as f:
        config = json.load(f)

    # Fix imports in all output folders
    for folder in config["output_folders"]:
        output_dir = project_root / folder

        # Find all *_grpc.py files
        for grpc_file in output_dir.glob("*_grpc.py"):
            fix_grpc_imports(grpc_file)

if __name__ == "__main__":
    main()