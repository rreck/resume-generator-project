#!/usr/bin/env python3
"""
Professional Resume Generator - Creates visually distinct resumes using real LaTeX templates
Uses cached templates with proper .cls files to generate genuinely different resume formats.
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
import yaml
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResumeGenerator:
    def __init__(self, base_dir="/home/rreck/Desktop/20250920a/crewai-pandoc"):
        self.base_dir = Path(base_dir)
        self.template_cache = self.base_dir / "template_cache"
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Resume content file
        self.resume_md = self.input_dir / "ronald-reck-resume-2024.md"
        
        # Template configurations - mapping cache dirs to template info
        self.template_configs = {
            "25ee69eeb3513355": {
                "name": "AltaCV",
                "main_file": "sample.tex",
                "cls_file": "altacv.cls",
                "description": "Modern timeline-based CV with sidebar",
                "color_scheme": "blue",
                "style": "modern_sidebar"
            },
            "31df2b6577e24288": {
                "name": "Deedy",
                "main_file": "deedy_resume-reversed.tex", 
                "cls_file": "deedy-resume-reversed.cls",
                "description": "Clean two-column professional resume",
                "color_scheme": "navy",
                "style": "two_column"
            },
            "17fdec2b08aa8af0": {
                "name": "SimpleHipster",
                "main_file": "main.tex",
                "cls_file": "simplehipstercv.cls",
                "description": "Creative hipster-style CV with photos",
                "color_scheme": "creative",
                "style": "creative_photo"
            },
            "f155da641c322573": {
                "name": "ModernCV",
                "main_file": "cv-llt.tex",
                "cls_file": "settings.sty",
                "description": "Academic-style CV with publications",
                "color_scheme": "academic",
                "style": "academic"
            },
            "6e657645a8f3ed94": {
                "name": "TwoColumn",
                "main_file": "resume_main.tex",
                "cls_file": "my_cv.cls",
                "description": "Professional two-column resume",
                "color_scheme": "corporate",
                "style": "corporate"
            },
            "3aa6777e6234f515": {
                "name": "Classic",
                "main_file": "resume.tex",
                "cls_file": "resume.cls",
                "description": "Traditional single-column resume",
                "color_scheme": "black",
                "style": "traditional"
            },
            "660e5f8a4587293a": {
                "name": "Elegant",
                "main_file": "resume.tex",
                "cls_file": "resume.cls",
                "description": "Elegant minimalist design",
                "color_scheme": "gray",
                "style": "minimalist"
            },
            "99baef84ac5c20f3": {
                "name": "Professional",
                "main_file": "resume.tex",
                "cls_file": "resume.cls",
                "description": "Professional business resume",
                "color_scheme": "blue",
                "style": "business"
            },
            "524b0634832386ba": {
                "name": "OpenCV",
                "main_file": "cv.tex",
                "cls_file": "OpenCV.cls",
                "description": "OpenCV-style academic resume",
                "color_scheme": "academic_blue",
                "style": "academic_modern"
            },
            "bed320998d939afd": {
                "name": "Modular",
                "main_file": "main.tex",
                "cls_file": None,  # Uses standard article class
                "description": "Modular academic CV",
                "color_scheme": "standard",
                "style": "modular"
            }
        }

    def load_resume_data(self):
        """Load resume data from markdown file with YAML frontmatter"""
        try:
            with open(self.resume_md, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Split frontmatter and content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    markdown_content = parts[2].strip()
                else:
                    frontmatter = {}
                    markdown_content = content
            else:
                frontmatter = {}
                markdown_content = content
                
            return frontmatter, markdown_content
        except Exception as e:
            logger.error(f"Error loading resume data: {e}")
            return {}, ""

    def extract_sections(self, markdown_content):
        """Extract structured sections from markdown"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in markdown_content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line[3:].strip()
                current_content = []
            elif line.startswith('### '):
                current_content.append(line)
            else:
                current_content.append(line)
                
        if current_section:
            sections[current_section] = '\n'.join(current_content)
            
        return sections

    def create_altacv_resume(self, frontmatter, sections, output_dir):
        """Create AltaCV format resume"""
        template_dir = self.template_cache / "25ee69eeb3513355"
        
        # Read the original sample.tex to understand structure
        with open(template_dir / "sample.tex", 'r') as f:
            template_content = f.read()
            
        # Create customized AltaCV resume
        altacv_content = f"""\\documentclass[10pt,a4paper,ragged2e,withhyper]{{altacv}}

\\geometry{{left=1.25cm,right=1.25cm,top=1.5cm,bottom=1.5cm,columnsep=1.2cm}}

\\usepackage{{paracol}}
\\usepackage{{xcolor}}

% Color scheme
\\definecolor{{PrimaryColor}}{{HTML}}{{1976D2}}
\\definecolor{{SecondaryColor}}{{HTML}}{{757575}}
\\definecolor{{AccentColor}}{{HTML}}{{FF5722}}

\\colorlet{{name}}{{black}}
\\colorlet{{tagline}}{{PrimaryColor}}
\\colorlet{{heading}}{{PrimaryColor}}
\\colorlet{{headingrule}}{{PrimaryColor}}
\\colorlet{{subheading}}{{SecondaryColor}}
\\colorlet{{accent}}{{AccentColor}}
\\colorlet{{emphasis}}{{black}}
\\colorlet{{body}}{{black!80!white}}

\\renewcommand{{\\namefont}}{{\\Huge\\rmfamily\\bfseries}}
\\renewcommand{{\\personalinfofont}}{{\\footnotesize}}
\\renewcommand{{\\cvsectionfont}}{{\\LARGE\\rmfamily\\bfseries}}
\\renewcommand{{\\cvsubsectionfont}}{{\\large\\bfseries}}

\\begin{{document}}
\\name{{{frontmatter.get('name', 'Ronald Reck')}}}
\\tagline{{{frontmatter.get('target_role', 'Senior AI Architect')}}}

\\personalinfo{{%
  \\email{{{frontmatter.get('email', 'rreck@rrecktek.com')}}}
  \\phone{{{frontmatter.get('phone', '248-444-0835')}}}
  \\location{{{frontmatter.get('address', 'Clifton, VA 20124')}}}
  \\homepage{{{frontmatter.get('website', 'www.rrecktek.com')}}}
  \\linkedin{{{frontmatter.get('linkedin', 'linkedin.com/in/ronaldreck')}}}
  \\github{{{frontmatter.get('github', 'github.com/rreck')}}}
}}

\\makecvheader
\\AtBeginEnvironment{{tabular}}{{\\small}}

\\columnratio{{0.6}}
\\begin{{paracol}}{{2}}

\\cvsection{{Professional Summary}}
{sections.get('Professional Summary', '').replace('##', '').strip()}

\\cvsection{{Core Skillset}}
{self._format_skills_for_altacv(sections.get('Core Skillset', ''))}

\\cvsection{{Professional Experience}}
{self._format_experience_for_altacv(sections.get('Professional Experience', ''))}

\\switchcolumn

\\cvsection{{Contact Info}}
\\begin{{itemize}}
\\item Security Clearance: {frontmatter.get('clearance', 'Top Secret')}
\\item Years AWS Experience: 18+
\\item AI/ML Specialization: Generative AI
\\end{{itemize}}

\\cvsection{{Education}}
{self._format_education_for_altacv(sections.get('Education', ''))}

\\cvsection{{Recent Certifications}}
{self._format_certs_for_altacv(sections.get('Awards & Certifications', ''))}

\\end{{paracol}}

\\end{{document}}"""

        # Write the customized resume
        output_file = output_dir / "resume_altacv.tex"
        with open(output_file, 'w') as f:
            f.write(altacv_content)
            
        return output_file

    def create_deedy_resume(self, frontmatter, sections, output_dir):
        """Create Deedy format resume"""
        
        deedy_content = f"""\\documentclass[letterpaper]{{deedy-resume-reversed}}
\\usepackage[left=0.75in,top=0.6in,right=0.75in,bottom=0.6in]{{geometry}}

\\begin{{document}}

\\namesection{{{frontmatter.get('name', 'Ronald').split()[0]}}}{{{frontmatter.get('name', 'Ronald Reck').split()[-1]}}}{{
\\urlstyle{{same}}\\href{{mailto:{frontmatter.get('email', 'rreck@rrecktek.com')}}}{{{frontmatter.get('email', 'rreck@rrecktek.com')}}} | {frontmatter.get('phone', '248-444-0835')} | {frontmatter.get('address', 'Clifton, VA')}
}}

\\begin{{minipage}}[t]{{0.33\\textwidth}} 

\\section{{Skills}}
\\subsection{{AI/ML Technologies}}
TensorFlow \\textbullet{{}} PyTorch \\\\
LangChain \\textbullet{{}} Ollama \\\\
Transformers \\textbullet{{}} LLMs \\\\
NLP \\textbullet{{}} Computer Vision \\\\

\\subsection{{Programming}}
Python \\textbullet{{}} R \\textbullet{{}} Perl \\\\
Shell \\textbullet{{}} PHP \\textbullet{{}} SQL \\\\
JavaScript \\textbullet{{}} C \\textbullet{{}} LISP \\\\

\\subsection{{Cloud \\& DevOps}}
AWS (18+ years) \\\\
Docker \\textbullet{{}} Kubernetes \\\\
Prometheus \\textbullet{{}} Grafana \\\\

\\sectionspace

\\section{{Education}}
\\subsection{{Eastern Michigan University}}
\\descript{{MA English Linguistics}}
\\location{{April 2007}}

\\subsection{{Wayne State University}}
\\descript{{BA English Linguistics}}
\\location{{June 1992}}

\\sectionspace

\\section{{Clearance}}
Active DoD Top Secret \\\\
FBI Counterintelligence Polygraph

\\end{{minipage}} 
\\hfill
\\begin{{minipage}}[t]{{0.66\\textwidth}} 

\\section{{Experience}}
\\runsubsection{{Technica Corporation}}
\\descript{{| Subject Matter Expert }}
\\location{{Sep 2023 – Current | FBI}}
\\begin{{tightemize}}
\\item Service Award within 90 days of service
\\item Global admin with CI-Poly clearance
\\item Enterprise application support across enclaves
\\item Designed workflows, ATO, REST automation
\\end{{tightemize}}

\\sectionsep

\\runsubsection{{RRecktek LLC}}
\\descript{{| Consultant }}
\\location{{Sep 2009 – Present | 100+ Clients}}
\\begin{{tightemize}}
\\item Designed generative AI for Immigration L-1 Visas using local LLM
\\item Implemented GAN for luxury brands counterfeit detection
\\item Created NLP processing pipeline for multiple domains
\\item Developed unsupervised categorization for 20k customer segmentation
\\item Built vector-based semantic comparison on 700k news articles
\\end{{tightemize}}

\\sectionsep

\\runsubsection{{SanCorpConsulting}}
\\descript{{| Chief Technology Officer }}
\\location{{May 2020 – June 2021 | DoD JAIC}}
\\begin{{tightemize}}
\\item Senior Technology Advisor in Joint AI Center
\\item Data Science oversight on projects with tens of millions in funding
\\item Designed NLP pipeline for "successful" projects receiving additional funding
\\item Security hardening of R containers in cloud environment
\\end{{tightemize}}

\\sectionsep

\\section{{Recent AI Projects}}
\\begin{{tightemize}}
\\item Advanced customer segmentation using AI
\\item NLP on biomedical research and FAERS compliance
\\item Legal contract NLP/NLU with generative AI
\\item Computer vision using OpenCV machine learning
\\item Language analysis with social network analysis and sentiment detection
\\end{{tightemize}}

\\end{{minipage}} 

\\end{{document}}"""

        output_file = output_dir / "resume_deedy.tex"
        with open(output_file, 'w') as f:
            f.write(deedy_content)
            
        return output_file

    def create_simple_hipster_resume(self, frontmatter, sections, output_dir):
        """Create Simple Hipster CV format"""
        
        hipster_content = f"""\\documentclass[12pt,a4paper]{{simplehipstercv}}

\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{lmodern}}

% Personal Information
\\name{{{frontmatter.get('name', 'Ronald Reck')}}}
\\tagline{{{frontmatter.get('target_role', 'Senior AI Architect & Generative AI Specialist')}}}
\\photo{{}}  % No photo for professional version

\\begin{{document}}

\\makeheader

\\section{{Contact Information}}
\\begin{{itemize}}
\\item Phone: {frontmatter.get('phone', '248-444-0835')}
\\item Email: {frontmatter.get('email', 'rreck@rrecktek.com')}
\\item Location: {frontmatter.get('address', 'Clifton, VA 20124')}
\\item Website: {frontmatter.get('website', 'www.rrecktek.com')}
\\item LinkedIn: {frontmatter.get('linkedin', 'linkedin.com/in/ronaldreck')}
\\item GitHub: {frontmatter.get('github', 'github.com/rreck')}
\\end{{itemize}}

\\section{{Professional Summary}}
{sections.get('Professional Summary', '').replace('##', '').replace('###', '').strip()}

\\section{{Core Technologies}}
\\textbf{{AI/ML:}} TensorFlow, PyTorch, LangChain, Ollama, Transformers, NLP, Computer Vision

\\textbf{{Programming:}} Python, R, Perl, Shell, PHP, SQL, JavaScript, C, LISP

\\textbf{{Cloud:}} AWS (18+ years), Docker, Kubernetes, Prometheus, Grafana

\\textbf{{Databases:}} MySQL, PostgreSQL, MongoDB, Virtuoso, MarkLogic, VectorDB

\\section{{Professional Experience}}
{self._format_experience_simple(sections.get('Professional Experience', ''))}

\\section{{Education}}
{self._format_education_simple(sections.get('Education', ''))}

\\section{{Security Clearance}}
{frontmatter.get('clearance', 'Active DoD Top Secret Clearance & FBI Counterintelligence Polygraph')}

\\end{{document}}"""

        output_file = output_dir / "resume_hipster.tex"
        with open(output_file, 'w') as f:
            f.write(hipster_content)
            
        return output_file

    def _format_skills_for_altacv(self, skills_text):
        """Format skills for AltaCV template"""
        if not skills_text:
            return ""
            
        formatted = ""
        lines = skills_text.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('###'):
                current_category = line[3:].strip()
                formatted += f"\\cvsubsection{{{current_category}}}\n"
            elif line.startswith('**') and line.endswith('**'):
                category = line[2:-2]
                formatted += f"\\cvtag{{{category}}}\n"
            elif line and not line.startswith('#'):
                # Extract technologies from description
                if ':' in line:
                    techs = line.split(':', 1)[1].strip()
                    for tech in techs.split(','):
                        tech = tech.strip()
                        if tech:
                            formatted += f"\\cvtag{{{tech}}}\n"
                            
        return formatted

    def _format_experience_for_altacv(self, exp_text):
        """Format experience for AltaCV template"""
        if not exp_text:
            return ""
            
        formatted = ""
        lines = exp_text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('###'):
                company = line[3:].strip()
                i += 1
                if i < len(lines) and '|' in lines[i]:
                    position_line = lines[i].strip()
                    if '|' in position_line:
                        position, dates = position_line.split('|', 1)
                        position = position.strip('*').strip()
                        dates = dates.strip()
                        
                        formatted += f"\\cvevent{{{position}}}{{{company}}}{{{dates}}}{{}}%\n"
                        
                        # Get description
                        i += 1
                        desc_lines = []
                        while i < len(lines) and not lines[i].strip().startswith('###'):
                            if lines[i].strip().startswith('-'):
                                desc_lines.append(lines[i].strip()[1:].strip())
                            elif lines[i].strip() and not lines[i].strip().startswith('#'):
                                desc_lines.append(lines[i].strip())
                            i += 1
                            
                        if desc_lines:
                            formatted += "\\begin{itemize}\\itemsep1pt\n"
                            for desc in desc_lines[:4]:  # Limit to 4 items
                                if desc:
                                    formatted += f"\\item {desc}\n"
                            formatted += "\\end{itemize}\n"
                        
                        formatted += "\\divider\n"
                        continue
            i += 1
            
        return formatted

    def _format_education_for_altacv(self, edu_text):
        """Format education for AltaCV template"""
        if not edu_text:
            return ""
            
        formatted = ""
        lines = edu_text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###'):
                school = line[3:].strip()
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if '|' in next_line:
                        degree, date = next_line.split('|', 1)
                        degree = degree.strip('*').strip()
                        date = date.strip()
                        formatted += f"\\cvevent{{{degree}}}{{{school}}}{{{date}}}{{}}%\n"
                        
        return formatted

    def _format_certs_for_altacv(self, cert_text):
        """Format certifications for AltaCV template"""
        if not cert_text:
            return ""
            
        formatted = ""
        lines = cert_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') and '2021' in line or '2022' in line or '2023' in line or '2024' in line:
                cert = line[1:].strip()
                formatted += f"\\cvachievement{{\\faCertificate}}{{{cert}}}{{}}%\n"
                
        return formatted

    def _format_experience_simple(self, exp_text):
        """Format experience for simple templates"""
        if not exp_text:
            return ""
            
        formatted = ""
        lines = exp_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('###'):
                company = line[3:].strip()
                formatted += f"\\textbf{{{company}}}\\\\\n"
            elif '|' in line and ('20' in line):
                parts = line.split('|')
                if len(parts) == 2:
                    position = parts[0].strip('*').strip()
                    dates = parts[1].strip()
                    formatted += f"\\textit{{{position}}} \\hfill {dates}\\\\\n"
            elif line.startswith('-'):
                item = line[1:].strip()
                if item:
                    formatted += f"• {item}\\\\\n"
                    
        return formatted

    def _format_education_simple(self, edu_text):
        """Format education for simple templates"""
        if not edu_text:
            return ""
            
        formatted = ""
        lines = edu_text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###'):
                school = line[3:].strip()
                formatted += f"\\textbf{{{school}}}\\\\\n"
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if '|' in next_line:
                        degree, date = next_line.split('|', 1)
                        degree = degree.strip('*').strip()
                        date = date.strip()
                        formatted += f"\\textit{{{degree}}} \\hfill {date}\\\\\n"
                        
        return formatted

    def compile_latex(self, tex_file, template_dir):
        """Compile LaTeX file to PDF"""
        try:
            # Copy template files to working directory
            work_dir = tex_file.parent
            
            # Copy all template files
            for file in template_dir.iterdir():
                if file.is_file() and file.suffix in ['.cls', '.sty', '.png', '.jpg', '.jpeg']:
                    shutil.copy2(file, work_dir)
            
            # Compile
            cmd = ['pdflatex', '-interaction=nonstopmode', str(tex_file)]
            result = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                pdf_file = tex_file.with_suffix('.pdf')
                if pdf_file.exists():
                    logger.info(f"Successfully compiled {tex_file.name}")
                    return pdf_file
                    
            logger.warning(f"Compilation failed for {tex_file.name}: {result.stderr}")
            return None
            
        except Exception as e:
            logger.error(f"Error compiling {tex_file}: {e}")
            return None

    def generate_all_formats(self):
        """Generate all resume formats"""
        frontmatter, markdown_content = self.load_resume_data()
        sections = self.extract_sections(markdown_content)
        
        generated_resumes = []
        
        # Create output directory for this run
        timestamp = "2024_distinct_formats"
        output_dir = self.output_dir / timestamp
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Generating resumes in {output_dir}")
        
        # Generate AltaCV format
        try:
            template_dir = self.template_cache / "25ee69eeb3513355"
            if template_dir.exists():
                tex_file = self.create_altacv_resume(frontmatter, sections, output_dir)
                pdf_file = self.compile_latex(tex_file, template_dir)
                if pdf_file:
                    generated_resumes.append(("AltaCV", pdf_file))
        except Exception as e:
            logger.error(f"Error generating AltaCV: {e}")
        
        # Generate Deedy format
        try:
            template_dir = self.template_cache / "31df2b6577e24288"
            if template_dir.exists():
                tex_file = self.create_deedy_resume(frontmatter, sections, output_dir)
                pdf_file = self.compile_latex(tex_file, template_dir)
                if pdf_file:
                    generated_resumes.append(("Deedy", pdf_file))
        except Exception as e:
            logger.error(f"Error generating Deedy: {e}")
            
        # Generate Simple Hipster format
        try:
            template_dir = self.template_cache / "17fdec2b08aa8af0"
            if template_dir.exists():
                tex_file = self.create_simple_hipster_resume(frontmatter, sections, output_dir)
                pdf_file = self.compile_latex(tex_file, template_dir)
                if pdf_file:
                    generated_resumes.append(("SimpleHipster", pdf_file))
        except Exception as e:
            logger.error(f"Error generating SimpleHipster: {e}")
        
        # Generate more formats...
        # TODO: Add remaining templates
        
        logger.info(f"Generated {len(generated_resumes)} distinct resume formats")
        for name, pdf in generated_resumes:
            logger.info(f"  - {name}: {pdf}")
            
        return generated_resumes

if __name__ == "__main__":
    generator = ResumeGenerator()
    resumes = generator.generate_all_formats()
    
    print(f"Generated {len(resumes)} distinct resume formats:")
    for name, pdf_path in resumes:
        print(f"  {name}: {pdf_path}")