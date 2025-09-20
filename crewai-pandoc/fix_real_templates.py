#!/usr/bin/env python3
"""
Fix Real Professional Templates - Make ALL 19 Templates Work
Properly handle .cls files, dependencies, and template-specific requirements
"""

import os
import sys
import subprocess
import logging
import shutil
from pathlib import Path
import time
import re

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from zip_template_support import ZipTemplateManager, scan_and_process_templates

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTemplateGenerator:
    """Make the actual professional templates work with proper dependency handling"""
    
    def __init__(self, source_file: str, output_dir: str = "./output"):
        self.source_file = Path(source_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize template manager
        self.template_manager = scan_and_process_templates("../templates")
        
        # Results tracking
        self.results = {
            "successful": [],
            "failed": [],
            "skipped": []
        }
        
        # Create comprehensive LaTeX environment
        self.setup_comprehensive_latex_environment()
    
    def setup_comprehensive_latex_environment(self):
        """Setup LaTeX environment with ALL template dependencies"""
        # Create centralized LaTeX support directory
        self.latex_support_dir = Path("./comprehensive_latex_support")
        self.latex_support_dir.mkdir(exist_ok=True)
        
        logger.info("🔧 Setting up comprehensive LaTeX environment...")
        
        # Copy ALL .cls, .sty, and other files from all templates
        total_files = 0
        for hash_id, template_info in self.template_manager.template_registry.items():
            cache_path = Path(f"./template_cache/{hash_id}")
            if cache_path.exists():
                # Copy all supporting files
                for pattern in ['*.cls', '*.sty', '*.def', '*.cfg', '*.fd']:
                    for support_file in cache_path.rglob(pattern):
                        dest_file = self.latex_support_dir / support_file.name
                        if not dest_file.exists():  # Don't overwrite
                            shutil.copy2(support_file, dest_file)
                            total_files += 1
                            logger.debug(f"Copied: {support_file.name}")
        
        logger.info(f"📦 Copied {total_files} LaTeX support files")
        
        # Set TEXINPUTS environment variable
        current_texinputs = os.environ.get('TEXINPUTS', '')
        os.environ['TEXINPUTS'] = f".:{self.latex_support_dir.absolute()}:{current_texinputs}"
        
        # Install missing LaTeX packages
        self.install_missing_packages()
    
    def install_missing_packages(self):
        """Install commonly needed LaTeX packages"""
        logger.info("📦 Installing additional LaTeX packages...")
        
        # Common packages needed by professional templates
        packages_to_install = [
            'texlive-fonts-extra',
            'texlive-latex-extra', 
            'texlive-fonts-recommended',
            'texlive-latex-recommended',
            'texlive-xetex',
            'texlive-luatex'
        ]
        
        for package in packages_to_install:
            try:
                result = subprocess.run(['which', 'tlmgr'], capture_output=True)
                if result.returncode == 0:
                    # Use tlmgr if available
                    subprocess.run(['tlmgr', 'install', package.replace('texlive-', '')], 
                                 capture_output=True, timeout=30)
                else:
                    # Try apt-get for Ubuntu/Debian
                    subprocess.run(['sudo', 'apt-get', 'install', '-y', package], 
                                 capture_output=True, timeout=60)
                logger.debug(f"Installed: {package}")
            except Exception as e:
                logger.debug(f"Could not install {package}: {e}")
    
    def fix_template_syntax(self, template_path: str, template_name: str) -> str:
        """Fix common template syntax issues that cause compilation failures"""
        with open(template_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Common fixes for template issues
        fixes_applied = []
        
        # Fix 1: Replace problematic variable syntax
        if '$if(' in content:
            content = re.sub(r'\$if\(([^)]+)\)\$', r'$if(\1)$', content)
            fixes_applied.append("if-syntax")
        
        # Fix 2: Fix variable expansion issues
        content = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)\$', r'$\1$', content)
        
        # Fix 3: Handle special characters in template variables
        content = content.replace('${', '$').replace('}$', '$')
        
        # Fix 4: Add missing documentclass if needed
        if '\\documentclass' not in content and '\\LoadClass' not in content:
            content = '\\documentclass{article}\n' + content
            fixes_applied.append("documentclass")
        
        # Fix 5: Ensure document environment exists
        if '\\begin{document}' not in content:
            # Find where to insert it (after preamble)
            lines = content.split('\n')
            insert_pos = len(lines)
            for i, line in enumerate(lines):
                if line.strip().startswith('\\begin{') and 'document' not in line:
                    insert_pos = i
                    break
            
            lines.insert(insert_pos, '\\begin{document}')
            lines.append('\\end{document}')
            content = '\n'.join(lines)
            fixes_applied.append("document-env")
        
        if fixes_applied:
            logger.debug(f"Applied fixes to {template_name}: {', '.join(fixes_applied)}")
        
        return content
    
    def create_resume_content_for_template(self, template_name: str) -> dict:
        """Create comprehensive resume content variables for templates"""
        
        # Read source markdown
        with open(self.source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract comprehensive variables
        variables = {
            # Basic info
            'name': 'Ronald Reck',
            'firstname': 'Ronald',
            'lastname': 'Reck',
            'title': 'Senior AI Architect & Technical Specialist',
            'phone': '248-444-0835',
            'email': 'rreck@rrecktek.com',
            'website': 'www.rrecktek.com',
            'linkedin': 'linkedin.com/in/ronaldreck',
            'github': 'github.com/rreck',
            'address': 'Clifton, VA 20124',
            'city': 'Clifton',
            'state': 'VA',
            'zip': '20124',
            
            # Professional
            'clearance': 'DoD Top Secret Clearance & FBI Counterintelligence Polygraph',
            'summary': 'AI professional with specialization in Generative AI. Author of commercial ARTIFICIAL INTELLIGENCE software Predictive Analytics Framework. 18+ Years of Amazon Web Services experience. AWS Marketplace publisher of 11 data products.',
            'objective': 'Seeking senior technical role leveraging extensive AI, cloud, and enterprise architecture experience.',
            
            # Skills (different formats for different templates)
            'skills': 'Python • TensorFlow • PyTorch • AWS • Docker • Machine Learning • NLP • Computer Vision • Kubernetes • DevOps',
            'skillslist': 'Python, TensorFlow, PyTorch, langchain, AWS, Docker, Machine Learning, NLP, Computer Vision, Kubernetes, DevOps, Prometheus, Grafana',
            'technical': 'Python, TensorFlow, PyTorch, langchain, AWS (18+ years), Docker, Kubernetes, Machine Learning, NLP, Computer Vision',
            'programming': 'Python, R, Perl, Shell, PHP, SQL, C, JavaScript',
            'platforms': 'AWS, Docker, Kubernetes, Linux, Unix, Windows',
            'ai': 'TensorFlow, PyTorch, langchain, NLP, Computer Vision, Generative AI, LLMs',
            
            # Experience
            'experience': '''Technica Corporation - Subject Matter Expert (2023-Present)
• Service Award within 90 days, FBI global admin with CI-Poly
• Enterprise application support across enclaves

RRecktek LLC - Consultant (2009-Present)  
• 100+ confidential clients including Johnson & Johnson, DHS, DoD
• Designed generative AI for Immigration L-1 Visas using local LLM
• Implemented NLP processing pipelines for multiple domains''',
            
            'job1company': 'Technica Corporation',
            'job1title': 'Subject Matter Expert',
            'job1dates': '2023 - Present',
            'job1description': 'FBI global admin with CI-Poly clearance. Enterprise application support across enclaves.',
            
            'job2company': 'RRecktek LLC',
            'job2title': 'Principal Consultant & Founder',
            'job2dates': '2009 - Present',
            'job2description': '100+ confidential clients. Designed generative AI solutions, NLP pipelines, cloud architecture.',
            
            'job3company': 'SanCorpConsulting',
            'job3title': 'Chief Technology Officer',
            'job3dates': '2020 - 2021',
            'job3description': 'Senior Technology Advisor at DoD Joint Artificial Intelligence Center (JAIC).',
            
            # Education
            'education': '''Eastern Michigan University - Master of Arts, English Linguistics (2007)
Wayne State University - Bachelor of Arts, English Linguistics (1992)''',
            
            'degree1': 'Master of Arts',
            'school1': 'Eastern Michigan University',
            'major1': 'English Linguistics',
            'year1': '2007',
            
            'degree2': 'Bachelor of Arts',
            'school2': 'Wayne State University', 
            'major2': 'English Linguistics',
            'year2': '1992',
            
            # Publications
            'publications': '''Reck, Ronald, Suh, Tong Sun. "Detecting Bias and Prejudice Online: It's Not Just Black and White." KMWorld, 2020.
Reck, Ronald P. "Hardening Linux." McGraw Hill Osborne Media, 2004.''',
            
            # Certifications
            'certifications': 'DoD Security Clearance, AWS Certifications, CyberAwareness Challenge 2021',
            
            # Additional common template variables
            'author': 'Ronald Reck',
            'subject': 'Resume - Ronald Reck',
            'keywords': 'AI, Machine Learning, AWS, Python, DevOps',
            'lang': 'en',
            'geometry': 'margin=1in',
            'fontsize': '11pt',
            'documentclass': 'article',
            
            # Date
            'date': '2024',
            'today': '2024',
            
            # Empty variables for templates that expect them
            'photo': '',
            'quote': '',
            'extrainfo': '',
            'homepage': 'www.rrecktek.com',
            'mobile': '248-444-0835',
            'fax': '',
            'skype': '',
            'twitter': '',
            'facebook': '',
            'instagram': '',
        }
        
        return variables
    
    def try_compilation_with_engines(self, tex_file: str, output_name: str, work_dir: Path) -> tuple[bool, str]:
        """Try compilation with different LaTeX engines"""
        engines = [
            ('xelatex', ['-interaction=nonstopmode', '-output-directory', str(work_dir)]),
            ('lualatex', ['-interaction=nonstopmode', '-output-directory', str(work_dir)]),
            ('pdflatex', ['-interaction=nonstopmode', '-output-directory', str(work_dir)])
        ]
        
        for engine_name, base_args in engines:
            try:
                cmd = [engine_name] + base_args + [str(tex_file)]
                logger.debug(f"Trying {engine_name} for {output_name}")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
                
                # Check if PDF was generated
                pdf_file = work_dir / f"{tex_file.stem}.pdf"
                if pdf_file.exists() and pdf_file.stat().st_size > 1000:  # At least 1KB
                    return True, engine_name
                    
            except subprocess.TimeoutExpired:
                logger.debug(f"{engine_name} timed out for {output_name}")
                continue
            except Exception as e:
                logger.debug(f"{engine_name} failed for {output_name}: {e}")
                continue
        
        return False, "none"
    
    def generate_from_real_template(self, hash_id: str, template_info: dict) -> bool:
        """Generate PDF from real professional template"""
        template_name = Path(template_info['zip_path']).stem
        main_template = template_info.get('main_template')
        
        if not main_template:
            logger.warning(f"⚠️ No main template found for {template_name}")
            return False
        
        cache_path = Path(f"./template_cache/{hash_id}")
        template_path = cache_path / main_template
        
        if not template_path.exists():
            logger.error(f"❌ Template file not found: {template_path}")
            return False
        
        # Create working directory
        work_dir = Path(f"./work_{int(time.time())}_{template_name}")
        work_dir.mkdir(exist_ok=True)
        
        try:
            # Copy entire template directory to working directory for dependencies
            for item in cache_path.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(cache_path)
                    dest_path = work_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)
            
            # Read and fix template
            working_template = work_dir / main_template
            fixed_content = self.fix_template_syntax(str(working_template), template_name)
            
            # Get resume variables
            variables = self.create_resume_content_for_template(template_name)
            
            # Substitute variables in template
            for var_name, var_value in variables.items():
                # Try different variable syntaxes that templates might use
                patterns = [
                    f'${var_name}$',
                    f'#{var_name}#',
                    f'@{var_name}@',
                    f'{{{{ {var_name} }}}}',
                    f'\\var{{{var_name}}}',
                    f'\\{var_name}',
                ]
                
                for pattern in patterns:
                    if pattern in fixed_content:
                        fixed_content = fixed_content.replace(pattern, str(var_value))
            
            # Write the processed template
            with open(working_template, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            logger.info(f"🔄 Compiling: {template_name}")
            
            # Try compilation with different engines
            success, engine = self.try_compilation_with_engines(working_template, template_name, work_dir)
            
            if success:
                # Copy successful PDF to output
                source_pdf = work_dir / f"{working_template.stem}.pdf"
                output_pdf = self.output_dir / f"ronald-reck-resume-{template_name}.pdf"
                
                shutil.copy2(source_pdf, output_pdf)
                file_size = output_pdf.stat().st_size
                
                logger.info(f"✅ SUCCESS: {template_name} with {engine} ({file_size/1024:.1f}KB)")
                
                self.results["successful"].append({
                    "template": template_name,
                    "output_file": str(output_pdf),
                    "size": file_size,
                    "engine": engine,
                    "type": template_info.get('type', 'professional'),
                    "complexity": template_info.get('complexity', 'medium')
                })
                return True
            else:
                logger.warning(f"❌ FAILED: {template_name} - All engines failed")
                self.results["failed"].append({
                    "template": template_name,
                    "error": "All LaTeX engines failed compilation"
                })
                return False
                
        except Exception as e:
            logger.error(f"💥 ERROR: {template_name} - {e}")
            self.results["failed"].append({
                "template": template_name,
                "error": str(e)
            })
            return False
        finally:
            # Cleanup working directory
            if work_dir.exists():
                try:
                    shutil.rmtree(work_dir)
                except:
                    pass  # Don't fail if cleanup fails
    
    def generate_all_real_templates(self):
        """Generate PDFs from all real professional templates"""
        logger.info("🚀 Processing ALL 19 professional resume templates...")
        
        total_templates = len(self.template_manager.template_registry)
        
        for i, (hash_id, template_info) in enumerate(self.template_manager.template_registry.items(), 1):
            template_name = Path(template_info['zip_path']).stem
            logger.info(f"📋 Processing {i}/{total_templates}: {template_name}")
            
            success = self.generate_from_real_template(hash_id, template_info)
            
            # Small delay to prevent system overload
            time.sleep(0.5)
        
        self.print_comprehensive_summary()
    
    def print_comprehensive_summary(self):
        """Print comprehensive generation summary"""
        total = len(self.template_manager.template_registry)
        successful = len(self.results["successful"])
        failed = len(self.results["failed"])
        
        print(f"\n📊 COMPREHENSIVE TEMPLATE GENERATION REPORT")
        print("=" * 60)
        print(f"📋 Total Professional Templates: {total}")
        print(f"✅ Successfully Generated: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(successful/total)*100:.1f}%")
        
        if self.results["successful"]:
            print(f"\n✅ SUCCESSFUL PROFESSIONAL FORMATS:")
            print("-" * 50)
            
            # Group by type
            by_type = {}
            for result in self.results["successful"]:
                template_type = result.get('type', 'professional')
                if template_type not in by_type:
                    by_type[template_type] = []
                by_type[template_type].append(result)
            
            for template_type, templates in by_type.items():
                print(f"\n🎯 {template_type.upper()} TEMPLATES ({len(templates)}):")
                for result in templates:
                    size_kb = result["size"] / 1024
                    complexity = result.get('complexity', 'unknown')
                    engine = result.get('engine', 'unknown')
                    print(f"  📄 {result['template']}.pdf ({size_kb:.1f}KB) [{complexity}, {engine}]")
        
        if self.results["failed"]:
            print(f"\n❌ FAILED TEMPLATES:")
            print("-" * 40)
            for result in self.results["failed"]:
                print(f"  ❌ {result['template']}: {result['error'][:60]}...")
        
        print(f"\n📁 All generated PDFs are in: {self.output_dir}")
        print("🎨 Each PDF has a unique professional design and layout!")

def main():
    """Main execution"""
    source_file = "./input/ronald-reck-resume-2024.md"
    
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        return 1
    
    # Check LaTeX installation
    latex_engines = ['pdflatex', 'xelatex', 'lualatex']
    available_engines = []
    
    for engine in latex_engines:
        try:
            subprocess.run([engine, '--version'], capture_output=True, check=True)
            available_engines.append(engine)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    if not available_engines:
        print("❌ No LaTeX engines found. Please install texlive or miktex.")
        return 1
    
    print(f"✅ Found LaTeX engines: {', '.join(available_engines)}")
    
    generator = RealTemplateGenerator(source_file)
    generator.generate_all_real_templates()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)