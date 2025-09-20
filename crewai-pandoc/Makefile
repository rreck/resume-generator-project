# CrewAI Pandoc Agent Makefile
# Copyright (c) RRECKTEK LLC
# Version: 1.1.0

.PHONY: help build run batch watch daemon status logs stop clean test health

# Default target
help:
	@echo "CrewAI Pandoc Agent - Available Commands:"
	@echo ""
	@echo "Building and Setup:"
	@echo "  build         Build the Docker image"
	@echo "  clean         Remove container and clean up"
	@echo ""
	@echo "Running Modes:"
	@echo "  daemon        Start daemon mode (background service)"
	@echo "  watch         Start watch mode (foreground)"
	@echo "  batch         Run one-shot batch processing"
	@echo ""
	@echo "Management:"
	@echo "  status        Show container and service status"
	@echo "  health        Check health endpoints"
	@echo "  logs          Show container logs"
	@echo "  logs-f        Follow container logs"
	@echo "  stop          Stop the container"
	@echo "  restart       Restart the container"
	@echo ""
	@echo "Development:"
	@echo "  test          Run basic functionality tests"
	@echo "  shell         Open shell in running container"
	@echo "  debug         Start container with debug logging"
	@echo ""
	@echo "Examples:"
	@echo "  make build && make daemon     # Build and start daemon"
	@echo "  make test                     # Test functionality"
	@echo "  make logs-f                   # Follow logs in real-time"

# Build the Docker image
build:
	@echo "Building CrewAI Pandoc Agent Docker image..."
	docker build -t rrecktek/crewai-pandoc:1.1.0 .
	@echo "Build complete!"

# Start daemon mode
daemon:
	@echo "Starting Pandoc Agent in daemon mode..."
	./run-pandoc-agent-watch.sh daemon

# Start watch mode  
watch:
	@echo "Starting Pandoc Agent in watch mode..."
	./run-pandoc-agent-watch.sh watch

# Run batch processing
batch:
	@echo "Running batch processing..."
	./run-pandoc-agent-watch.sh batch

# Show status
status:
	@echo "Checking agent status..."
	./run-pandoc-agent-watch.sh status

# Check health
health:
	@echo "Checking health endpoints..."
	./run-pandoc-agent-watch.sh health

# Show logs
logs:
	@echo "Showing container logs..."
	./run-pandoc-agent-watch.sh logs

# Follow logs
logs-f:
	@echo "Following container logs... (Ctrl-C to stop)"
	./run-pandoc-agent-watch.sh logs -f

# Stop container
stop:
	@echo "Stopping Pandoc Agent..."
	./run-pandoc-agent-watch.sh stop

# Restart container  
restart:
	@echo "Restarting Pandoc Agent..."
	./run-pandoc-agent-watch.sh restart

# Clean up
clean:
	@echo "Cleaning up..."
	./run-pandoc-agent-watch.sh remove
	docker image prune -f
	@echo "Cleanup complete!"

# Run tests
test:
	@echo "Running basic functionality tests..."
	@mkdir -p input output app
	@echo "# Test Document\n\nThis is a test **markdown** document.\n\n- Item 1\n- Item 2" > input/test.md
	@echo "Template file check..."
	@ls -la app/template.tex 2>/dev/null || echo "Template will be auto-created"
	@echo "Starting test batch processing..."
	./run-pandoc-agent-watch.sh batch
	@echo "Checking output..."
	@ls -la output/
	@echo "Test logs:"
	@ls -la output/logs/ 2>/dev/null || echo "No logs found"
	@echo "Running enhanced test suite..."
	python3 run_tests.py || echo "⚠️ Enhanced tests failed or not available"
	@echo "Test complete!"

# Open shell in running container
shell:
	@echo "Opening shell in running container..."
	docker exec -it pandoc-agent bash

