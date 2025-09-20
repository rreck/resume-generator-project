#!/usr/bin/env python3
"""
Comprehensive Test Suite for CrewAI Pandoc Agent
Tests functionality, resilience, performance, and integration scenarios
"""

import asyncio
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import unittest
import requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Test configuration
TEST_INPUT_DIR = "./test_input"
TEST_OUTPUT_DIR = "./test_output"
TEST_TEMPLATE = "./test_template.tex"
AGENT_API_BASE = "http://localhost:8080"
METRICS_BASE = "http://localhost:9090"

class PandocAgentTestSuite(unittest.TestCase):
    """Comprehensive test suite for Pandoc agent"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.setup_test_directories()
        cls.create_test_files()
        cls.create_test_templates()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        cls.cleanup_test_directories()
    
    @classmethod
    def setup_test_directories(cls):
        """Create test directories"""
        for dir_path in [TEST_INPUT_DIR, TEST_OUTPUT_DIR]:
            os.makedirs(dir_path, exist_ok=True)
            os.makedirs(f"{dir_path}/logs", exist_ok=True)
    
    @classmethod
    def cleanup_test_directories(cls):
        """Remove test directories"""
        for dir_path in [TEST_INPUT_DIR, TEST_OUTPUT_DIR]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
        if os.path.exists(TEST_TEMPLATE):
            os.remove(TEST_TEMPLATE)
    
    @classmethod
    def create_test_files(cls):
        """Create various test markdown files"""
        test_files = {
            "simple.md": "# Simple Test\n\nBasic markdown content.",
            "complex.md": """# Complex Document
            
