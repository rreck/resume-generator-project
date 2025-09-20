#!/usr/bin/env python3
"""
Enhanced CrewAI Pandoc Agent with Improved Resilience
Supports multiple input formats, enhanced error handling, and better testing
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import signal
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Enhanced input format support
SUPPORTED_INPUT_FORMATS = {
    ".md": "markdown",
    ".markdown": "markdown", 
    ".txt": "plain",
    ".rst": "rst",
    ".tex": "latex",
    ".html": "html",
    ".htm": "html",
    ".docx": "docx",
    ".odt": "odt",
    ".epub": "epub"
}

# Enhanced output format support
SUPPORTED_OUTPUT_FORMATS = {
    "pdf": [".pdf"],
    "docx": [".docx"],
    "html": [".html"],
    "epub": [".epub"],
    "odt": [".odt"],
    "rtf": [".rtf"],
    "latex": [".tex"]
}

# PDF engine configurations with fallback strategies
PDF_ENGINE_CONFIGS = {
    "xelatex": {
        "binary": "xelatex",
        "supports_unicode": True,
        "supports_fontspec": True,
        "memory_limit": "2GB"
    },
    "lualatex": {
        "binary": "lualatex", 
        "supports_unicode": True,
        "supports_fontspec": True,
        "memory_limit": "2GB"
    },
    "pdflatex": {
        "binary": "pdflatex",
        "supports_unicode": False,
        "supports_fontspec": False,
        "memory_limit": "1GB"
    }
}

# Default configuration
DEFAULT_CONFIG = {
    "input_dir": os.environ.get("INPUT_DIR", "./input"),
    "output_dir": os.environ.get("OUTPUT_DIR", "./output"),
    "template_file": os.environ.get("TEMPLATE_FILE", "./app/template.tex"),
    "api_port": int(os.environ.get("API_PORT", "8080")),
    "metrics_port": int(os.environ.get("METRICS_PORT", "9090")),
    "max_workers": int(os.environ.get("MAX_WORKERS", "4")),
    "timeout_seconds": int(os.environ.get("PANDOC_TIMEOUT", "300")),
    "retry_attempts": int(os.environ.get("RETRY_ATTEMPTS", "3")),
    "default_output_format": os.environ.get("DEFAULT_OUTPUT_FORMAT", "pdf")
}

class EnhancedMetrics:
    """Enhanced thread-safe metrics with more detailed tracking"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._metrics = {
            "files_processed_total": 0,
            "files_failed_total": 0,
            "files_skipped_total": 0,
            "files_retried_total": 0,
            "processing_time_seconds_total": 0.0,
            "queue_depth": 0,
            "active_jobs": 0,
            "daemon_uptime_seconds": 0,
            "last_processing_timestamp": 0,
            "memory_usage_bytes": 0,
            "disk_usage_bytes": 0,
            "format_usage": {},
            "engine_usage": {},
            "error_types": {},
            "network_requests_total": 0,
            "api_requests_total": 0
        }
        self._start_time = time.time()
        
        # Initialize format and engine counters
        for fmt in SUPPORTED_INPUT_FORMATS.values():
            self._metrics["format_usage"][fmt] = 0
        for engine in PDF_ENGINE_CONFIGS.keys():
            self._metrics["engine_usage"][engine] = 0
    
    def increment(self, metric: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment metric with optional labels"""
        with self._lock:
            if metric in self._metrics:
                self._metrics[metric] += value
            elif labels and metric in ["format_usage", "engine_usage", "error_types"]:
                for label_key, label_value in labels.items():
                    if metric not in self._metrics:
                        self._metrics[metric] = {}
                    if label_value not in self._metrics[metric]:
                        self._metrics[metric][label_value] = 0
                    self._metrics[metric][label_value] += value
    
    def set_gauge(self, metric: str, value: float):
        """Set gauge metric value"""
        with self._lock:
            self._metrics[metric] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get snapshot of current metrics"""
        with self._lock:
            metrics = self._metrics.copy()
            metrics["daemon_uptime_seconds"] = time.time() - self._start_time
            return metrics

class ResilienceManager:
    """Manages system resilience and recovery"""
    
    def __init__(self):
        self.circuit_breakers = {}
        self.retry_delays = [1, 2, 5, 10, 30]  # Exponential backoff
        
    def check_system_health(self) -> Dict[str, bool]:
        """Comprehensive system health check"""
        health = {
            "disk_space": self._check_disk_space(),
            "memory": self._check_memory(),
            "dependencies": self._check_dependencies(),
            "network": self._check_network(),
            "permissions": self._check_permissions()
        }
        return health
    
    def _check_disk_space(self, min_gb: float = 1.0) -> bool:
        """Check available disk space"""
        try:
            for path in [DEFAULT_CONFIG["input_dir"], DEFAULT_CONFIG["output_dir"]]:
                if os.path.exists(path):
                    stat = shutil.disk_usage(path)
                    free_gb = stat.free / (1024**3)
                    if free_gb < min_gb:
                        return False
            return True
        except Exception:
            return False
    
    def _check_memory(self, max_usage_percent: float = 90.0) -> bool:
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.percent < max_usage_percent
        except ImportError:
            return True  # Assume OK if psutil not available
        except Exception:
            return False
    
    def _check_dependencies(self) -> bool:
        """Check required dependencies"""
        required_binaries = ["pandoc"]
        for binary in required_binaries:
            if not shutil.which(binary):
                return False
        return True
    
    def _check_network(self) -> bool:
        """Check network connectivity"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(("8.8.8.8", 53))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def _check_permissions(self) -> bool:
        """Check file system permissions"""
        try:
            for path in [DEFAULT_CONFIG["input_dir"], DEFAULT_CONFIG["output_dir"]]:
                if os.path.exists(path):
                    test_file = os.path.join(path, ".permission_test")
                    with open(test_file, "w") as f:
                        f.write("test")
                    os.remove(test_file)
            return True
        except Exception:
            return False
    
    @contextmanager
    def retry_with_backoff(self, operation_name: str, max_attempts: int = 3):
        """Context manager for retry with exponential backoff"""
        attempt = 0
        while attempt < max_attempts:
            try:
                yield attempt
                break
            except Exception as e:
                attempt += 1
                if attempt >= max_attempts:
                    raise Exception(f"Operation {operation_name} failed after {max_attempts} attempts: {e}")
                
                delay = self.retry_delays[min(attempt - 1, len(self.retry_delays) - 1)]
                logging.warning(f"Attempt {attempt} for {operation_name} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)

class EnhancedConverter:
    """Enhanced conversion engine with multi-format support"""
    
    def __init__(self, config: Dict[str, Any], metrics: EnhancedMetrics, resilience: ResilienceManager):
        self.config = config
        self.metrics = metrics
        self.resilience = resilience
        self.logger = logging.getLogger(__name__)
    
    def detect_input_format(self, file_path: str) -> str:
        """Auto-detect input format from file extension"""
        ext = Path(file_path).suffix.lower()
        return SUPPORTED_INPUT_FORMATS.get(ext, "markdown")
    
    def determine_output_format(self, input_format: str, requested_format: Optional[str] = None) -> str:
        """Determine best output format based on input and request"""
        if requested_format and requested_format in SUPPORTED_OUTPUT_FORMATS:
            return requested_format
        
        # Smart defaults based on input format
        if input_format in ["latex", "markdown"]:
            return "pdf"
        elif input_format in ["html", "htm"]:
            return "html"
        else:
            return self.config["default_output_format"]
    
    def convert_file(self, 
                    input_path: str, 
                    output_path: str,
                    input_format: Optional[str] = None,
                    output_format: Optional[str] = None,
                    template_path: Optional[str] = None,
                    force: bool = False) -> Tuple[str, Optional[str], str]:
        """Enhanced file conversion with multiple format support"""
        
        start_time = time.time()
        self.metrics.increment("active_jobs")
        
        try:
            # Auto-detect formats if not provided
            if not input_format:
                input_format = self.detect_input_format(input_path)
            if not output_format:
                output_format = self.determine_output_format(input_format)
            
            # Track format usage
            self.metrics.increment("format_usage", labels={"format": input_format})
            
            # Health check before processing
            health = self.resilience.check_system_health()
            if not all(health.values()):
                unhealthy = [k for k, v in health.items() if not v]
                raise Exception(f"System health issues detected: {unhealthy}")
            
            # Attempt conversion with retry logic
            with self.resilience.retry_with_backoff("file_conversion", self.config["retry_attempts"]) as attempt:
                if attempt > 0:
                    self.metrics.increment("files_retried_total")
                
                result = self._perform_conversion(
                    input_path, output_path, input_format, output_format, template_path
                )
                
                # Track successful conversion
                duration = time.time() - start_time
                self.metrics.increment("processing_time_seconds_total", duration)
                self.metrics.increment("files_processed_total")
                self.metrics.set_gauge("last_processing_timestamp", time.time())
                
                return result
                
        except Exception as e:
            self.logger.error(f"Conversion failed for {input_path}: {e}")
            self.metrics.increment("files_failed_total")
            self.metrics.increment("error_types", labels={"error": type(e).__name__})
            return ("FAIL", "", str(e))
        finally:
            self.metrics.increment("active_jobs", -1)
    
    def _perform_conversion(self, 
                          input_path: str, 
                          output_path: str,
                          input_format: str,
                          output_format: str,
                          template_path: Optional[str]) -> Tuple[str, str, str]:
        """Perform the actual conversion"""
        
        # Build pandoc command
        cmd = ["pandoc", input_path, "-f", input_format, "-t", output_format, "-o", output_path]
        
        # Add template if provided and applicable
        if template_path and output_format == "pdf":
            cmd.extend(["--template", template_path])
        
        # PDF-specific engine selection
        if output_format == "pdf":
            engine = self._select_pdf_engine(input_path, input_format, template_path)
            if engine:
                cmd.extend(["--pdf-engine", engine])
                self.metrics.increment("engine_usage", labels={"engine": engine})
        
        # Execute conversion
        self.logger.debug(f"Running command: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config["timeout_seconds"]
            )
            
            if result.returncode == 0:
                return ("OK", output_path, result.stdout)
            else:
                # Try fallback strategies
                fallback_result = self._try_fallback_conversion(input_path, output_path, input_format, result.stderr)
                return fallback_result
        except Exception as e:
            return ("FAIL", "", f"Conversion command failed: {e}")
    
    def _select_pdf_engine(self, input_path: str, input_format: str, template_path: Optional[str]) -> Optional[str]:
        """Intelligently select PDF engine based on content and template"""
        
        # Check for unicode content
        has_unicode = False
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
                has_unicode = any(ord(char) > 127 for char in content)
        except Exception:
            pass
        
        # Check template requirements
        uses_fontspec = False
        if template_path and os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                    uses_fontspec = "fontspec" in template_content
            except Exception:
                pass
        
        # Select engine based on requirements and availability
        preferred_engines = []
        
        if uses_fontspec or has_unicode:
            preferred_engines = ["xelatex", "lualatex", "pdflatex"]
        else:
            preferred_engines = ["pdflatex", "xelatex", "lualatex"]
        
        for engine in preferred_engines:
            if shutil.which(PDF_ENGINE_CONFIGS[engine]["binary"]):
                return engine
        
        return None
    
    def _try_fallback_conversion(self, input_path: str, output_path: str, input_format: str, error_msg: str) -> Tuple[str, str, str]:
        """Try fallback conversion strategies"""
        
        # Strategy 1: Try without template
        try:
            cmd = ["pandoc", input_path, "-f", input_format, "-t", "docx", "-o", output_path.replace(".pdf", ".docx")]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.config["timeout_seconds"])
            if result.returncode == 0:
                return ("DEGRADED", output_path.replace(".pdf", ".docx"), "Converted to DOCX fallback")
        except Exception:
            pass
        
        # Strategy 2: Try HTML output
        try:
            cmd = ["pandoc", input_path, "-f", input_format, "-t", "html", "-o", output_path.replace(".pdf", ".html")]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.config["timeout_seconds"])
            if result.returncode == 0:
                return ("DEGRADED", output_path.replace(".pdf", ".html"), "Converted to HTML fallback")
        except Exception:
            pass
        
            return ("FAIL", "", f"All conversion strategies failed: {error_msg}")

class EnhancedAPIHandler(BaseHTTPRequestHandler):
    """Enhanced API handler with better error handling and features"""
    
    def __init__(self, *args, converter=None, metrics=None, **kwargs):
        self.converter = converter
        self.metrics = metrics
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if self.metrics:
            self.metrics.increment("api_requests_total")
        
        try:
            if path == "/health":
                self._handle_health()
            elif path == "/status":
                self._handle_status()
            elif path == "/config":
                self._handle_config()
            elif path == "/formats":
                self._handle_formats()
            else:
                self._send_error(404, "Endpoint not found")
        except Exception as e:
            self._send_error(500, f"Internal server error: {e}")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if self.metrics:
            self.metrics.increment("api_requests_total")
        
        try:
            data = self._get_json_data()
            
            if path == "/convert":
                self._handle_convert(data)
            elif path == "/batch":
                self._handle_batch(data)
            elif path == "/config":
                self._handle_config_update(data)
            else:
                self._send_error(404, "Endpoint not found")
        except Exception as e:
            self._send_error(500, f"Internal server error: {e}")
    
    def _handle_health(self):
        """Handle health check"""
        resilience = ResilienceManager()
        health = resilience.check_system_health()
        overall_health = "healthy" if all(health.values()) else "unhealthy"
        
        response = {
            "status": overall_health,
            "details": health,
            "timestamp": time.time()
        }
        self._send_json_response(response)
    
    def _handle_status(self):
        """Handle status request"""
        response = {
            "status": "running",
            "metrics": self.metrics.get_metrics() if self.metrics else {},
            "timestamp": time.time()
        }
        self._send_json_response(response)
    
    def _handle_formats(self):
        """Handle supported formats request"""
        response = {
            "input_formats": SUPPORTED_INPUT_FORMATS,
            "output_formats": SUPPORTED_OUTPUT_FORMATS,
            "pdf_engines": PDF_ENGINE_CONFIGS
        }
        self._send_json_response(response)
    
    def _handle_config(self):
        """Handle config request"""
        response = {"config": DEFAULT_CONFIG}
        self._send_json_response(response)
    
    def _handle_batch(self, data: Dict[str, Any]):
        """Handle batch processing request"""
        response = {"status": "batch processing not implemented in enhanced version"}
        self._send_json_response(response)
    
    def _handle_config_update(self, data: Dict[str, Any]):
        """Handle config update request"""
        response = {"status": "config update not implemented in enhanced version"}
        self._send_json_response(response)
    
    def _handle_convert(self, data: Dict[str, Any]):
        """Handle file conversion request"""
        required_fields = ["input_path"]
        if not all(field in data for field in required_fields):
            self._send_error(400, f"Missing required fields: {required_fields}")
            return
        
        input_path = data["input_path"]
        output_path = data.get("output_path")
        input_format = data.get("input_format")
        output_format = data.get("output_format")
        template_path = data.get("template_path")
        force = data.get("force", False)
        
        if not output_path:
            # Generate output path
            base_name = Path(input_path).stem
            ext = SUPPORTED_OUTPUT_FORMATS.get(output_format or "pdf", [".pdf"])[0]
            output_path = f"./output/{int(time.time())}.{base_name}{ext}"
        
        if self.converter:
            status, artifact, message = self.converter.convert_file(
                input_path, output_path, input_format, output_format, template_path, force
            )
        else:
            status, artifact, message = "ERROR", "", "Converter not available"
        
        response = {
            "status": status,
            "input_path": input_path,
            "output_path": artifact,
            "message": message,
            "timestamp": time.time()
        }
        self._send_json_response(response)
    
    def _get_json_data(self) -> Dict[str, Any]:
        """Extract JSON data from POST request"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        
        post_data = self.rfile.read(content_length)
        return json.loads(post_data.decode('utf-8'))
    
    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def _send_error(self, code: int, message: str):
        """Send error response"""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        error_data = {"error": message, "timestamp": time.time()}
        response = json.dumps(error_data)
        self.wfile.write(response.encode('utf-8'))

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup enhanced logging"""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        file_handler = logging.FileHandler('./enhanced_pandoc_agent.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not setup file logging: {e}")
    
    return logger

def main():
    """Enhanced main function"""
    parser = argparse.ArgumentParser(description="Enhanced CrewAI Pandoc Agent")
    parser.add_argument("--input-dir", default=DEFAULT_CONFIG["input_dir"], help="Input directory")
    parser.add_argument("--output-dir", default=DEFAULT_CONFIG["output_dir"], help="Output directory")
    parser.add_argument("--template", default=DEFAULT_CONFIG["template_file"], help="Template file")
    parser.add_argument("--api-port", type=int, default=DEFAULT_CONFIG["api_port"], help="API port")
    parser.add_argument("--metrics-port", type=int, default=DEFAULT_CONFIG["metrics_port"], help="Metrics port")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log level")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode")
    parser.add_argument("--test", action="store_true", help="Run test suite")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    
    # Update configuration
    config = DEFAULT_CONFIG.copy()
    config.update({
        "input_dir": args.input_dir,
        "output_dir": args.output_dir,
        "template_file": args.template,
        "api_port": args.api_port,
        "metrics_port": args.metrics_port
    })
    
    # Initialize components
    metrics = EnhancedMetrics()
    resilience = ResilienceManager()
    converter = EnhancedConverter(config, metrics, resilience)
    
    # Run test suite if requested
    if args.test:
        logger.info("Running enhanced test suite...")
        # Import and run test suite
        try:
            # Import and run test suite
            import sys
            sys.path.append('.')
            from test_suite import run_test_suite
            success = run_test_suite()
            return 0 if success else 1
        except ImportError:
            logger.error("Test suite not found. Please ensure test_suite.py is available.")
            return 1
    
    # Start API server
    logger.info(f"Starting Enhanced Pandoc Agent API on port {config['api_port']}")
    
    def create_handler(*args, **kwargs):
        return EnhancedAPIHandler(*args, converter=converter, metrics=metrics, **kwargs)
    
    server = None
    try:
        server = HTTPServer(('0.0.0.0', config['api_port']), create_handler)
        logger.info("Enhanced Pandoc Agent started successfully")
        logger.info(f"API available at: http://localhost:{config['api_port']}")
        logger.info("Supported endpoints: /health, /status, /formats, /convert, /batch")
        
        if args.daemon:
            logger.info("Running in daemon mode...")
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Shutting down Enhanced Pandoc Agent...")
        if server:
            server.shutdown()
        return 0
    except Exception as e:
        logger.error(f"Failed to start Enhanced Pandoc Agent: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())