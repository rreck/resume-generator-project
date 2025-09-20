#!/usr/bin/env python3
"""
Generate Ronald Reck's Resume in Multiple Formats
Uses ZIP template system to create various resume versions
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
import time
import json

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from zip_template_support import ZipTemplateManager, scan_and_process_templates

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResumeGenerator:
    """Generate multiple resume formats from Markdown source"""
    
    def __init__(self, source_file: str, output_dir: str = "./output"):
        self.source_file = Path(source_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize template manager
        self.template_manager = scan_and_process_templates("./templates")
        
        # Results tracking
        self.results = {
            "successful": [],
            "failed": [],
            "skipped": []
        }
    
    def run_pandoc_conversion(self, template_hash: str, template_name: str, output_suffix: str = "") -> bool:
        """Run pandoc conversion with specified template"""
        
        # Get template path
        template_path = self.template_manager.get_template_path(template_hash)
        if not template_path:
            logger.error(f"Template path not found for {template_name}")
            return False
        
        # Create output filename
        timestamp = int(time.time())
        base_name = f"ronald-reck-resume-{template_name.lower().replace('_', '-')}"
        if output_suffix:
            base_name += f"-{output_suffix}"
        output_file = self.output_dir / f"{timestamp}.{base_name}.pdf"
        
        # Build pandoc command
        cmd = [
            "pandoc",
            str(self.source_file),
            "-o", str(output_file),
            "--template", template_path,
            "--pdf-engine=xelatex",
            "--variable", "geometry:margin=1in",
            "--variable", "fontsize=11pt",
            "--variable", "documentclass=article"
        ]
        
        try:
            logger.info(f"Generating: {template_name} -> {output_file.name}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"✅ SUCCESS: {template_name}")
                self.results["successful"].append({
                    "template": template_name,
                    "output_file": str(output_file),
                    "size": output_file.stat().st_size if output_file.exists() else 0
                })
                return True
            else:
                logger.warning(f"❌ FAILED: {template_name} - {result.stderr[:200]}")
                self.results["failed"].append({
                    "template": template_name,
                    "error": result.stderr[:500]
                })
                
                # Try fallback with lualatex
                return self.try_fallback_engines(template_path, template_name, output_file)
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ TIMEOUT: {template_name}")
            self.results["failed"].append({
                "template": template_name,
                "error": "Conversion timeout after 60 seconds"
            })
            return False
        except Exception as e:
            logger.error(f"💥 ERROR: {template_name} - {str(e)}")
            self.results["failed"].append({
                "template": template_name,
                "error": str(e)
            })
            return False
    
    def try_fallback_engines(self, template_path: str, template_name: str, output_file: Path) -> bool:
        """Try fallback PDF engines"""
        engines = ["lualatex", "pdflatex"]
        
        for engine in engines:
            try:
                cmd = [
                    "pandoc",
                    str(self.source_file),
                    "-o", str(output_file),
                    "--template", template_path,
                    f"--pdf-engine={engine}",
                    "--variable", "geometry:margin=1in"
                ]
                
                logger.info(f"🔄 Trying {engine} for {template_name}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    logger.info(f"✅ SUCCESS with {engine}: {template_name}")
                    self.results["successful"].append({
                        "template": f"{template_name} ({engine})",
                        "output_file": str(output_file),
                        "size": output_file.stat().st_size if output_file.exists() else 0
                    })
                    return True
                    
            except Exception as e:
                logger.debug(f"Engine {engine} failed for {template_name}: {e}")
                continue
        
        # Try DOCX fallback
        return self.try_docx_fallback(template_name)
    
    def try_docx_fallback(self, template_name: str) -> bool:
        """Try DOCX conversion as ultimate fallback"""
        try:
            timestamp = int(time.time())
            output_file = self.output_dir / f"{timestamp}.ronald-reck-resume-{template_name.lower().replace('_', '-')}.docx"
            
            cmd = [
                "pandoc",
                str(self.source_file),
                "-o", str(output_file)
            ]
            
            logger.info(f"📄 Trying DOCX fallback for {template_name}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"✅ DOCX SUCCESS: {template_name}")
                self.results["successful"].append({
                    "template": f"{template_name} (DOCX)",
                    "output_file": str(output_file),
                    "size": output_file.stat().st_size if output_file.exists() else 0
                })
                return True
                
        except Exception as e:
            logger.debug(f"DOCX fallback failed for {template_name}: {e}")
        
        return False
    
    def generate_simple_templates(self):
        """Generate resumes using simple templates first"""
        simple_templates = []
        
        for hash_id, template_info in self.template_manager.template_registry.items():
            if template_info.get('complexity') == 'simple':
                simple_templates.append((hash_id, Path(template_info['zip_path']).stem))
        
        logger.info(f"🎯 Generating {len(simple_templates)} simple templates...")
        
        for template_hash, template_name in simple_templates:
            self.run_pandoc_conversion(template_hash, template_name, "simple")
    
    def generate_medium_templates(self):
        """Generate resumes using medium complexity templates"""
        medium_templates = []
        
        for hash_id, template_info in self.template_manager.template_registry.items():
            if template_info.get('complexity') == 'medium':
                medium_templates.append((hash_id, Path(template_info['zip_path']).stem))
        
        logger.info(f"🎯 Generating {len(medium_templates)} medium templates...")
        
        for template_hash, template_name in medium_templates:
            self.run_pandoc_conversion(template_hash, template_name, "medium")
    
    def generate_academic_templates(self):
        """Generate resumes using academic templates"""
        academic_templates = []
        
        for hash_id, template_info in self.template_manager.template_registry.items():
            if template_info.get('type') == 'academic':
                academic_templates.append((hash_id, Path(template_info['zip_path']).stem))
        
        logger.info(f"🎯 Generating {len(academic_templates)} academic templates...")
        
        for template_hash, template_name in academic_templates:
            self.run_pandoc_conversion(template_hash, template_name, "academic")
    
    def generate_all_formats(self):
        """Generate resume in all available formats"""
        logger.info("🚀 Starting resume generation in all formats...")
        
        if not self.source_file.exists():
            logger.error(f"Source file not found: {self.source_file}")
            return
        
        # Generate in order of complexity
        self.generate_simple_templates()
        self.generate_medium_templates()
        self.generate_academic_templates()
        
        # Generate complex templates (more likely to fail)
        complex_templates = []
        for hash_id, template_info in self.template_manager.template_registry.items():
            if template_info.get('complexity') == 'complex':
                complex_templates.append((hash_id, Path(template_info['zip_path']).stem))
        
        logger.info(f"🎯 Generating {len(complex_templates)} complex templates...")
        
        for template_hash, template_name in complex_templates:
            self.run_pandoc_conversion(template_hash, template_name, "complex")
    
    def generate_summary_report(self):
        """Generate summary report of all conversions"""
        total_templates = len(self.template_manager.template_registry)
        successful_count = len(self.results["successful"])
        failed_count = len(self.results["failed"])
        
        report = f"""