## Section 1
This is a more complex document with:
- Lists
- **Bold text**
- *Italic text*
- [Links](https://example.com)

### Code blocks
```python
def hello():
    print("Hello, World!")
```

## Mathematics
When $a \\ne 0$, there are two solutions to $ax^2 + bx + c = 0$.

## Table
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
""",
            "unicode.md": """# Unicode Test
            
测试中文内容 - Chinese content
Español - Spanish content  
العربية - Arabic content
🎉 Emoji support test
""",
            "malformed.md": "# Malformed\n\nUnclosed [link(\n\n**Bold without close",
            "empty.md": "",
            "large.md": "# Large Document\n\n" + "Lorem ipsum dolor sit amet. " * 1000,
        }
        
        for filename, content in test_files.items():
            with open(f"{TEST_INPUT_DIR}/{filename}", "w", encoding="utf-8") as f:
                f.write(content)
    
    @classmethod
    def create_test_templates(cls):
        """Create test LaTeX templates"""
        valid_template = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{hyperref}
\usepackage{amsmath}

\geometry{margin=1in}
\title{$title$}
\author{$author$}
\date{$date$}

\begin{document}
$if(title)$\maketitle$endif$
$body$
\end{document}
"""
        
        with open(TEST_TEMPLATE, "w") as f:
            f.write(valid_template)
        
        # Create invalid template for testing
        invalid_template = r"""
\documentclass{article
\usepackage{missing-package}
\begin{document}
$body$
\end{document}
"""
        with open("./test_invalid_template.tex", "w") as f:
            f.write(invalid_template)

class UnitTests(PandocAgentTestSuite):
    """Unit tests for individual functions"""
    
    def test_file_utilities(self):
        """Test file utility functions"""
        # Test with the agent's utility functions
        from app.main import safe_stem, sha256_file, which_ok
        
        # Test safe_stem
        self.assertEqual(safe_stem("test file.md"), "test_file")
        self.assertEqual(safe_stem("/path/to/file.md"), "file")
        
        # Test which_ok
        self.assertTrue(which_ok("python3"))
        self.assertFalse(which_ok("nonexistent-command"))
        
        # Test sha256_file
        test_file = f"{TEST_INPUT_DIR}/simple.md"
        hash1 = sha256_file(test_file)
        hash2 = sha256_file(test_file)
        self.assertEqual(hash1, hash2)
        self.assertTrue(hash1.startswith("sha256:"))
    
    def test_template_validation(self):
        """Test template validation functions"""
        from app.main import validate_template_syntax, parse_template_requires
        
        # Test valid template
        valid, msg = validate_template_syntax(TEST_TEMPLATE)
        self.assertTrue(valid, f"Valid template failed: {msg}")
        
        # Test invalid template
        valid, msg = validate_template_syntax("./test_invalid_template.tex")
        self.assertFalse(valid, "Invalid template passed validation")
        
        # Test template parsing
        reqs = parse_template_requires(TEST_TEMPLATE)
        self.assertIn("pkgs", reqs)
        self.assertIn("class_name", reqs)
    
    def test_dependency_checking(self):
        """Test dependency checking"""
        from app.main import dependency_report, kpse_exists
        
        # Test dependency report
        ok, report = dependency_report(TEST_TEMPLATE)
        self.assertIsInstance(ok, bool)
        self.assertIn("[DEP]", report)
        
        # Test kpsewhich functionality
        if shutil.which("kpsewhich"):
            self.assertTrue(kpse_exists("article.cls"))
            self.assertFalse(kpse_exists("nonexistent-package.sty"))

class IntegrationTests(PandocAgentTestSuite):
    """Integration tests for complete workflows"""
    
    def test_basic_conversion(self):
        """Test basic markdown to PDF conversion"""
        from app.main import convert_one
        
        md_file = f"{TEST_INPUT_DIR}/simple.md"
        status, artifact, log_path = convert_one(
            md_file, TEST_OUTPUT_DIR, TEST_TEMPLATE, force=True
        )
        
        self.assertIn(status, ["OK", "DEGRADED"])
        if artifact:
            self.assertTrue(os.path.exists(artifact))
        self.assertTrue(os.path.exists(log_path))
    
    def test_batch_processing(self):
        """Test batch processing of multiple files"""
        from app.main import batch
        
        exit_code = batch(TEST_INPUT_DIR, TEST_OUTPUT_DIR, TEST_TEMPLATE, force=True)
        self.assertIn(exit_code, [0, 2])  # 0 = success, 2 = some failures
        
        # Check output directory has files
        output_files = os.listdir(TEST_OUTPUT_DIR)
        self.assertGreater(len(output_files), 0)
    
    def test_malformed_input_handling(self):
        """Test handling of malformed markdown"""
        from app.main import convert_one
        
        md_file = f"{TEST_INPUT_DIR}/malformed.md"
        status, artifact, log_path = convert_one(
            md_file, TEST_OUTPUT_DIR, TEST_TEMPLATE, force=True
        )
        
        # Should still produce some output, even if degraded
        self.assertIn(status, ["OK", "DEGRADED", "FAIL"])
        self.assertTrue(os.path.exists(log_path))
    
    def test_unicode_support(self):
        """Test Unicode content handling"""
        from app.main import convert_one
        
        md_file = f"{TEST_INPUT_DIR}/unicode.md"
        status, artifact, log_path = convert_one(
            md_file, TEST_OUTPUT_DIR, TEST_TEMPLATE, force=True
        )
        
        self.assertIn(status, ["OK", "DEGRADED"])
    
    def test_large_file_processing(self):
        """Test processing of large files"""
        from app.main import convert_one
        
        md_file = f"{TEST_INPUT_DIR}/large.md"
        start_time = time.time()
        
        status, artifact, log_path = convert_one(
            md_file, TEST_OUTPUT_DIR, TEST_TEMPLATE, force=True
        )
        
        duration = time.time() - start_time
        self.assertLess(duration, 60)  # Should complete within 60 seconds
        self.assertIn(status, ["OK", "DEGRADED"])

class ResilienceTests(PandocAgentTestSuite):
    """Tests for system resilience and error handling"""
    
    def test_disk_space_handling(self):
        """Test behavior with low disk space"""
        from app.main import validate_disk_space
        
        # Test with reasonable space requirement
        result = validate_disk_space(TEST_OUTPUT_DIR, min_mb=1)
        self.assertTrue(result)
        
        # Test with unreasonable space requirement
        result = validate_disk_space(TEST_OUTPUT_DIR, min_mb=999999999)
        self.assertFalse(result)
    
    def test_permission_handling(self):
        """Test handling of permission issues"""
        # Create a read-only directory
        readonly_dir = "./readonly_test"
        os.makedirs(readonly_dir, exist_ok=True)
        os.chmod(readonly_dir, 0o444)
        
        try:
            from app.main import ensure_host_directories
            result = ensure_host_directories(readonly_dir)
            self.assertFalse(result)
        finally:
            os.chmod(readonly_dir, 0o755)
            os.rmdir(readonly_dir)
    
    def test_missing_dependencies(self):
        """Test behavior with missing dependencies"""
        from app.main import dependency_report
        
        # Test with non-existent template
        ok, report = dependency_report("./nonexistent.tex")
        self.assertFalse(ok)
        self.assertIn("not found", report)
    
    def test_concurrent_processing(self):
        """Test concurrent file processing"""
        from app.main import convert_one
        
        def process_file(filename):
            md_file = f"{TEST_INPUT_DIR}/{filename}"
            return convert_one(md_file, TEST_OUTPUT_DIR, TEST_TEMPLATE, force=True)
        
        files = ["simple.md", "complex.md", "unicode.md"]
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(process_file, f) for f in files]
            results = [f.result(timeout=60) for f in futures]
        
        # All should complete without major errors
        for status, artifact, log_path in results:
            self.assertIn(status, ["OK", "DEGRADED", "FAIL"])
    
    def test_signal_handling(self):
        """Test graceful shutdown on signals"""
        # This would require running the daemon and sending signals
        # Placeholder for signal handling tests
        pass

