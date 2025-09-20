# CrewAI Pandoc Agent (Docker) — v1.1.0

**Copyright (c) RRECKTEK LLC**  
**Built:** @EPOCH

A robust, containerized Pandoc agent for converting Markdown files to PDFs using LaTeX templates, with daemon mode, agent-to-agent (A2A) messaging, and Prometheus metrics support.

## 🚀 Features

- **Multiple Processing Modes**: Batch, watch (foreground), and daemon (background service)
- **Intelligent Engine Fallbacks**: xelatex → lualatex → pdflatex → DOCX fallback
- **Template Validation**: Enhanced LaTeX template syntax and dependency checking
- **Deduplication**: SHA256-based job caching to avoid redundant processing
- **Agent-to-Agent (A2A) API**: HTTP endpoints for job submission and configuration
- **Prometheus Metrics**: Comprehensive metrics for monitoring and alerting
- **Robust Error Handling**: Disk space, permissions, template validation
- **Parallel Processing**: Multi-threaded file processing for better performance
- **Enhanced Logging**: File and syslog support with configurable levels

## 📋 Quick Start

```bash
# Extract and build
tar -xvf crewai-pandoc.tar.gz
cd crewai-pandoc
docker build -t rrecktek/crewai-pandoc:1.1.0 .

# Start daemon mode (recommended)
./run-pandoc-agent-watch.sh daemon

# Or one-shot batch processing
./run-pandoc-agent-watch.sh batch

# Or foreground watch mode
./run-pandoc-agent-watch.sh watch
```

## 📁 Directory Structure

```
crewai-pandoc/
├── input/              # Place .md files here
├── output/             # Generated PDFs/DOCX appear here
│   └── logs/           # Processing logs and job cache
├── app/
│   ├── main.py         # Enhanced agent script
│   └── template.tex    # LaTeX template (auto-created if missing)
├── Dockerfile
├── run-pandoc-agent-watch.sh  # Container management script
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `INPUT_DIR` | `./input` | Directory to watch for Markdown files |
| `OUTPUT_DIR` | `./output` | Directory for generated files and logs |
| `TEMPLATE_FILE` | `./app/template.tex` | LaTeX template file |
| `PIDFILE` | `/var/run/pandoc-agent.pid` | PID file for daemon mode |
| `METRICS_PORT` | `9090` | Prometheus metrics server port |
| `API_PORT` | `8080` | A2A API server port |

### Container Ports

- **9090**: Prometheus metrics (`/metrics` endpoint)
- **8080**: A2A API endpoints

## 🖥️ Usage

### Container Management

```bash
# Start daemon mode (background service)
./run-pandoc-agent-watch.sh daemon

# Start watch mode (foreground, Ctrl-C to stop)
./run-pandoc-agent-watch.sh watch

# One-shot batch processing
./run-pandoc-agent-watch.sh batch

# Check status and health
./run-pandoc-agent-watch.sh status
./run-pandoc-agent-watch.sh health

# View logs
./run-pandoc-agent-watch.sh logs
./run-pandoc-agent-watch.sh logs -f  # Follow logs

# Stop/restart container
./run-pandoc-agent-watch.sh stop
./run-pandoc-agent-watch.sh restart
```

### Direct Python Usage

```bash
# Inside container or with local Python setup
python3 main.py --help

# Examples
python3 main.py -i ./input -o ./output                    # Batch mode
python3 main.py -w -s 5                                   # Watch every 5 seconds
python3 main.py --daemon --metrics-port 9090 --api-port 8080  # Daemon mode
python3 main.py -f -t ./custom-template.tex               # Force with custom template
```

## 🔌 Agent-to-Agent (A2A) API

The agent provides HTTP endpoints for remote control and integration with other agents.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/status` | Get agent status and metrics |
| `GET` | `/config` | Get current configuration |
| `POST` | `/job` | Process specific file |
| `POST` | `/batch` | Trigger batch processing |
| `POST` | `/config` | Update configuration |

### Examples

```bash
# Health check
curl http://localhost:8080/health

# Get status and metrics
curl http://localhost:8080/status | jq

# Submit single file job
curl -X POST http://localhost:8080/job \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/work/input/document.md", "force": false}'

# Trigger batch processing
curl -X POST http://localhost:8080/batch \
  -H "Content-Type: application/json" \
  -d '{"force": false}'

# Update template configuration
curl -X POST http://localhost:8080/config \
  -H "Content-Type: application/json" \
  -d '{"template_file": "/opt/app/new-template.tex"}'
```

### Using the management script

```bash
# Submit job via script
./run-pandoc-agent-watch.sh job input/document.md

# Trigger batch processing
./run-pandoc-agent-watch.sh trigger-batch
```

## 📊 Prometheus Metrics

Access metrics at `http://localhost:9090/metrics`

### Available Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `pandoc_files_processed_total` | Counter | Successfully processed files |
| `pandoc_files_failed_total` | Counter | Failed processing attempts |
| `pandoc_files_skipped_total` | Counter | Files skipped (cached) |
| `pandoc_files_degraded_total` | Counter | Files converted to DOCX fallback |
| `pandoc_processing_time_seconds_total` | Counter | Total processing time |
| `pandoc_queue_depth` | Gauge | Current files in queue |
| `pandoc_template_validation_failures_total` | Counter | Template validation failures |
| `pandoc_daemon_uptime_seconds` | Gauge | Agent uptime |
| `pandoc_last_processing_timestamp` | Gauge | Last successful processing time |
| `pandoc_active_jobs` | Gauge | Currently processing files |
| `pandoc_engine_usage_total` | Counter | Usage by engine (xelatex, lualatex, etc.) |

