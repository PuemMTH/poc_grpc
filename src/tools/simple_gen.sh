#!/bin/bash

# Simple Protocol Buffer Generator
# อ่าน config จาก protogen.json แล้ว generate protobuf files

set -e

# หา config file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$SCRIPT_DIR/protogen.json"

# อ่าน config จาก JSON
INPUT_FOLDER=$(cat "$CONFIG_FILE" | python3 -c "import sys, json; print(json.load(sys.stdin)['input_folder'])")
OUTPUT_FOLDERS=$(cat "$CONFIG_FILE" | python3 -c "import sys, json; print(' '.join(json.load(sys.stdin)['output_folders']))")

echo "🔧 Generating protobuf files..."
echo "📂 Input: $INPUT_FOLDER"

# Convert to absolute paths
INPUT_FOLDER="$PROJECT_ROOT/$INPUT_FOLDER"

# Check if proto files exist
if [ ! -d "$INPUT_FOLDER" ]; then
    echo "❌ Input folder not found: $INPUT_FOLDER"
    exit 1
fi

# Generate สำหรับแต่ละ output folder
for output_folder in $OUTPUT_FOLDERS; do
    # Convert to absolute path
    abs_output_folder="$PROJECT_ROOT/$output_folder"
    echo "📁 Generating to: $abs_output_folder"

    # สร้าง output directory
    mkdir -p "$abs_output_folder"

    # หา proto files
    for proto_file in "$INPUT_FOLDER"/*.proto; do
        if [ -f "$proto_file" ]; then
            filename=$(basename "$proto_file")

            # Run protoc (need to be in server directory for uv environment)
            if (cd "$PROJECT_ROOT/src/server/sample_service" && uv run python -m grpc_tools.protoc \
                --proto_path="$INPUT_FOLDER" \
                --python_out="$abs_output_folder" \
                --grpc_python_out="$abs_output_folder" \
                "$proto_file"); then
                echo "  ✅ $filename"
            else
                echo "  ❌ $filename"
                exit 1
            fi
        fi
    done

    # สร้าง __init__.py
    touch "$abs_output_folder/__init__.py"
done

echo "🎉 Done!"