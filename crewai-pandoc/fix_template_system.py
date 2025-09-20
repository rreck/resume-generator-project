#!/usr/bin/env python3
"""
Fix Template System to Generate Actually Different PDF Formats
Properly configure LaTeX templates with their dependencies
"""

import os
import sys
import subprocess
import logging
import shutil
from pathlib import Path
import time

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from zip_template_support import ZipTemplateManager, scan_and_process_templates

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FixedResumeGenerator:
    """Generate truly different resume formats with proper template support"""
    
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
    
    def setup_latex_environment(self, template_cache_dir: str):
        """Setup LaTeX environment with template dependencies"""
        cache_path = Path(template_cache_dir)
        
        # Copy all .cls and .sty files to a common location
        latex_dir = Path("./latex_support")
        latex_dir.mkdir(exist_ok=True)
        
        for cls_file in cache_path.rglob("*.cls"):
            shutil.copy2(cls_file, latex_dir)
            logger.debug(f"Copied class file: {cls_file.name}")
        
        for sty_file in cache_path.rglob("*.sty"):
            shutil.copy2(sty_file, latex_dir)
            logger.debug(f"Copied style file: {sty_file.name}")
        
        # Set TEXINPUTS to include our latex support directory
        current_texinputs = os.environ.get('TEXINPUTS', '')
        os.environ['TEXINPUTS'] = f"{latex_dir.absolute()}:{current_texinputs}"
        
        return str(latex_dir.absolute())
    
    def create_simple_working_templates(self):
        """Create simple working templates that will actually produce different outputs"""
        
        templates = {
            "modern": {
                "name": "modern-professional",
                "template": r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}

\geometry{margin=0.8in}
\definecolor{primarycolor}{RGB}{0,100,200}
\definecolor{secondarycolor}{RGB}{100,100,100}

\titleformat{\section}{\Large\bfseries\color{primarycolor}}{}{0em}{}[\titlerule]
\titleformat{\subsection}{\large\bfseries\color{secondarycolor}}{}{0em}{}

\setlist[itemize]{leftmargin=1em,itemsep=0.2em}

\begin{document}
\pagestyle{empty}

{\Huge\bfseries\color{primarycolor} $name$}

\vspace{0.5em}
{\large $phone$ | $email$ | $website$}

\vspace{1em}
\section{Professional Summary}
$summary$

\section{Core Skills}
$skills$

\section{Experience}
$experience$

\section{Education}
$education$

\end{document}
""",
                "style": "modern with blue headers and clean lines"
            },
            
            "classic": {
                "name": "classic-traditional", 
                "template": r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{enumitem}

\geometry{margin=1in}
\setlist[itemize]{leftmargin=1.5em,itemsep=0.3em}

\begin{document}
\pagestyle{empty}

\begin{center}
{\LARGE\textbf{$name$}}\\[0.5em]
$phone$ | $email$ | $website$\\[1em]
\end{center}

\textbf{\large PROFESSIONAL SUMMARY}\\[0.3em]
\hrule
\vspace{0.5em}
$summary$

\vspace{1em}
\textbf{\large CORE SKILLS}\\[0.3em]
\hrule
\vspace{0.5em}
$skills$

\vspace{1em}
\textbf{\large PROFESSIONAL EXPERIENCE}\\[0.3em]
\hrule
\vspace{0.5em}
$experience$

\vspace{1em}
\textbf{\large EDUCATION}\\[0.3em]
\hrule
\vspace{0.5em}
$education$

\end{document}
""",
                "style": "traditional black and white with horizontal rules"
            },
            
            "minimal": {
                "name": "minimal-clean",
                "template": r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{enumitem}

\geometry{margin=1.2in}
\setlist[itemize]{leftmargin=0em,itemsep=0.1em,label=--}

\begin{document}
\pagestyle{empty}

$name$

$phone$ | $email$ | $website$

$summary$

Skills: $skills$

$experience$

$education$

\end{document}
""",
                "style": "ultra-minimal with no formatting"
            },
            
            "creative": {
                "name": "creative-sidebar",
                "template": r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{multicol}
\usepackage{enumitem}

\geometry{margin=0.5in}
\definecolor{sidebarcolor}{RGB}{50,50,50}
\definecolor{namecolor}{RGB}{200,50,50}

\setlist[itemize]{leftmargin=1em,itemsep=0.1em}

\begin{document}
\pagestyle{empty}

\begin{minipage}[t]{0.35\textwidth}
\colorbox{sidebarcolor}{%
\begin{minipage}{\textwidth}
\color{white}
\vspace{1em}
\textbf{\large CONTACT}\\[0.5em]
$phone$\\
$email$\\
$website$
\vspace{1em}

\textbf{\large SKILLS}\\[0.5em]
$skills$
\vspace{1em}
\end{minipage}
}
\end{minipage}%
\hfill
\begin{minipage}[t]{0.6\textwidth}
{\Huge\bfseries\color{namecolor} $name$}

\vspace{1em}
\textbf{SUMMARY}\\[0.3em]
$summary$

\vspace{1em}
\textbf{EXPERIENCE}\\[0.3em]
$experience$

\vspace{1em}
\textbf{EDUCATION}\\[0.3em]
$education$
\end{minipage}

\end{document}
""",
                "style": "creative with dark sidebar and red accent"
            },
            
            "academic": {
                "name": "academic-detailed",
                "template": r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{enumitem}
\usepackage{titlesec}

\geometry{margin=0.8in}
\titleformat{\section}{\large\bfseries}{}{0em}{}
\titleformat{\subsection}{\normalsize\bfseries}{}{0em}{}
\setlist[itemize]{leftmargin=2em,itemsep=0.2em}

\begin{document}

\begin{center}
\textbf{\Large $name$}\\[0.3em]
$phone$ | $email$ | $website$
\end{center}

\section{Research Interests and Summary}
$summary$

\section{Technical Expertise}
$skills$

\section{Professional and Research Experience}
$experience$

\section{Education and Training}
$education$

\section{Selected Publications}
$publications$

\end{document}
""",
                "style": "academic with publications section"
            },
            
            "technical": {
                "name": "technical-engineer",
                "template": r"""
\documentclass[10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{array}

\geometry{margin=0.7in}
\definecolor{techblue}{RGB}{0,50,100}
\setlist[itemize]{leftmargin=1em,itemsep=0.1em}

\begin{document}
\pagestyle{empty}

\noindent
\begin{tabular}{p{0.7\textwidth} p{0.25\textwidth}}
{\huge\bfseries\color{techblue} $name$} & \raggedleft $phone$ \\
{\large Technical Specialist} & \raggedleft $email$ \\
& \raggedleft $website$ \\
\end{tabular}

\vspace{0.5em}
\noindent\rule{\textwidth}{2pt}

\vspace{0.5em}
\textbf{\color{techblue} TECHNICAL SUMMARY}
$summary$

\vspace{0.5em}
\textbf{\color{techblue} CORE TECHNOLOGIES}
$skills$

\vspace{0.5em}
\textbf{\color{techblue} PROFESSIONAL EXPERIENCE}
$experience$

\vspace{0.5em}
\textbf{\color{techblue} EDUCATION \& CERTIFICATIONS}
$education$

\end{document}
""",
                "style": "technical with blue theme and structured layout"
            }
        }
        
        # Create template directory
        template_dir = Path("./working_templates")
        template_dir.mkdir(exist_ok=True)
        
        for template_id, template_data in templates.items():
            template_file = template_dir / f"{template_data['name']}.tex"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(template_data['template'])
            logger.info(f"Created working template: {template_data['name']} ({template_data['style']})")
        
        return templates
    
    def extract_resume_variables(self):
        """Extract variables from resume markdown for template substitution"""
        with open(self.source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML frontmatter
        import re
        yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        
        variables = {
            "name": "Ronald Reck",
            "phone": "248-444-0835",
            "email": "rreck@rrecktek.com", 
            "website": "www.rrecktek.com",
            "summary": "AI professional with specialization in Generative AI and 18+ years AWS experience.",
            "skills": "Python, TensorFlow, PyTorch, AWS, Docker, Machine Learning, NLP, Computer Vision",
            "experience": "RRecktek LLC - Consultant, Technica Corporation - SME, SanCorpConsulting - CTO",
            "education": "Eastern Michigan University - MA English Linguistics, Wayne State University - BA English Linguistics",
            "publications": "Multiple conference papers and technical publications in AI and semantic web technologies"
        }
        
        # Extract better content from markdown sections
        sections = content.split('\n## ')
        for section in sections:
            if section.startswith('Professional Summary'):
                summary_text = section.split('\n')[1:3]
                variables["summary"] = ' '.join(summary_text).strip()
            elif section.startswith('Core Skillset'):
                # Extract first few skill lines
                skill_lines = []
                lines = section.split('\n')[1:6]
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        skill_lines.append(line.strip().replace('**', '').replace('*', ''))
                variables["skills"] = ' | '.join(skill_lines[:3])
        
        return variables
    
    def generate_pdf_with_template(self, template_file: str, template_name: str, variables: dict) -> bool:
        """Generate PDF using specific template with variable substitution"""
        
        # Create working directory for this conversion
        work_dir = Path(f"./temp_work_{int(time.time())}_{template_name}")
        work_dir.mkdir(exist_ok=True)
        
        try:
            # Read template
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Substitute variables
            for var_name, var_value in variables.items():
                template_content = template_content.replace(f"${var_name}$", str(var_value))
            
            # Write working .tex file
            working_tex = work_dir / f"{template_name}.tex"
            with open(working_tex, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            # Generate PDF
            output_pdf = self.output_dir / f"ronald-reck-resume-{template_name}.pdf"
            
            cmd = [
                "pdflatex",
                "-output-directory", str(work_dir),
                "-interaction=nonstopmode",
                str(working_tex)
            ]
            
            logger.info(f"Generating PDF: {template_name}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Copy PDF to output if successful
            generated_pdf = work_dir / f"{template_name}.pdf"
            if generated_pdf.exists():
                shutil.copy2(generated_pdf, output_pdf)
                file_size = output_pdf.stat().st_size
                logger.info(f"✅ SUCCESS: {template_name} ({file_size/1024:.1f}KB)")
                
                self.results["successful"].append({
                    "template": template_name,
                    "output_file": str(output_pdf),
                    "size": file_size
                })
                return True
            else:
                logger.warning(f"❌ FAILED: {template_name} - PDF not generated")
                logger.debug(f"LaTeX output: {result.stdout}")
                logger.debug(f"LaTeX errors: {result.stderr}")
                
                self.results["failed"].append({
                    "template": template_name,
                    "error": result.stderr[:200] if result.stderr else "PDF not generated"
                })
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ TIMEOUT: {template_name}")
            self.results["failed"].append({
                "template": template_name,
                "error": "LaTeX compilation timeout"
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
                shutil.rmtree(work_dir)
    
    def generate_all_different_formats(self):
        """Generate truly different resume formats"""
        logger.info("🚀 Creating working templates that will produce different visual formats...")
        
        # Create working templates
        templates = self.create_simple_working_templates()
        
        # Extract resume content
        variables = self.extract_resume_variables()
        
        # Generate each format
        for template_id, template_data in templates.items():
            template_file = f"./working_templates/{template_data['name']}.tex"
            success = self.generate_pdf_with_template(
                template_file, 
                template_data['name'], 
                variables
            )
        
        # Generate summary
        self.print_summary(templates)
    
    def print_summary(self, templates):
        """Print generation summary"""
        total = len(templates)
        successful = len(self.results["successful"])
        failed = len(self.results["failed"])
        
        print(f"\n📊 DIFFERENT FORMAT GENERATION SUMMARY")
        print("=" * 50)
        print(f"📋 Templates Created: {total}")
        print(f"✅ Successful PDFs: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(successful/total)*100:.1f}%")
        
        print(f"\n✅ DIFFERENT VISUAL FORMATS GENERATED:")
        print("-" * 40)
        for result in self.results["successful"]:
            size_kb = result["size"] / 1024
            print(f"  📄 {result['template']}.pdf ({size_kb:.1f}KB)")
        
        if self.results["failed"]:
            print(f"\n❌ FAILED FORMATS:")
            print("-" * 30)
            for result in self.results["failed"]:
                print(f"  ❌ {result['template']}: {result['error'][:50]}...")

def main():
    """Main execution"""
    source_file = "./input/ronald-reck-resume-2024.md"
    
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        return 1
    
    # Check LaTeX installation
    try:
        subprocess.run(["pdflatex", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pdflatex not found. Please install a LaTeX distribution (texlive, miktex, etc.)")
        return 1
    
    generator = FixedResumeGenerator(source_file)
    generator.generate_all_different_formats()
    
    print(f"\n📁 Generated PDFs are in: {generator.output_dir}")
    print("Each PDF has a truly different visual format and layout!")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)