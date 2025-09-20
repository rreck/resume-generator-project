#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Copyright (c) RRECKTEK LLC
# Project: CrewAI Pandoc Agent
# Version: 1.1.0
# Built: @EPOCH
#
# Purpose:
#   Convert input/*.md -> output/@EPOCH.<stem>.pdf using Pandoc + LaTeX template.
#   - Preflight TeX deps (kpsewhich, biber/bibtex, fonts via fc-list)
#   - Engine fallbacks: xelatex -> lualatex -> pdflatex -> (no template) -> DOCX
#   - Checksum-as-UUID for dedupe (job_key = sha256(md) + sha256(template or none))
#   - Epoch-stamped filenames and per-file logs under output/logs/
#   - Foreground watch mode and daemon mode support
#   - Agent-to-Agent (A2A) HTTP API for remote job control
#   - Prometheus metrics endpoint for monitoring
#   - Enhanced template validation and error checking
#
# Exit codes:
#   0 = all good / no work
#   1 = general error
#   2 = at least one file failed
#   3 = daemon startup failed
# -----------------------------------------------------------------------------

import argparse
import atexit
import daemon
import daemon.pidfile
import hashlib
import json
import logging
import logging.handlers
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Tuple, Optional, Any
from urllib.parse import urlparse, parse_qs
import socket

# ---- Defaults (overridden by CLI or env) -------------------------------------

DEFAULT_INPUT = os.environ.get("INPUT_DIR", "./input")
DEFAULT_OUTPUT = os.environ.get("OUTPUT_DIR", "./output")
DEFAULT_TEMPLATE = os.environ.get("TEMPLATE_FILE", "./app/template.tex")
DEFAULT_PIDFILE = os.environ.get("PIDFILE", "/var/run/pandoc-agent.pid")
DEFAULT_METRICS_PORT = int(os.environ.get("METRICS_PORT", "9090"))
DEFAULT_API_PORT = int(os.environ.get("API_PORT", "8080"))
PDF_ENGINES = ["xelatex", "lualatex", "pdflatex"]
PANDOC_TIMEOUT_SEC = 300

# ---- Global state for metrics and daemon control ----------------------------

class AgentMetrics:
    """Thread-safe metrics collection for Prometheus export"""
    def __init__(self):
        self._lock = threading.Lock()
        self._metrics = {
            'files_processed_total': 0,
            'files_failed_total': 0,
            'files_skipped_total': 0,
            'files_degraded_total': 0,  # DOCX fallback
            'processing_time_seconds_total': 0.0,
            'queue_depth': 0,
            'template_validation_failures_total': 0,
            'daemon_uptime_seconds': 0,
            'last_processing_timestamp': 0,
            'active_jobs': 0,
            'engine_usage': {'xelatex': 0, 'lualatex': 0, 'pdflatex': 0, 'docx_fallback': 0}
        }
        self._start_time = time.time()

    def increment(self, metric: str, value: float = 1.0):
        """Thread-safe metric increment"""
        with self._lock:
            if metric in self._metrics:
                self._metrics[metric] += value

    def set_gauge(self, metric: str, value: float):
        """Thread-safe gauge setting"""
        with self._lock:
            self._metrics[metric] = value

    def get_metrics(self) -> Dict[str, Any]:
        """Get snapshot of current metrics"""
        with self._lock:
            metrics = self._metrics.copy()
            metrics['daemon_uptime_seconds'] = time.time() - self._start_time
            return metrics

# Global metrics instance
METRICS = AgentMetrics()

# Daemon control
SHUTDOWN_EVENT = threading.Event()

# ---- Logging setup -----------------------------------------------------------

