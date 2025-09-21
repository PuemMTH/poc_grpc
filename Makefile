.PHONY: help install generate-proto generate-proto-sh run-server run-client clean

PROTO_DIR = src/protos
SERVER_DIR = src/server/image_service
CLIENT_DIR = src/client
TOOLS_DIR = src/tools

help:
	@echo "Available commands:"
	@echo "  install            - Install all dependencies"
	@echo "  generate-proto     - Generate Python files from proto (simple Python script)"
	@echo "  generate-proto-sh  - Generate using Shell script"
	@echo "  run-server         - Run the gRPC server"
	@echo "  run-client         - Run the CLI client"
	@echo "  clean              - Clean generated files"

install:
	cd $(SERVER_DIR) && uv sync
	cd $(CLIENT_DIR) && uv sync

generate-proto:
	@echo "🔧 Generating protobuf files using simple script..."
	@cd $(SERVER_DIR) && uv run python ../../../$(TOOLS_DIR)/simple_gen.py

generate-proto-sh:
	@echo "🔧 Generating protobuf files using Shell script..."
	@$(TOOLS_DIR)/simple_gen.sh

run-server:
	cd $(SERVER_DIR) && uv run python main.py

run-client:
	cd $(CLIENT_DIR) && uv run python poc_grpc/main.py

clean:
	@echo "🧹 Cleaning generated files and cache..."
	rm -rf $(SERVER_DIR)/protos/*.py $(CLIENT_DIR)/poc_grpc/protos/*.py
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name ".venv" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup completed"