.PHONY: help install-server install-client generate-proto clean run-server run-client demo health test

PROTO_DIR = src/protos
GENERATED_DIR = src/generated
SERVER_DIR = src/server
CLIENT_DIR = src/client

help:
	@echo "Available commands:"
	@echo "  install-server    - Install server dependencies (Python 3.8)"
	@echo "  install-client    - Install client dependencies (Python 3.12)"
	@echo "  generate-proto    - Generate Python code from proto files"
	@echo "  run-server        - Run the gRPC server"
	@echo "  run-client        - Run the CLI client"
	@echo "  demo              - Run client demo"
	@echo "  health            - Check server health"
	@echo "  test              - Full test: install, generate, run server, test client, cleanup"
	@echo "  clean             - Clean generated files"

install-server:
	@echo "Installing server dependencies with uv (Python 3.8)..."
	cd $(SERVER_DIR) && uv venv --python 3.8
	cd $(SERVER_DIR) && uv pip install -r requirements.txt

install-client:
	@echo "Installing client dependencies with uv (Python 3.12)..."
	cd $(CLIENT_DIR) && uv venv --python 3.12
	cd $(CLIENT_DIR) && uv pip install -r requirements.txt

generate-proto:
	@echo "Generating Python code from proto files..."
	mkdir -p $(GENERATED_DIR)
	cd $(SERVER_DIR) && uv run python -m grpc_tools.protoc \
		--proto_path=../../$(PROTO_DIR) \
		--python_out=../../$(GENERATED_DIR) \
		--grpc_python_out=../../$(GENERATED_DIR) \
		../../$(PROTO_DIR)/*.proto
	touch $(GENERATED_DIR)/__init__.py

run-server:
	@echo "Starting gRPC server..."
	cd $(SERVER_DIR) && uv run python model_server.py

run-client:
	@echo "Running CLI client..."
	cd $(CLIENT_DIR) && uv run python cli_client.py

demo:
	@echo "Running demo..."
	cd $(CLIENT_DIR) && uv run python cli_client.py demo

health:
	@echo "Checking server health..."
	cd $(CLIENT_DIR) && uv run python cli_client.py health

test:
	@echo "Running full test suite..."
	@echo "Step 1: Installing dependencies..."
	$(MAKE) install-server
	$(MAKE) install-client
	@echo "Step 2: Generating protobuf files..."
	$(MAKE) generate-proto
	@echo "Step 3: Testing integration..."
	@./test_integration.sh
	@echo "Step 4: Cleaning up..."
	$(MAKE) clean
	@echo "✅ Test completed successfully!"

clean:
	@echo "Cleaning generated files..."
	rm -rf $(GENERATED_DIR)
	rm -rf $(SERVER_DIR)/.venv
	rm -rf $(CLIENT_DIR)/.venv