def setup_logging(daemon_mode: bool = False, log_level: str = "INFO"):
    """Configure logging for both file and syslog (in daemon mode)"""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Always log to file
    try:
        file_handler = logging.FileHandler('/var/log/pandoc-agent.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (PermissionError, FileNotFoundError):
        # Fallback to local log file if /var/log not writable
        file_handler = logging.FileHandler('./pandoc-agent.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    if daemon_mode:
        # Add syslog handler for daemon mode
        try:
            syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
            syslog_formatter = logging.Formatter('pandoc-agent: %(levelname)s - %(message)s')
            syslog_handler.setFormatter(syslog_formatter)
            logger.addHandler(syslog_handler)
        except Exception as e:
            logger.warning(f"Could not setup syslog handler: {e}")
    else:
        # Add console handler for non-daemon mode
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

# ---- Directory and validation utilities --------------------------------------

def ensure_host_directories(*paths) -> bool:
    """
    Create directories on host with proper error checking.
    Returns True if all directories exist/created successfully.
    """
    logger = logging.getLogger(__name__)
    success = True
    
    for path in paths:
        try:
            os.makedirs(path, exist_ok=True)
            # Test write permissions
            test_file = os.path.join(path, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            logger.info(f"Directory verified: {path}")
        except PermissionError:
            logger.error(f"Permission denied creating/writing to directory: {path}")
            success = False
        except OSError as e:
            logger.error(f"OS error creating directory {path}: {e}")
            success = False
        except Exception as e:
            logger.error(f"Unexpected error with directory {path}: {e}")
            success = False
    
    return success

def validate_disk_space(path: str, min_mb: int = 100) -> bool:
    """Check if path has minimum disk space available"""
    logger = logging.getLogger(__name__)
    try:
        stat = shutil.disk_usage(path)
        free_mb = stat.free // (1024 * 1024)
        if free_mb < min_mb:
            logger.warning(f"Low disk space in {path}: {free_mb}MB free (minimum {min_mb}MB)")
            return False
        return True
    except Exception as e:
        logger.error(f"Error checking disk space for {path}: {e}")
        return False

# ---- Small utils (enhanced) --------------------------------------------------

def epoch() -> int:
    return int(time.time())

def sha256_file(path: str) -> str:
    """Compute SHA256 hash of file with error handling"""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return f"sha256:{h.hexdigest()}"
    except Exception as e:
        logging.getLogger(__name__).error(f"Error hashing file {path}: {e}")
        return f"sha256:error-{epoch()}"

def sha256_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"

def safe_stem(path: str) -> str:
    stem = os.path.splitext(os.path.basename(path))[0]
    return "".join(c if (c.isalnum() or c in "-_.") else "_" for c in stem)

def which_ok(cmd: str) -> bool:
    return shutil.which(cmd) is not None

def run(cmd: List[str], timeout: int = PANDOC_TIMEOUT_SEC) -> Tuple[bool, str]:
    """Run a command; return (ok, combined_output). Never raises."""
    logger = logging.getLogger(__name__)
    try:
        logger.debug(f"Running command: {' '.join(cmd)}")
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            check=False,
        )
        return (p.returncode == 0, p.stdout)
    except subprocess.TimeoutExpired as e:
        out = e.stdout or ""
        logger.warning(f"Command timeout after {timeout}s: {' '.join(cmd)}")
        return (False, out + "\n[TIMEOUT]")
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        return (False, f"[ERROR: {e}]")

def log_append(logf: str, text: str):
    """Append text to log file with error handling"""
    try:
        with open(logf, "a", encoding="utf-8") as f:
            f.write(text)
            if not text.endswith("\n"):
                f.write("\n")
    except Exception as e:
        logging.getLogger(__name__).error(f"Error writing to log file {logf}: {e}")

# ---- Enhanced template dependency analysis -----------------------------------

PKG_RE = re.compile(r'\\(?:usepackage|RequirePackage)(?:\[[^\]]*\])?\{([^}]+)\}')
CLS_RE = re.compile(r'\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}')
BIBSTYLE_RE = re.compile(r'\\bibliographystyle\{([^}]+)\}')
FONTDEF_RE = re.compile(r'\\set(?:main|sans|mono)font\{([^}]+)\}')

def kpse_exists(texname: str) -> bool:
    """Check if TeX package/class exists using kpsewhich"""
    if not which_ok("kpsewhich"):
        return False
    ok, out = run(["kpsewhich", texname], timeout=20)
    return ok and out.strip() != ""

def fc_has_font(font_family: str) -> bool:
    """Check if font family is available via fontconfig"""
    if not which_ok("fc-list"):
        return True  # can't verify; don't block
    ok, out = run(["fc-list", ":", "family"], timeout=20)
    if not ok:
        return True
    target = font_family.lower()
    return any(target in ln.lower() for ln in out.splitlines())

def validate_template_syntax(tex_path: str) -> Tuple[bool, str]:
    """Enhanced template syntax validation"""
    logger = logging.getLogger(__name__)
    
    if not os.path.isfile(tex_path):
        return False, f"Template file not found: {tex_path}"
    
    try:
        with open(tex_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        return False, f"Template file encoding error: {tex_path}"
    except Exception as e:
        return False, f"Error reading template: {e}"
    
    issues = []
    
    # Check for balanced braces
    brace_count = content.count("{") - content.count("}")
    if brace_count != 0:
        issues.append(f"Unbalanced braces (difference: {brace_count})")
    
    # Check for required document structure
    if "\\documentclass" not in content:
        issues.append("Missing \\documentclass")
    if "\\begin{document}" not in content and "\\documentclass" in content:
        issues.append("Missing \\begin{document}")
    if "\\end{document}" not in content and "\\begin{document}" in content:
        issues.append("Missing \\end{document}")
    
    # Check for common problematic patterns
    if "\\usepackage{" in content and "}" not in content[content.find("\\usepackage{"):]:
        issues.append("Malformed \\usepackage command")
    
    if issues:
        METRICS.increment('template_validation_failures_total')
        return False, f"Template syntax issues: {'; '.join(issues)}"
    
    return True, "Template syntax validation passed"

def parse_template_requires(tex_path: str):
    """Parse template requirements with enhanced validation"""
    try:
        with open(tex_path, "r", encoding="utf-8") as f:
            s = f.read()
    except Exception as e:
        logging.getLogger(__name__).error(f"Error parsing template {tex_path}: {e}")
        return {}
    
    pkgs = []
    for m in PKG_RE.finditer(s):
        for p in m.group(1).split(","):
            p = p.strip()
            if p:
                pkgs.append(p)
    
    cls = CLS_RE.search(s)
    uses_biblatex = any(p.lower() == "biblatex" for p in pkgs)
    fontspec = any(p.lower() == "fontspec" for p in pkgs)
    fonts = FONTDEF_RE.findall(s) if fontspec else []
    
    return dict(
        class_name=(cls.group(1).strip() if cls else None),
        pkgs=sorted(set(pkgs)),
        uses_biblatex=uses_biblatex,
        uses_bibtex_style=(BIBSTYLE_RE.search(s) is not None),
        fontspec=fontspec,
        fonts=sorted(set(fonts)),
    )

def dependency_report(tex_path: str) -> Tuple[bool, str]:
    """Enhanced dependency checking with template validation"""
    logger = logging.getLogger(__name__)
    
    # First validate template syntax
    syntax_ok, syntax_msg = validate_template_syntax(tex_path)
    if not syntax_ok:
        logger.error(f"Template validation failed: {syntax_msg}")
        return False, f"[DEP] {syntax_msg}"
    
    if not which_ok("kpsewhich"):
        return False, "[DEP] missing kpsewhich (install TeX Live tools)"

    r = parse_template_requires(tex_path)
    if not r:  # Parse failed
        return False, "[DEP] Failed to parse template requirements"
    
    missing, notes = [], []

    # Check document class
    if r["class_name"] and not kpse_exists(r["class_name"] + ".cls"):
        missing.append(f"class:{r['class_name']} (.cls not found)")
    
    # Check packages
    for p in r["pkgs"]:
        if not kpse_exists(p + ".sty"):
            missing.append(f"package:{p} (.sty not found)")
    
    # Check bibliography tools
    if r["uses_biblatex"] and not which_ok("biber"):
        missing.append("binary:biber required by biblatex")
    if r["uses_bibtex_style"] and not which_ok("bibtex"):
        missing.append("binary:bibtex required by bibliographystyle")
    
    # Check fonts and engines for fontspec
    if r["fontspec"]:
        if not which_ok("xelatex") and not which_ok("lualatex"):
            notes.append("fontspec present but xelatex/lualatex missing")
        for fam in r["fonts"]:
            if not fc_has_font(fam):
                notes.append(f"font:{fam} not found via fontconfig (fc-list)")

    ok = len(missing) == 0
    lines = ["[DEP] Template analysis:"]
    lines.append(f"  syntax: {syntax_msg}")
    lines.append(f"  class: {r['class_name'] or '—'}")
    lines.append(f"  packages: {', '.join(r['pkgs']) or '—'}")
    if r["uses_biblatex"]:
        lines.append("  biblatex: yes")
    if r["uses_bibtex_style"]:
        lines.append("  bibtex style: yes")
    if r["fontspec"]:
        lines.append(f"  fontspec: yes; fonts={', '.join(r['fonts']) or '—'}")
    if missing:
        lines.append("  MISSING:"); lines += [f"    - {m}" for m in missing]
    if notes:
        lines.append("  NOTES:"); lines += [f"    - {n}" for n in notes]
    
    return ok, "\n".join(lines)

# ---- Conversion core (enhanced with metrics) ---------------------------------

def try_pandoc_pdf(md_path: str, out_pdf: str, engine: str, template_file: Optional[str], logf: str) -> bool:
    """Try PDF conversion with specified engine"""
    cmd = ["pandoc", md_path, "-o", out_pdf, f"--pdf-engine={engine}"]
    if template_file:
        cmd.append(f"--template={template_file}")
    
    start_time = time.time()
    ok, out = run(cmd)
    duration = time.time() - start_time
    
    METRICS.increment('processing_time_seconds_total', duration)
    if ok:
        with METRICS._lock:
            METRICS._metrics['engine_usage'][engine] += 1
    
    log_append(logf, f"=== CMD ===\n{' '.join(cmd)}\n=== OUTPUT ===\n{out}\n=== RESULT === {'OK' if ok else 'FAIL'} ({duration:.2f}s)\n")
    return ok

def try_docx(md_path: str, out_docx: str, logf: str) -> bool:
    """Try DOCX fallback conversion"""
    cmd = ["pandoc", md_path, "-o", out_docx]
    start_time = time.time()
    ok, out = run(cmd)
    duration = time.time() - start_time
    
    METRICS.increment('processing_time_seconds_total', duration)
    if ok:
        with METRICS._lock:
            METRICS._metrics['engine_usage']['docx_fallback'] += 1
    
    log_append(logf, f"=== DOCX FALLBACK ===\n{' '.join(cmd)}\n=== OUTPUT ===\n{out}\n=== RESULT === {'OK' if ok else 'FAIL'} ({duration:.2f}s)\n")
    return ok

def compute_job_key(md_path: str, template_file: Optional[str]) -> str:
    """Compute unique job key for deduplication"""
    md_cid = sha256_file(md_path)
    tpl_cid = sha256_file(template_file) if (template_file and os.path.isfile(template_file)) else "sha256:0"*8
    return sha256_bytes((md_cid + "|" + tpl_cid).encode("utf-8"))

def already_done(cache_dir: str, job_key: str) -> Optional[str]:
    """Return artifact path if job_key cached, else None."""
    idx = os.path.join(cache_dir, f"{job_key}.done")
    if os.path.isfile(idx):
        try:
            with open(idx, "r", encoding="utf-8") as f:
                p = f.read().strip()
            return p if p else None
        except Exception:
            return None
    return None

def mark_done(cache_dir: str, job_key: str, artifact_path: str):
    """Mark job as completed in cache"""
    try:
        with open(os.path.join(cache_dir, f"{job_key}.done"), "w", encoding="utf-8") as f:
            f.write(artifact_path)
    except Exception as e:
        logging.getLogger(__name__).error(f"Error writing cache file: {e}")

def convert_one(
    md_path: str,
    output_dir: str,
    template_file: Optional[str],
    force: bool = False,
) -> Tuple[str, Optional[str], str]:
    """
    Convert a Markdown file to PDF (or DOCX fallback).
    Returns (status, artifact_path_or_None, log_path):
      status in {"OK","DEGRADED","FAIL","SKIP"}
    """
    logger = logging.getLogger(__name__)
    METRICS.increment('active_jobs')
    
    try:
        stem = safe_stem(md_path)
        logs_dir = os.path.join(output_dir, "logs")
        cache_dir = os.path.join(logs_dir, "jobcache")
        
        if not ensure_host_directories(logs_dir, cache_dir):
            METRICS.increment('files_failed_total')
            return ("FAIL", None, "")

        logf = os.path.join(logs_dir, f"{epoch()}.{stem}.log")
        job_key = compute_job_key(md_path, template_file)

        logger.info(f"Processing {md_path} -> job_key={job_key}")

        # Dedupe/skip if cached and not forced
        if not force:
            prior = already_done(cache_dir, job_key)
            if prior and os.path.isfile(prior):
                log_append(logf, f"SKIP: cached job_key {job_key}; artifact={prior}")
                METRICS.increment('files_skipped_total')
                return ("SKIP", prior, logf)

        # Check disk space
        if not validate_disk_space(output_dir):
            log_append(logf, "FAIL: insufficient disk space")
            METRICS.increment('files_failed_total')
            return ("FAIL", None, logf)

        # Reproducibility-ish
        os.environ["SOURCE_DATE_EPOCH"] = str(epoch())

        # Preflight dependencies
        if template_file and os.path.isfile(template_file):
            dep_ok, dep_txt = dependency_report(template_file)
            log_append(logf, dep_txt)
            if not dep_ok:
                log_append(logf, "[DEP] Missing dependencies; will attempt fallbacks.")

        # Strategy 1: engines + template
        if template_file and os.path.isfile(template_file):
            for eng in PDF_ENGINES:
                if not which_ok(eng):
                    continue
                pdf_out = os.path.join(output_dir, f"{epoch()}.{stem}.pdf")
                if try_pandoc_pdf(md_path, pdf_out, eng, template_file, logf):
                    mark_done(cache_dir, job_key, pdf_out)
                    # record artifact cid
                    with open(pdf_out, "rb") as f: 
                        art_cid = sha256_bytes(f.read())
                    log_append(logf, f"[ARTIFACT] pdf={pdf_out} cid={art_cid}")
                    logger.info(f"Successfully converted {md_path} using {eng}")
                    METRICS.increment('files_processed_total')
                    METRICS.set_gauge('last_processing_timestamp', time.time())
                    return ("OK", pdf_out, logf)

        # Strategy 2: engines without template
        for eng in PDF_ENGINES:
            if not which_ok(eng):
                continue
            pdf_out2 = os.path.join(output_dir, f"{epoch()}.{stem}.pdf")
            if try_pandoc_pdf(md_path, pdf_out2, eng, None, logf):
                log_append(logf, "NOTE: succeeded after dropping template")
                mark_done(cache_dir, job_key, pdf_out2)
                with open(pdf_out2, "rb") as f: 
                    art_cid = sha256_bytes(f.read())
                log_append(logf, f"[ARTIFACT] pdf={pdf_out2} cid={art_cid}")
                logger.info(f"Successfully converted {md_path} using {eng} (no template)")
                METRICS.increment('files_processed_total')
                METRICS.set_gauge('last_processing_timestamp', time.time())
                return ("OK", pdf_out2, logf)

        # Strategy 3: DOCX fallback
        docx_out = os.path.join(output_dir, f"{epoch()}.{stem}.docx")
        if try_docx(md_path, docx_out, logf):
            mark_done(cache_dir, job_key, docx_out)
            with open(docx_out, "rb") as f: 
                art_cid = sha256_bytes(f.read())
            log_append(logf, f"[ARTIFACT] docx={docx_out} cid={art_cid}")
            logger.warning(f"Converted {md_path} to DOCX fallback")
            METRICS.increment('files_degraded_total')
            METRICS.set_gauge('last_processing_timestamp', time.time())
            return ("DEGRADED", docx_out, logf)

        log_append(logf, "FATAL: all conversion strategies failed")
        logger.error(f"Failed to convert {md_path}")
        METRICS.increment('files_failed_total')
        return ("FAIL", None, logf)
        
    finally:
        METRICS.increment('active_jobs', -1)

# ---- Batch / Watch / Daemon --------------------------------------------------

def list_markdown(input_dir: str) -> List[str]:
    """List all markdown files in input directory"""
    try:
        files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith(".md")]
        files.sort()
        return files
    except FileNotFoundError:
        logging.getLogger(__name__).warning(f"Input directory not found: {input_dir}")
        return []
    except Exception as e:
        logging.getLogger(__name__).error(f"Error listing markdown files: {e}")
        return []

def batch(input_dir: str, output_dir: str, template_file: Optional[str], force: bool) -> int:
    """Process all markdown files in input directory once"""
    logger = logging.getLogger(__name__)
    files = list_markdown(input_dir)
    
    if not files:
        logger.info("No .md files found in input/")
        return 0
    
    METRICS.set_gauge('queue_depth', len(files))
    summary = {"OK":0, "DEGRADED":0, "FAIL":0, "SKIP":0}
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=min(4, len(files))) as executor:
        futures = []
        for md in files:
            future = executor.submit(convert_one, md, output_dir, template_file, force)
            futures.append((md, future))
        
        for md, future in futures:
            try:
                st, art, logf = future.result(timeout=PANDOC_TIMEOUT_SEC + 60)
                summary[st] += 1
                print(f"{st}\t{md}\t{art or ''}\t{logf}")
                logger.info(f"Batch result: {st} for {md}")
            except Exception as e:
                summary["FAIL"] += 1
                logger.error(f"Batch processing error for {md}: {e}")
                print(f"FAIL\t{md}\t\terror")
    
    METRICS.set_gauge('queue_depth', 0)
    logger.info(f"Batch complete: {summary}")
    return 0 if summary["FAIL"] == 0 else 2

def watch(input_dir: str, output_dir: str, template_file: Optional[str], sleep_sec: int, force: bool):
    """Watch mode - continuously monitor input directory"""
    logger = logging.getLogger(__name__)
    logger.info(f"[watch] scanning every {sleep_sec}s — Ctrl-C to stop")
    
    while not SHUTDOWN_EVENT.is_set():
        try:
            batch(input_dir, output_dir, template_file, force)
            
            # Sleep with early exit on shutdown
            for _ in range(max(1, sleep_sec)):
                if SHUTDOWN_EVENT.is_set():
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Watch mode interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error in watch loop: {e}")
            time.sleep(5)  # Brief pause on errors

def daemon_main(input_dir: str, output_dir: str, template_file: Optional[str], sleep_sec: int, force: bool):
    """Main daemon loop"""
    logger = logging.getLogger(__name__)
    logger.info("Daemon mode started")
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        SHUTDOWN_EVENT.set()
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        watch(input_dir, output_dir, template_file, sleep_sec, force)
    except Exception as e:
        logger.error(f"Daemon error: {e}")
        return 1
    
    logger.info("Daemon shutdown complete")
    return 0

# ---- Prometheus metrics server -----------------------------------------------

class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics endpoint"""
    
    def do_GET(self):
        """Handle GET requests for metrics"""
        if self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            
            metrics = METRICS.get_metrics()
            
            # Format metrics in Prometheus exposition format
            output = []
            output.append("# HELP pandoc_files_processed_total Total number of files successfully processed")
            output.append("# TYPE pandoc_files_processed_total counter")
            output.append(f"pandoc_files_processed_total {metrics['files_processed_total']}")
            
            output.append("# HELP pandoc_files_failed_total Total number of files that failed processing")
            output.append("# TYPE pandoc_files_failed_total counter")
            output.append(f"pandoc_files_failed_total {metrics['files_failed_total']}")
            
            output.append("# HELP pandoc_files_skipped_total Total number of files skipped (cached)")
            output.append("# TYPE pandoc_files_skipped_total counter")
            output.append(f"pandoc_files_skipped_total {metrics['files_skipped_total']}")
            
            output.append("# HELP pandoc_files_degraded_total Total number of files converted to DOCX fallback")
            output.append("# TYPE pandoc_files_degraded_total counter")
            output.append(f"pandoc_files_degraded_total {metrics['files_degraded_total']}")
            
            output.append("# HELP pandoc_processing_time_seconds_total Total processing time in seconds")
            output.append("# TYPE pandoc_processing_time_seconds_total counter")
            output.append(f"pandoc_processing_time_seconds_total {metrics['processing_time_seconds_total']:.2f}")
            
            output.append("# HELP pandoc_queue_depth Current number of files in processing queue")
            output.append("# TYPE pandoc_queue_depth gauge")
            output.append(f"pandoc_queue_depth {metrics['queue_depth']}")
            
            output.append("# HELP pandoc_template_validation_failures_total Total template validation failures")
            output.append("# TYPE pandoc_template_validation_failures_total counter")
            output.append(f"pandoc_template_validation_failures_total {metrics['template_validation_failures_total']}")
            
            output.append("# HELP pandoc_daemon_uptime_seconds Agent uptime in seconds")
            output.append("# TYPE pandoc_daemon_uptime_seconds gauge")
            output.append(f"pandoc_daemon_uptime_seconds {metrics['daemon_uptime_seconds']:.2f}")
            
            output.append("# HELP pandoc_last_processing_timestamp Last file processing timestamp")
            output.append("# TYPE pandoc_last_processing_timestamp gauge")
            output.append(f"pandoc_last_processing_timestamp {metrics['last_processing_timestamp']}")
            
            output.append("# HELP pandoc_active_jobs Current number of active processing jobs")
            output.append("# TYPE pandoc_active_jobs gauge")
            output.append(f"pandoc_active_jobs {metrics['active_jobs']}")
            
            # Engine usage metrics
            output.append("# HELP pandoc_engine_usage_total Total usage count by engine")
            output.append("# TYPE pandoc_engine_usage_total counter")
            for engine, count in metrics['engine_usage'].items():
                output.append(f'pandoc_engine_usage_total{{engine="{engine}"}} {count}')
            
            response = "\n".join(output) + "\n"
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def log_message(self, format, *args):
        """Override to use proper logging"""
        logging.getLogger(__name__).info(f"Metrics request: {format % args}")

def start_metrics_server(port: int = DEFAULT_METRICS_PORT):
    """Start Prometheus metrics HTTP server in background thread"""
    logger = logging.getLogger(__name__)
    
    def run_server():
        try:
            server = HTTPServer(('0.0.0.0', port), MetricsHandler)
            logger.info(f"Metrics server started on port {port}")
            server.serve_forever()
        except Exception as e:
            logger.error(f"Metrics server error: {e}")
    
    metrics_thread = threading.Thread(target=run_server, daemon=True)
    metrics_thread.start()
    return metrics_thread

# ---- Agent-to-Agent (A2A) API server ----------------------------------------

class A2AHandler(BaseHTTPRequestHandler):
    """HTTP handler for Agent-to-Agent communication API"""
    
    def do_GET(self):
        """Handle GET requests for status and queries"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        if path == "/status":
            self.send_json_response({
                "status": "running",
                "metrics": METRICS.get_metrics(),
                "timestamp": time.time()
            })
        elif path == "/health":
            self.send_json_response({"status": "healthy"})
        elif path == "/config":
            # Return current configuration
            config = {
                "input_dir": getattr(self.server, 'input_dir', 'unknown'),
                "output_dir": getattr(self.server, 'output_dir', 'unknown'),
                "template_file": getattr(self.server, 'template_file', None),
            }
            self.send_json_response(config)
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def do_POST(self):
        """Handle POST requests for job submission and configuration"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
        except Exception as e:
            self.send_error_response(400, f"Invalid JSON: {e}")
            return
        
        if path == "/job":
            # Process specific file
            result = self.handle_job_request(data)
            self.send_json_response(result)
        elif path == "/batch":
            # Trigger batch processing
            result = self.handle_batch_request(data)
            self.send_json_response(result)
        elif path == "/config":
            # Update configuration
            result = self.handle_config_update(data)
            self.send_json_response(result)
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def handle_job_request(self, data: dict) -> dict:
        """Handle individual job processing request"""
        logger = logging.getLogger(__name__)
        
        required_fields = ['file_path']
        if not all(field in data for field in required_fields):
            return {"error": "Missing required fields", "required": required_fields}
        
        file_path = data['file_path']
        force = data.get('force', False)
        
        # Validate file exists and is markdown
        if not os.path.isfile(file_path) or not file_path.lower().endswith('.md'):
            return {"error": "Invalid markdown file", "file_path": file_path}
        
        try:
            output_dir = getattr(self.server, 'output_dir', DEFAULT_OUTPUT)
            template_file = getattr(self.server, 'template_file', None)
            
            # Process the file
            status, artifact, log_path = convert_one(file_path, output_dir, template_file, force)
            
            logger.info(f"A2A job request processed: {file_path} -> {status}")
            
            return {
                "status": status,
                "file_path": file_path,
                "artifact_path": artifact,
                "log_path": log_path,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"A2A job processing error: {e}")
            return {"error": str(e), "file_path": file_path}
    
    def handle_batch_request(self, data: dict) -> dict:
        """Handle batch processing request"""
        logger = logging.getLogger(__name__)
        
        try:
            input_dir = data.get('input_dir', getattr(self.server, 'input_dir', DEFAULT_INPUT))
            output_dir = getattr(self.server, 'output_dir', DEFAULT_OUTPUT)
            template_file = getattr(self.server, 'template_file', None)
            force = data.get('force', False)
            
            # Run batch in background thread to avoid blocking
            def run_batch():
                return batch(input_dir, output_dir, template_file, force)
            
            batch_thread = threading.Thread(target=run_batch)
            batch_thread.start()
            
            logger.info(f"A2A batch request triggered for {input_dir}")
            
            return {
                "status": "started",
                "message": "Batch processing started in background",
                "input_dir": input_dir,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"A2A batch request error: {e}")
            return {"error": str(e)}
    
    def handle_config_update(self, data: dict) -> dict:
        """Handle configuration update request"""
        logger = logging.getLogger(__name__)
        
        try:
            updated_fields = []
            
            if 'template_file' in data:
                template_file = data['template_file']
                if template_file and os.path.isfile(template_file):
                    # Validate template
                    syntax_ok, msg = validate_template_syntax(template_file)
                    if syntax_ok:
                        self.server.template_file = template_file
                        updated_fields.append('template_file')
                    else:
                        return {"error": f"Template validation failed: {msg}"}
                else:
                    self.server.template_file = None
                    updated_fields.append('template_file (cleared)')
            
            logger.info(f"A2A config updated: {updated_fields}")
            
            return {
                "status": "updated",
                "updated_fields": updated_fields,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"A2A config update error: {e}")
            return {"error": str(e)}
    
    def send_json_response(self, data: dict):
        """Send JSON response"""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def send_error_response(self, code: int, message: str):
        """Send error response"""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        error_data = {"error": message, "timestamp": time.time()}
        response = json.dumps(error_data)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use proper logging"""
        logging.getLogger(__name__).info(f"A2A API request: {format % args}")

def start_a2a_server(port: int = DEFAULT_API_PORT, **server_config):
    """Start A2A API HTTP server in background thread"""
    logger = logging.getLogger(__name__)
    
    def run_server():
        try:
            server = HTTPServer(('0.0.0.0', port), A2AHandler)
            # Pass configuration to server for handlers to access
            for key, value in server_config.items():
                setattr(server, key, value)
            
            logger.info(f"A2A API server started on port {port}")
            server.serve_forever()
        except Exception as e:
            logger.error(f"A2A API server error: {e}")
    
    api_thread = threading.Thread(target=run_server, daemon=True)
    api_thread.start()
    return api_thread

# ---- PID file management -----------------------------------------------------

@contextmanager
def pid_file_manager(pidfile_path: str):
    """Context manager for PID file creation and cleanup"""
    logger = logging.getLogger(__name__)
    
    try:
        # Check if PID file exists and process is running
        if os.path.exists(pidfile_path):
            try:
                with open(pidfile_path, 'r') as f:
                    old_pid = int(f.read().strip())
                
                # Check if process is still running
                try:
                    os.kill(old_pid, 0)  # Send signal 0 to check if process exists
                    logger.error(f"Daemon already running with PID {old_pid}")
                    raise SystemExit(3)
                except ProcessLookupError:
                    # Process doesn't exist, remove stale PID file
                    os.remove(pidfile_path)
                    logger.info(f"Removed stale PID file: {pidfile_path}")
            except (ValueError, FileNotFoundError):
                # Invalid or missing PID file
                pass
        
        # Create PID file
        pid = os.getpid()
        with open(pidfile_path, 'w') as f:
            f.write(str(pid))
        logger.info(f"Created PID file: {pidfile_path} (PID: {pid})")
        
        # Setup cleanup on exit
        def cleanup_pid():
            try:
                if os.path.exists(pidfile_path):
                    os.remove(pidfile_path)
                    logger.info(f"Removed PID file: {pidfile_path}")
            except Exception as e:
                logger.error(f"Error removing PID file: {e}")
        
        atexit.register(cleanup_pid)
        
        yield
        
    except Exception as e:
        logger.error(f"PID file management error: {e}")
        raise
    finally:
        # Cleanup handled by atexit
        pass

# ---- CLI and main entry point ------------------------------------------------

def main() -> int:
    """Main entry point with enhanced CLI options"""
    ap = argparse.ArgumentParser(
        description="CrewAI Pandoc Agent with daemon mode, A2A messaging, and Prometheus metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # One-shot batch processing
  python main.py -i ./input -o ./output

  # Foreground watch mode
  python main.py -w -s 5

  # Daemon mode with custom ports
  python main.py --daemon --metrics-port 9090 --api-port 8080

  # Force re-render with template validation
  python main.py -f -t ./custom-template.tex

A2A API Endpoints:
  GET  /status      - Get agent status and metrics
  GET  /health      - Health check
  GET  /config      - Get current configuration
  POST /job         - Process specific file {"file_path": "path.md", "force": false}
  POST /batch       - Trigger batch processing {"input_dir": "path", "force": false}
  POST /config      - Update configuration {"template_file": "path.tex"}

Metrics available at http://localhost:9090/metrics (Prometheus format)
        """
    )
    
    # Core options
    ap.add_argument("-i","--input", default=DEFAULT_INPUT, 
                    help="input directory (Markdown files)")
    ap.add_argument("-o","--output", default=DEFAULT_OUTPUT, 
                    help="output directory (PDFs/logs)")
    ap.add_argument("-t","--template", default=DEFAULT_TEMPLATE, 
                    help="LaTeX template .tex file (optional)")
    
    # Mode options
    ap.add_argument("-w","--watch", action="store_true", 
                    help="foreground watch mode")
    ap.add_argument("--daemon", action="store_true", 
                    help="daemon mode (background service)")
    ap.add_argument("-s","--sleep", type=int, default=5, 
                    help="seconds between scans in watch/daemon mode")
    ap.add_argument("-f","--force", action="store_true", 
                    help="force re-render (ignore dedupe cache)")
    
    # Service options
    ap.add_argument("--pidfile", default=DEFAULT_PIDFILE, 
                    help="PID file path for daemon mode")
    ap.add_argument("--metrics-port", type=int, default=DEFAULT_METRICS_PORT,
                    help="Prometheus metrics server port")
    ap.add_argument("--api-port", type=int, default=DEFAULT_API_PORT,
                    help="A2A API server port")
    ap.add_argument("--log-level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                    default='INFO', help="logging level")
    
    args = ap.parse_args()

    # Validate conflicting modes
    if args.watch and args.daemon:
        print("ERROR: Cannot use both --watch and --daemon modes simultaneously", file=sys.stderr)
        return 1

    # Setup logging
    setup_logging(daemon_mode=args.daemon, log_level=args.log_level)
    logger = logging.getLogger(__name__)

    # Sanity check: required binaries
    if not which_ok("pandoc"):
        logger.error("pandoc not found in PATH")
        return 2
    if not any(which_ok(e) for e in PDF_ENGINES):
        logger.warning("No TeX engines found; only DOCX fallback may work")

    # Create and validate directories
    if not ensure_host_directories(args.input, args.output, os.path.join(args.output, "logs")):
        logger.error("Failed to create or access required directories")
        return 2

    # Validate template if provided
    template_file = None
    if args.template and os.path.isfile(args.template):
        syntax_ok, syntax_msg = validate_template_syntax(args.template)
        if syntax_ok:
            template_file = args.template
            logger.info(f"Template validated: {args.template}")
        else:
            logger.error(f"Template validation failed: {syntax_msg}")
            if not args.force:
                logger.error("Use --force to proceed with invalid template")
                return 2
            else:
                logger.warning("Proceeding with invalid template due to --force")
                template_file = args.template
    elif args.template:
        logger.warning(f"Template file not found: {args.template}")

    # Start metrics server
    logger.info(f"Starting metrics server on port {args.metrics_port}")
    metrics_thread = start_metrics_server(args.metrics_port)

    # Start A2A API server
    logger.info(f"Starting A2A API server on port {args.api_port}")
    api_thread = start_a2a_server(
        args.api_port,
        input_dir=args.input,
        output_dir=args.output,
        template_file=template_file
    )

    # Mode selection
    try:
        if args.daemon:
            logger.info("Starting daemon mode")
            with pid_file_manager(args.pidfile):
                # Create daemon context
                with daemon.DaemonContext(
                    pidfile=daemon.pidfile.TimeoutPIDLockFile(args.pidfile),
                    detach_process=True,
                ):
                    # Re-setup logging after daemonization
                    setup_logging(daemon_mode=True, log_level=args.log_level)
                    return daemon_main(args.input, args.output, template_file, args.sleep, args.force)
        
        elif args.watch:
            logger.info("Starting watch mode")
            watch(args.input, args.output, template_file, args.sleep, args.force)
            return 0
        
        else:
            logger.info("Starting batch mode")
            return batch(args.input, args.output, template_file, args.force)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())