📊 RESUME GENERATION SUMMARY REPORT
{'='*50}

📁 Source File: {self.source_file}
📂 Output Directory: {self.output_dir}
📋 Total Templates Available: {total_templates}

✅ SUCCESSFUL CONVERSIONS: {successful_count}
❌ FAILED CONVERSIONS: {failed_count}
📈 Success Rate: {(successful_count/total_templates)*100:.1f}%

✅ SUCCESSFUL FORMATS:
{'-'*30}
"""
        
        for result in self.results["successful"]:
            size_mb = result["size"] / (1024*1024) if result["size"] > 0 else 0
            report += f"  • {result['template']} ({size_mb:.1f}MB)\n"
            report += f"    📄 {Path(result['output_file']).name}\n"
        
        if self.results["failed"]:
            report += f"\n❌ FAILED FORMATS:\n{'-'*30}\n"
            for result in self.results["failed"]:
                report += f"  • {result['template']}\n"
                report += f"    💥 {result['error'][:100]}...\n"
        
        # Save report to file
        report_file = self.output_dir / f"resume_generation_report_{int(time.time())}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(report)
        logger.info(f"📋 Report saved to: {report_file}")
        
        return report

def main():
    """Main execution function"""
    # Check if source file exists
    source_file = "./input/ronald-reck-resume-2024.md"
    
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        print("Please ensure the resume markdown file exists.")
        return 1
    
    # Check if pandoc is available
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Pandoc not found. Please install pandoc to generate resumes.")
        return 1
    
    # Initialize generator
    generator = ResumeGenerator(source_file)
    
    # Generate all formats
    generator.generate_all_formats()
    
    # Generate and display summary
    generator.generate_summary_report()
    
    # Show file listing
    print(f"\n📁 Generated files in {generator.output_dir}:")
    try:
        for file in sorted(generator.output_dir.glob("*.pdf")):
            size_mb = file.stat().st_size / (1024*1024)
            print(f"  📄 {file.name} ({size_mb:.1f}MB)")
        
        for file in sorted(generator.output_dir.glob("*.docx")):
            size_mb = file.stat().st_size / (1024*1024)
            print(f"  📄 {file.name} ({size_mb:.1f}MB)")
            
    except Exception as e:
        logger.error(f"Error listing files: {e}")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)