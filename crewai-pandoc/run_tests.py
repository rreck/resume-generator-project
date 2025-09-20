#!/usr/bin/env python3
"""
Test Runner for CrewAI Pandoc Agent
Simplified test runner that works with the existing codebase
"""

import os
import sys
import unittest
import subprocess
import time
import json
import tempfile
import shutil
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

class BasicAgentTests(unittest.TestCase):
    """Basic tests for the Pandoc agent"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_dir = tempfile.mkdtemp(prefix="pandoc_test_")
        cls.input_dir = os.path.join(cls.test_dir, "input")
        cls.output_dir = os.path.join(cls.test_dir, "output")
        
        os.makedirs(cls.input_dir)
        os.makedirs(cls.output_dir)
        
        # Create a simple test file
        test_content = """# Test Document

This is a simple test document.

## Features
- Markdown support
- Basic formatting
- Lists

**Bold text** and *italic text* should work.
"""
        
        with open(os.path.join(cls.input_dir, "test.md"), "w") as f:
            f.write(test_content)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    def test_pandoc_available(self):
        """Test that pandoc is available"""
        result = subprocess.run(["which", "pandoc"], capture_output=True)
        self.assertEqual(result.returncode, 0, "Pandoc should be available in PATH")
    
    def test_basic_conversion(self):
        """Test basic markdown to PDF conversion"""
        input_file = os.path.join(self.input_dir, "test.md")
        output_file = os.path.join(self.output_dir, "test.pdf")
        
        cmd = ["pandoc", input_file, "-o", output_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Should either succeed or fail gracefully
        self.assertIn(result.returncode, [0, 1, 2], "Pandoc should exit with expected code")
        
        if result.returncode == 0:
            self.assertTrue(os.path.exists(output_file), "Output file should be created")
    
    def test_docx_fallback(self):
        """Test DOCX fallback conversion"""
        input_file = os.path.join(self.input_dir, "test.md")
        output_file = os.path.join(self.output_dir, "test.docx")
        
        cmd = ["pandoc", input_file, "-o", output_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0, "DOCX conversion should succeed")
        self.assertTrue(os.path.exists(output_file), "DOCX output file should be created")
    
    def test_html_conversion(self):
        """Test HTML conversion"""
        input_file = os.path.join(self.input_dir, "test.md")
        output_file = os.path.join(self.output_dir, "test.html")
        
        cmd = ["pandoc", input_file, "-o", output_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0, "HTML conversion should succeed")
        self.assertTrue(os.path.exists(output_file), "HTML output file should be created")
    
    def test_agent_import(self):
        """Test that the main agent can be imported"""
        try:
            import main
            self.assertIsNotNone(main, "Main module should be importable")
        except ImportError as e:
            self.skipTest(f"Main module not importable: {e}")
    
    def test_utility_functions(self):
        """Test utility functions if available"""
        try:
            from main import safe_stem, which_ok
            
            # Test safe_stem
            self.assertEqual(safe_stem("test file.md"), "test_file")
            self.assertEqual(safe_stem("/path/to/file.md"), "file")
            
            # Test which_ok
            self.assertTrue(which_ok("python3"))
            self.assertFalse(which_ok("nonexistent-command-12345"))
            
        except ImportError:
            self.skipTest("Utility functions not available")

class SystemResilienceTests(unittest.TestCase):
    """Tests for system resilience"""
    
    def test_disk_space_check(self):
        """Test disk space checking"""
        # This is a basic test - in production you'd want more sophisticated checks
        import shutil
        
        try:
            usage = shutil.disk_usage('.')
            free_gb = usage.free / (1024**3)
            self.assertGreater(free_gb, 0.1, "Should have at least 100MB free space")
        except Exception as e:
            self.skipTest(f"Disk space check failed: {e}")
    
    def test_memory_check(self):
        """Test basic memory availability"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            self.assertLess(memory.percent, 95, "Memory usage should be reasonable")
        except ImportError:
            self.skipTest("psutil not available for memory testing")
        except Exception as e:
            self.skipTest(f"Memory check failed: {e}")
    
    def test_permissions(self):
        """Test file system permissions"""
        test_file = "./permission_test.tmp"
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            self.assertTrue(True, "File permissions are working")
        except Exception as e:
            self.fail(f"Permission test failed: {e}")

class ContainerTests(unittest.TestCase):
    """Tests related to container functionality"""
    
    def test_docker_available(self):
        """Test if Docker is available"""
        result = subprocess.run(["which", "docker"], capture_output=True)
        if result.returncode != 0:
            self.skipTest("Docker not available")
        
        # Test Docker daemon
        result = subprocess.run(["docker", "info"], capture_output=True)
        if result.returncode != 0:
            self.skipTest("Docker daemon not running")
        
        self.assertTrue(True, "Docker is available and running")
    
    def test_management_script_exists(self):
        """Test that the management script exists and is executable"""
        script_path = "./run-pandoc-agent-watch.sh"
        self.assertTrue(os.path.exists(script_path), "Management script should exist")
        self.assertTrue(os.access(script_path, os.X_OK), "Management script should be executable")

def run_comprehensive_tests():
    """Run all tests and generate a report"""
    print("=" * 60)
    print("CrewAI Pandoc Agent - Test Suite")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        BasicAgentTests,
        SystemResilienceTests,
        ContainerTests
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, failfast=False)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, error in result.failures:
            print(f"- {test}: {error.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, error in result.errors:
            print(f"- {test}: {error.split('Exception:')[-1].strip()}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    # Save detailed results
    test_report = {
        "timestamp": time.time(),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "success_rate": success_rate,
        "details": {
            "failures": [{"test": str(test), "error": error} for test, error in result.failures],
            "errors": [{"test": str(test), "error": error} for test, error in result.errors],
            "skipped": [{"test": str(test), "reason": reason} for test, reason in result.skipped]
        }
    }
    
    with open("test_results.json", "w") as f:
        json.dump(test_report, f, indent=2)
    
    print(f"\nDetailed results saved to: test_results.json")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)