# Start with debug logging
debug:
	@echo "Starting with debug logging..."
	docker run --rm -it \
		-v $(PWD)/input:/work/input \
		-v $(PWD)/output:/work/output \
		-v $(PWD)/app:/opt/app \
		-p 9090:9090 -p 8080:8080 \
		rrecktek/crewai-pandoc:1.1.0 \
		python3 /opt/app/main.py --log-level DEBUG -w

# Install dependencies for local development
dev-setup:
	@echo "Setting up development environment..."
	pip3 install python-daemon
	@echo "Development setup complete!"

# Lint and validate
lint:
	@echo "Validating scripts..."
	@bash -n run-pandoc-agent-watch.sh && echo "✓ Shell script syntax OK" || echo "✗ Shell script syntax error"
	@python3 -m py_compile main.py && echo "✓ Python script syntax OK" || echo "✗ Python script syntax error"
	@echo "Validation complete!"

# Create sample files
samples:
	@echo "Creating sample files..."
	@mkdir -p input
	@cat > input/sample1.md << 'EOF' ;\
	echo "# Sample Document 1" > input/sample1.md ;\
	echo "" >> input/sample1.md ;\
	echo "This is a **sample** Markdown document for testing the CrewAI Pandoc Agent." >> input/sample1.md ;\
	echo "" >> input/sample1.md ;\
	echo "## Features" >> input/sample1.md ;\
	echo "" >> input/sample1.md ;\
	echo "- Converts Markdown to PDF" >> input/sample1.md ;\
	echo "- Uses LaTeX templates" >> input/sample1.md ;\
	echo "- Supports multiple engines" >> input/sample1.md ;\
	echo "" >> input/sample1.md ;\
	echo "### Code Example" >> input/sample1.md ;\
	echo "" >> input/sample1.md ;\
	echo '```python' >> input/sample1.md ;\
	echo 'def hello_world():' >> input/sample1.md ;\
	echo '    print("Hello, World!")' >> input/sample1.md ;\
	echo '```' >> input/sample1.md ;\
	echo "" >> input/sample1.md ;\
	echo "### Math Example" >> input/sample1.md ;\
	echo "" >> input/sample1.md ;\
	echo '$$E = mc^2$$' >> input/sample1.md ;\
	echo "" >> input/sample1.md ;\
	echo "That's it!" >> input/sample1.md
	@echo "# Another Sample" > input/sample2.md ;\
	echo "" >> input/sample2.md ;\
	echo "This is another test document with different content." >> input/sample2.md ;\
	echo "" >> input/sample2.md ;\
	echo "## Table Example" >> input/sample2.md ;\
	echo "" >> input/sample2.md ;\
	echo "| Name | Role | Status |" >> input/sample2.md ;\
	echo "|------|------|--------|" >> input/sample2.md ;\
	echo "| Alice | Developer | Active |" >> input/sample2.md ;\
	echo "| Bob | Designer | Active |" >> input/sample2.md ;\
	echo "| Carol | Manager | On Leave |" >> input/sample2.md ;\
	echo "" >> input/sample2.md ;\
	echo "## List Example" >> input/sample2.md ;\
	echo "" >> input/sample2.md ;\
	echo "1. First item" >> input/sample2.md ;\
	echo "2. Second item" >> input/sample2.md ;\
	echo "   - Nested item A" >> input/sample2.md ;\
	echo "   - Nested item B" >> input/sample2.md ;\
	echo "3. Third item" >> input/sample2.md ;\
	echo "" >> input/sample2.md ;\
	echo "> This is a blockquote with some important information." >> input/sample2.md ;\
	echo "" >> input/sample2.md ;\
	echo "The end." >> input/sample2.md
	@echo "Sample files created in input/ directory!"
	@ls -la input/

# Monitor metrics in real-time
metrics:
	@echo "Monitoring Prometheus metrics..."
	@echo "Press Ctrl-C to stop"
	@while true; do \
		echo "=== $(date) ==="; \
		curl -s http://localhost:9090/metrics | grep -E "(pandoc_files|pandoc_queue|pandoc_active)" || echo "Metrics not available"; \
		echo ""; \
		sleep 5; \
	done

