.PHONY: help install generate-proto generate-proto-sh run-server run-client clean monitor

PROTO_DIR = src/protos
SERVER_DIR = src/server/image_service
CLIENT_CLI_DIR = src/client/cli
CLIENT_API_DIR = src/client/api
TOOLS_DIR = src/tools

help:
	@echo "Available commands:"
	@echo "  install            - Install all dependencies"
	@echo "  generate-proto     - Generate Python files from proto (simple Python script)"
	@echo "  generate-proto-sh  - Generate using Shell script"
	@echo "  run-server         - Run the gRPC server"
	@echo "  run-client         - Run the CLI client"
	@echo "  clean              - Clean generated files"
	@echo "  monitor            - Monitor Docker services with logs"

install:
	cd $(CLIENT_CLI_DIR) && uv sync
	cd $(CLIENT_API_DIR) && uv sync
	cd $(SERVER_DIR) && uv sync

generate-proto:
	@echo "🔧 Generating protobuf files using simple script..."
	@cd $(SERVER_DIR) && uv run python ../../../$(TOOLS_DIR)/simple_gen.py

generate-proto-sh:
	@echo "🔧 Generating protobuf files using Shell script..."
	@$(TOOLS_DIR)/simple_gen.sh

run-server:
	cd $(SERVER_DIR) && uv run python main.py

run-client:
	cd $(CLIENT_CLI_DIR) && uv run python main.py

run-client-api:
	cd $(CLIENT_API_DIR) && uv run python main.py

clean:
	@echo "🧹 Cleaning generated files and cache..."
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name ".venv" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup completed"

run-tmux-dev:
	tmux new-session -d -s grpc_session
	tmux send-keys -t grpc_session 'uvx watchfiles "make run-server" ${SERVER_DIR}/main.py' C-m
	tmux split-window -h
	tmux send-keys -t grpc_session 'make run-client-api' C-m
	tmux attach -t grpc_session

kill-tmux:
	tmux kill-session -t grpc_session || true

monitor:
	@echo "🔍 Starting Docker services monitoring..."
	cd src/server && docker-compose up -d --build
	@echo "📊 Showing live logs (Press Ctrl+C to exit)..."
	cd src/server && docker-compose logs -f