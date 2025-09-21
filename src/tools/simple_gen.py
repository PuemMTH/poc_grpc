#!/usr/bin/env python3
"""
Simple Protocol Buffer Generator
อ่าน config จาก protogen.json แล้ว generate protobuf files
"""

import json
import subprocess
import sys
from pathlib import Path

def main():
    # หา config file และ project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    config_file = script_dir / "protogen.json"

    # อ่าน config
    with open(config_file) as f:
        config = json.load(f)

    # Convert paths เป็น absolute
    input_folder = project_root / config["input_folder"]
    output_folders = [project_root / folder for folder in config["output_folders"]]

    print(f"🔧 Generating protobuf files...")
    print(f"📂 Input: {input_folder}")

    # หา proto files ทั้งหมด
    proto_files = list(input_folder.glob("*.proto"))

    if not proto_files:
        print("❌ No .proto files found!")
        sys.exit(1)

    # Generate สำหรับแต่ละ output folder
    for output_folder in output_folders:
        print(f"📁 Generating to: {output_folder}")

        # สร้าง output directory
        output_folder.mkdir(parents=True, exist_ok=True)

        # Run protoc สำหรับแต่ละ proto file
        for proto_file in proto_files:
            cmd = [
                "uv", "run", "python", "-m", "grpc_tools.protoc",
                f"--proto_path={input_folder}",
                f"--python_out={output_folder}",
                f"--grpc_python_out={output_folder}",
                str(proto_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"  ✅ {proto_file.name}")
            else:
                print(f"  ❌ {proto_file.name}: {result.stderr}")
                sys.exit(1)

        # สร้าง __init__.py
        init_file = output_folder / "__init__.py"
        init_file.touch(exist_ok=True)

    # Fix imports in generated files
    print("🔧 Fixing imports in generated files...")
    fix_imports_script = Path(__file__).parent / "fix_imports.py"
    subprocess.run([
        "uv", "run", "python", str(fix_imports_script)
    ], cwd=Path.cwd())

    print("🎉 Done!")

if __name__ == "__main__":
    main()