# API testing
api-test:
	@echo "Testing A2A API endpoints..."
	@echo "1. Health check:"
	@curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || echo "Health endpoint not available"
	@echo ""
	@echo "2. Status check:"
	@curl -s http://localhost:8080/status | python3 -m json.tool 2>/dev/null || echo "Status endpoint not available"
	@echo ""
	@echo "3. Config check:"
	@curl -s http://localhost:8080/config | python3 -m json.tool 2>/dev/null || echo "Config endpoint not available"
	@echo ""
	@echo "API test complete!"

# Submit test job via API
submit-job:
	@echo "Submitting test job via A2A API..."
	@mkdir -p input
	@echo "# API Test Job\n\nThis job was submitted via the A2A API." > input/api-test.md
	@curl -s -X POST http://localhost:8080/job \
		-H "Content-Type: application/json" \
		-d '{"file_path": "/work/input/api-test.md", "force": true}' \
		| python3 -m json.tool 2>/dev/null || echo "Failed to submit job"

# Full integration test
integration-test: build samples
	@echo "Running full integration test..."
	@echo "1. Starting daemon..."
	@make daemon
	@sleep 5
	@echo "2. Checking health..."
	@make health
	@echo "3. Testing API..."
	@make api-test
	@echo "4. Submitting job..."
	@make submit-job
	@sleep 3
	@echo "5. Checking results..."
	@ls -la output/
	@echo "6. Checking metrics..."
	@curl -s http://localhost:9090/metrics | head -20
	@echo ""
	@echo "Integration test complete!"

# Backup output directory
backup:
	@echo "Creating backup of output directory..."
	@tar -czf "pandoc-output-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz" output/
	@echo "Backup created!"

# View recent processing results
results:
	@echo "Recent processing results:"
	@echo "========================="
	@echo "Output files:"
	@ls -lat output/*.pdf output/*.docx 2>/dev/null | head -10 || echo "No output files found"
	@echo ""
	@echo "Recent logs:"
	@ls -lat output/logs/*.log 2>/dev/null | head -5 || echo "No log files found"
	@echo ""
	@echo "Last 10 log entries:"
	@tail -10 output/logs/*.log 2>/dev/null | tail -10 || echo "No log content found"

# Performance monitoring
perf:
	@echo "Performance monitoring..."
	@echo "Press Ctrl-C to stop"
	@while true; do \
		clear; \
		echo "=== CrewAI Pandoc Agent Performance Monitor ==="; \
		echo "Time: $(date)"; \
		echo ""; \
		echo "Container Stats:"; \
		docker stats --no-stream pandoc-agent 2>/dev/null || echo "Container not running"; \
		echo ""; \
		echo "Metrics Summary:"; \
		curl -s http://localhost:9090/metrics 2>/dev/null | grep -E "(files_processed|files_failed|active_jobs|queue_depth)" | head -10 || echo "Metrics not available"; \
		echo ""; \
		echo "Recent Files:"; \
		ls -lt output/*.pdf output/*.docx 2>/dev/null | head -3 || echo "No recent files"; \
		sleep 10; \
	done

# Quick start for new users
quickstart: build samples daemon
	@echo ""
	@echo "🚀 CrewAI Pandoc Agent Quick Start Complete!"
	@echo "=============================================="
	@echo ""
	@echo "✅ Docker image built"
	@echo "✅ Sample files created"
	@echo "✅ Daemon started"
	@echo ""
	@echo "Next steps:"
	@echo "1. Check status:    make status"
	@echo "2. Monitor logs:    make logs-f" 
	@echo "3. View results:    make results"
	@echo "4. Test API:        make api-test"
	@echo "5. View metrics:    open http://localhost:9090/metrics"
	@echo "6. API endpoints:   open http://localhost:8080/status"
	@echo ""
	@echo "Add your .md files to the input/ directory and they'll be processed automatically!"

# Show all available make targets
targets:
	@echo "Available make targets:"
	@echo "======================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $1, $2}'
	@echo ""
	@echo "Or run 'make help' for detailed information."
