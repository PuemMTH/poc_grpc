.PHONY: help install generate-proto generate-proto-sh run-server run-client clean monitor dev-services sample-service api-consumer api-producer stop-services kill-ports

PROTO_DIR = src/protos
SERVER_DIR = src/server/image_service
CLIENT_CLI_DIR = src/client/cli
CLIENT_API_DIR = src/client/api
TOOLS_DIR = src/tools
SESSION_NAME = grpc_services

help:
	@echo "Available commands:"
	@echo "  install            - Install all dependencies"
	@echo "  generate-proto     - Generate Python files from proto (simple Python script)"
	@echo "  generate-proto-sh  - Generate using Shell script"
	@echo "  run-server         - Run the gRPC server"
	@echo "  run-client         - Run the CLI client"
	@echo "  clean              - Clean generated files"
	@echo "  monitor            - Monitor Docker services with logs"
	@echo ""
	@echo "Development Services:"
	@echo "  dev-services       - Start all services in tmux session"
	@echo "  stop-services      - Stop tmux session"
	@echo "  kill-ports         - Kill processes using ports 50052 and 8000"

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

kill-ports:
	@echo "🔪 Killing processes on ports 50052 and 8000..."
	@lsof -ti:50052 | xargs kill -9 2>/dev/null || echo "No process found on port 50052"
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No process found on port 8000"
	@echo "✅ Port cleanup completed"

dev-services: kill-ports
	@echo "🚀 Starting all services in tmux session: $(SESSION_NAME)"
	@tmux new-session -d -s $(SESSION_NAME) || true
	@tmux send-keys -t $(SESSION_NAME) "export SAMPLE_SERVICE_PORT=50052 && cd src/server/sample_service/ && echo '🔧 Sample Service (Port 50052)' && uv run main.py" C-m
	@tmux split-window -h -t $(SESSION_NAME)
	@tmux send-keys -t $(SESSION_NAME) "echo '⏳ Waiting for Sample Service to start...' && sleep 3 && export RABBITMQ_HOST=localhost RABBITMQ_PORT=5672 RABBITMQ_QUEUE=image_queue CLOUDAMQP_URL='amqp://guest:guest@localhost:5672/%2f' SAMPLE_SERVICE_ADDRESS='localhost:50052' && cd src/client/api-consumer && echo '📥 API Consumer (RabbitMQ)' && uv run main.py" C-m
	@tmux split-window -v -t $(SESSION_NAME):0.1
	@tmux send-keys -t $(SESSION_NAME) "echo '⏳ Waiting for services to start...' && sleep 2 && export REDIS_HOST=localhost REDIS_PORT=6379 CLOUDAMQP_URL='amqp://guest:guest@localhost:5672/%2f' && cd src/client/api-producer && echo '📤 API Producer (Redis)' && uv run main.py" C-m
	@tmux attach-session -t $(SESSION_NAME)

stop-services:
	@echo "🛑 Stopping tmux session: $(SESSION_NAME)"
	@tmux kill-session -t $(SESSION_NAME) 2>/dev/null || echo "Session $(SESSION_NAME) not found"