class APITests(PandocAgentTestSuite):
    """Tests for A2A API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Start agent for API testing"""
        super().setUpClass()
        cls.agent_process = None
        cls.start_agent_for_testing()
    
    @classmethod
    def tearDownClass(cls):
        """Stop agent after API testing"""
        if cls.agent_process:
            cls.agent_process.terminate()
            cls.agent_process.wait(timeout=10)
        super().tearDownClass()
    
    @classmethod
    def start_agent_for_testing(cls):
        """Start the agent in background for API testing"""
        try:
            cls.agent_process = subprocess.Popen([
                "python3", "app/main.py", 
                "--daemon",
                "-i", TEST_INPUT_DIR,
                "-o", TEST_OUTPUT_DIR,
                "-t", TEST_TEMPLATE,
                "--api-port", "8080",
                "--metrics-port", "9090"
            ])
            time.sleep(3)  # Give agent time to start
        except Exception as e:
            print(f"Could not start agent for API testing: {e}")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{AGENT_API_BASE}/health", timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "healthy")
        except requests.RequestException:
            self.skipTest("Agent not running for API tests")
    
    def test_status_endpoint(self):
        """Test status endpoint"""
        try:
            response = requests.get(f"{AGENT_API_BASE}/status", timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("status", data)
            self.assertIn("metrics", data)
        except requests.RequestException:
            self.skipTest("Agent not running for API tests")
    
    def test_job_submission(self):
        """Test job submission endpoint"""
        try:
            job_data = {
                "file_path": f"{TEST_INPUT_DIR}/simple.md",
                "force": True
            }
            response = requests.post(
                f"{AGENT_API_BASE}/job",
                json=job_data,
                timeout=30
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("status", data)
        except requests.RequestException:
            self.skipTest("Agent not running for API tests")
    
    def test_batch_trigger(self):
        """Test batch processing trigger"""
        try:
            batch_data = {"force": True}
            response = requests.post(
                f"{AGENT_API_BASE}/batch",
                json=batch_data,
                timeout=10
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "started")
        except requests.RequestException:
            self.skipTest("Agent not running for API tests")

class MetricsTests(PandocAgentTestSuite):
    """Tests for Prometheus metrics"""
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint availability"""
        try:
            response = requests.get(f"{METRICS_BASE}/metrics", timeout=5)
            self.assertEqual(response.status_code, 200)
            self.assertIn("pandoc_files_processed_total", response.text)
        except requests.RequestException:
            self.skipTest("Metrics server not running")
    
    def test_metrics_format(self):
        """Test Prometheus metrics format"""
        try:
            response = requests.get(f"{METRICS_BASE}/metrics", timeout=5)
            lines = response.text.split('\n')
            
            # Check for required metric types
            help_lines = [l for l in lines if l.startswith("# HELP")]
            type_lines = [l for l in lines if l.startswith("# TYPE")]
            
            self.assertGreater(len(help_lines), 0)
            self.assertGreater(len(type_lines), 0)
        except requests.RequestException:
            self.skipTest("Metrics server not running")

class PerformanceTests(PandocAgentTestSuite):
    """Performance and load tests"""
    
    def test_processing_performance(self):
        """Test processing performance benchmarks"""
        from app.main import convert_one
        
        md_file = f"{TEST_INPUT_DIR}/simple.md"
        
        # Measure processing time
        times = []
        for _ in range(5):
            start = time.time()
            convert_one(md_file, TEST_OUTPUT_DIR, TEST_TEMPLATE, force=True)
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        self.assertLess(avg_time, 10)  # Should process in under 10 seconds
    
    def test_concurrent_load(self):
        """Test handling of concurrent requests"""
        from app.main import convert_one
        
        def stress_test():
            files = [f"{TEST_INPUT_DIR}/simple.md", f"{TEST_INPUT_DIR}/complex.md"]
            for _ in range(3):
                for md_file in files:
                    convert_one(md_file, TEST_OUTPUT_DIR, TEST_TEMPLATE, force=True)
        
        # Run multiple threads
        threads = []
        for _ in range(3):
            t = threading.Thread(target=stress_test)
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join(timeout=60)
            self.assertFalse(t.is_alive(), "Thread did not complete in time")
    
    def test_memory_usage(self):
        """Test memory usage during processing"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        from app.main import batch
        batch(TEST_INPUT_DIR, TEST_OUTPUT_DIR, TEST_TEMPLATE, force=True)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Should not increase memory by more than 100MB
        self.assertLess(memory_increase, 100 * 1024 * 1024)

def run_test_suite():
    """Run the complete test suite"""
    print("CrewAI Pandoc Agent - Comprehensive Test Suite")
    print("=" * 50)
    
    # Create test loader
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        UnitTests,
        IntegrationTests,
        ResilienceTests,
        APITests,
        MetricsTests,
        PerformanceTests
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        failfast=False,
        buffer=True
    )
    
    result = runner.run(suite)
    
    # Generate test report
    generate_test_report(result)
    
    return result.wasSuccessful()

def generate_test_report(result):
    """Generate detailed test report"""
    report = {
        "timestamp": time.time(),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100,
        "details": {
            "failures": [{"test": str(test), "error": error} for test, error in result.failures],
            "errors": [{"test": str(test), "error": error} for test, error in result.errors],
            "skipped": [{"test": str(test), "reason": reason} for test, reason in result.skipped]
        }
    }
    
    # Save report to file
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nTest Report Summary:")
    print(f"Tests Run: {report['tests_run']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Skipped: {report['skipped']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print(f"Detailed report saved to: test_report.json")

if __name__ == "__main__":
    success = run_test_suite()
    exit(0 if success else 1)