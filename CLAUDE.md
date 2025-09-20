# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Repository Overview

This workspace contains CrewAI agents following a standardized architecture pattern. All agents are based on the design patterns from:
- https://github.com/rreck/agent/tree/main/crewai-pandoc
- https://github.com/rreck/agent/tree/main/crewai-transcribe

**Current Status**: New empty repository ready for agent development.

## Critical Rules (ALWAYS Follow)

### Directory Structure
- Create subdirectories named `crewai-*` at the root level
- Avoid non-printable characters and spaces in file/directory names
- Cache files like packages and Docker images for reuse

### Tools & Commands
- Use `gh` command line tool for all GitHub interactions
- Test network connectivity with `ping 8.8.8.8` when encountering network issues
- Address path problems immediately when encountered

### Architecture Patterns
- Make MINIMAL CHANGES to existing patterns and structures
- Preserve existing naming conventions and file organization
- Follow established architecture and component patterns
- Use existing utility functions, avoid duplicating functionality

## Standard Agent Directory Structure

Every new CrewAI agent MUST follow this structure:

```
crewai-<agent>/
├── input/              # Input files (e.g., .md files)
├── output/             # Generated outputs
│   └── logs/           # Processing logs and job cache
├── app/
│   ├── main.py         # Main agent script
│   └── template.*      # Templates (auto-created if missing)
├── metrics/
│   ├── <agent>-dashboard.json  # Grafana dashboard
│   └── prometheus.yml          # Prometheus collector config
├── Dockerfile
├── run-<agent>-watch.sh        # Container management script
└── README.md
```

## Required Agent Components

### 1. Agent-to-Agent (A2A) API
Every agent MUST implement these HTTP endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /health  | Health check |
| GET    | /status  | Agent status and metrics |
| GET    | /config  | Current configuration |
| POST   | /job     | Process specific file |
| POST   | /batch   | Trigger batch processing |
| POST   | /config  | Update configuration |

### 2. Standard Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| INPUT_DIR | ./input | Directory for input files |
| OUTPUT_DIR | ./output | Directory for outputs and logs |
| PIDFILE | /var/run/<agent>.pid | PID file for daemon mode |
| METRICS_PORT | 9090 | Prometheus metrics server port |
| API_PORT | 8080 | A2A API server port |

### 3. Prometheus Metrics
- Expose all useful metrics to Prometheus exporter
- Independent Prometheus and Grafana are running (don't provide these)
- Include example Grafana dashboards in `metrics/` directory

### 4. Required README.md Sections
Every agent README.md MUST contain:
- **Quick Start**: Immediate setup instructions
- **Directory Structure**: File organization explanation
- **Environment Variables**: All configurable variables
- **Configuration**: Setup and customization options
- **Usage**: Operating instructions and examples
- **API Endpoints**: A2A interface documentation

## Development Workflow

1. **Create Agent Structure**: Follow standard directory layout
2. **Implement Core Logic**: Main processing in `app/main.py`
3. **Add A2A API**: Implement required HTTP endpoints
4. **Setup Metrics**: Add Prometheus monitoring
5. **Container Support**: Create Dockerfile and management script
6. **Documentation**: Complete README.md with all required sections
7. **Testing**: Verify all endpoints and functionality

## Common Commands

Commands will be added here as the codebase develops:
- Build commands
- Test commands  
- Lint/typecheck commands
- Development server commands