### Grafana Dashboard

Example PromQL queries:

```promql
# Processing rate
rate(pandoc_files_processed_total[5m])

# Error rate
rate(pandoc_files_failed_total[5m]) / rate(pandoc_files_processed_total[5m])

# Queue depth over time
pandoc_queue_depth

# Average processing time
rate(pandoc_processing_time_seconds_total[5m]) / rate(pandoc_files_processed_total[5m])
```

## 🔧 Template System

### Template Validation

The agent performs comprehensive template validation:

- **Syntax checking**: Balanced braces, required document structure
- **Dependency analysis**: Missing packages, document classes
- **Font validation**: fontspec fonts via fontconfig
- **Binary requirements**: biber, bibtex availability

### Custom Templates

Place custom LaTeX templates in `app/template.tex`:

```latex
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{hyperref}

% Custom styling here
\geometry{margin=1.5in}

\title{$title$}
\author{$author$}
\date{$date$}

\begin{document}
$if(title)$\maketitle$endif$
$body$
\end{document}
```

### Engine Fallback Strategy

1. **xelatex** with template
2. **lualatex** with template  
3. **pdflatex** with template
4. **xelatex** without template
5. **lualatex** without template
6. **pdflatex** without template
7. **DOCX fallback** (degraded mode)

## 📋 Processing Workflow

1. **File Discovery**: Scans input directory for `.md` files
2. **Deduplication**: Computes job key from file + template hash
3. **Cache Check**: Skips if already processed (unless `--force`)
4. **Validation**: Template syntax and dependency checking
5. **Processing**: Attempts conversion with engine fallbacks
6. **Output**: Saves to output directory with epoch timestamp
7. **Logging**: Detailed logs in `output/logs/`
8. **Metrics**: Updates Prometheus counters and gauges

## 🔍 Debugging and Troubleshooting

### Check Container Status

```bash
./run-pandoc-agent-watch.sh status
./run-pandoc-agent-watch.sh health
```

### View Logs

```bash
# Container logs
./run-pandoc-agent-watch.sh logs -f

# Processing logs (inside container)
docker exec pandoc-agent ls -la /work/output/logs/
docker exec pandoc-agent tail -f /work/output/logs/*.log
```

### Common Issues

**Template Validation Failures:**
- Check template syntax with `--log-level DEBUG`
- Verify package installations in container
- Use `--force` to bypass validation temporarily

**Permission Issues:**
- Ensure host directories are writable
- Check Docker volume mount permissions

**Processing Failures:**
- Review individual job logs in `output/logs/`
- Check available disk space
- Verify input file encoding (UTF-8 required)

**Service Not Responding:**
- Check if ports 8080/9090 are available
- Verify container is running: `docker ps`
- Check firewall settings

### Manual Testing

```bash
# Test inside container
docker exec -it pandoc-agent bash
cd /work
echo "# Test Document" > input/test.md
python3 /opt/app/main.py -f

# Check template dependencies
docker exec pandoc-agent python3 /opt/app/main.py --help
```

## 🚀 Advanced Configuration

### Custom Docker Build

```dockerfile
FROM rrecktek/crewai-pandoc:1.1.0
# Add custom packages or fonts
RUN apt-get update && apt-get install -y custom-package
COPY custom-template.tex /opt/app/template.tex
```

### Production Deployment

```bash
# With persistent volumes
docker run -d --name pandoc-agent \
  --restart always \
  -v /host/data/input:/work/input \
  -v /host/data/output:/work/output \
  -v /host/templates:/opt/app \
  -p 9090:9090 -p 8080:8080 \
  rrecktek/crewai-pandoc:1.1.0 \
  python3 /opt/app/main.py --daemon --log-level INFO
```

### Integration with Monitoring

```yaml
# docker-compose.yml example
version: "3.9"
services:
  pandoc-agent:
    image: rrecktek/crewai-pandoc:1.1.0
    restart: unless-stopped
    ports:
      - "9090:9090"
      - "8080:8080"
    volumes:
      - ./input:/work/input
      - ./output:/work/output
      - ./app:/opt/app
    command: ["python3", "/opt/app/main.py", "--daemon"]
    
  prometheus:
    image: prom/prometheus
    ports:
      - "9091:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

## 📝 Development

### Dependencies

- Python 3.9+
- `python-daemon` for daemon mode
- Pandoc 3.2.1+
- TeX Live (LaTeX engines)
- Standard HTTP libraries (built-in)

### Contributing

1. Fork the repository
2. Create feature branch
3. Test with provided examples
4. Update documentation
5. Submit pull request

## 📜 License

Copyright (c) RRECKTEK LLC. All rights reserved.

## 🆘 Support

- Check logs first: `./run-pandoc-agent-watch.sh logs`
- Validate configuration: `./run-pandoc-agent-watch.sh status`
- Test health endpoints: `./run-pandoc-agent-watch.sh health`
- Review metrics: `curl http://localhost:9090/metrics`
