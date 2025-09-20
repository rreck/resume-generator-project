#!/usr/bin/env python3
"""
Professional Resume Generator - Creates visually distinct resumes
Creates multiple resume formats that are actually different in layout and style.
"""

import os
import sys
import yaml
import shutil
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DistinctResumeGenerator:
    def __init__(self, base_dir="/home/rreck/Desktop/20250920a/crewai-pandoc"):
        self.base_dir = Path(base_dir)
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Resume content file
        self.resume_md = self.input_dir / "ronald-reck-resume-2024.md"

    def load_resume_data(self):
        """Load resume data from markdown file with YAML frontmatter"""
        try:
            with open(self.resume_md, 'r', encoding='utf-8') as f:
                content = f.read()
                
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
            else:
                current_content.append(line)
                
        if current_section:
            sections[current_section] = '\n'.join(current_content)
            
        return sections

    def create_modern_sidebar_resume(self, frontmatter, sections, output_dir):
        """Create a modern sidebar resume (AltaCV-inspired)"""
        content = f"""\\documentclass[10pt,a4paper]{{article}}
\\usepackage[left=0.5in,right=4in,top=0.5in,bottom=0.5in]{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{fontawesome}}
\\usepackage{{tikz}}
\\usepackage{{enumitem}}
\\usepackage{{multicol}}

% Define colors
\\definecolor{{primary}}{{RGB}}{{25, 118, 210}}
\\definecolor{{secondary}}{{RGB}}{{117, 117, 117}}
\\definecolor{{accent}}{{RGB}}{{255, 87, 34}}

\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}

\\begin{{document}}

% Sidebar
\\begin{{tikzpicture}}[remember picture,overlay]
\\fill[primary] (current page.north west) rectangle ([xshift=3.5in]current page.south west);
\\end{{tikzpicture}}

% Main content area
\\hspace{{3.7in}}
\\begin{{minipage}}[t]{{4.3in}}
\\vspace{{0.5in}}

{{\\Huge \\textbf{{{frontmatter.get('name', 'Ronald Reck')}}}}}

\\vspace{{0.2in}}
{{\\Large \\color{{primary}} {frontmatter.get('target_role', 'Senior AI Architect')}}}

\\vspace{{0.3in}}
\\textbf{{\\color{{secondary}} Professional Summary}}
\\vspace{{0.1in}}

{self._clean_text(sections.get('Professional Summary', ''))}

\\vspace{{0.3in}}
\\textbf{{\\color{{secondary}} Professional Experience}}
\\vspace{{0.1in}}

{self._format_experience_compact(sections.get('Professional Experience', ''))}

\\end{{minipage}}

% Sidebar content
\\begin{{tikzpicture}}[remember picture,overlay]
\\node[anchor=north west, text=white] at ([xshift=0.3in,yshift=-0.5in]current page.north west) {{
\\begin{{minipage}}[t]{{3in}}

\\textbf{{\\Large Contact}}
\\vspace{{0.2in}}

\\faPhone\\, {frontmatter.get('phone', '248-444-0835')}

\\faEnvelope\\, {frontmatter.get('email', 'rreck@rrecktek.com')}

\\faMapMarker\\, {frontmatter.get('address', 'Clifton, VA 20124')}

\\faGlobe\\, {frontmatter.get('website', 'www.rrecktek.com')}

\\faLinkedin\\, {frontmatter.get('linkedin', 'linkedin.com/in/ronaldreck')}

\\faGithub\\, {frontmatter.get('github', 'github.com/rreck')}

\\vspace{{0.4in}}
\\textbf{{\\Large Skills}}
\\vspace{{0.2in}}

\\textbf{{AI/ML}}
\\begin{{itemize}}[leftmargin=*,noitemsep]
\\item TensorFlow, PyTorch
\\item LangChain, Ollama  
\\item NLP, Computer Vision
\\item Generative AI
\\end{{itemize}}

\\textbf{{Programming}}
\\begin{{itemize}}[leftmargin=*,noitemsep]
\\item Python, R, Perl
\\item Shell, PHP, SQL
\\item JavaScript, C
\\end{{itemize}}

\\textbf{{Cloud}}
\\begin{{itemize}}[leftmargin=*,noitemsep]
\\item AWS (18+ years)
\\item Docker, Kubernetes
\\item Prometheus, Grafana
\\end{{itemize}}

\\vspace{{0.4in}}
\\textbf{{\\Large Security}}
\\vspace{{0.2in}}

{frontmatter.get('clearance', 'Active DoD Top Secret Clearance & FBI Counterintelligence Polygraph')}

\\vspace{{0.4in}}
\\textbf{{\\Large Education}}
\\vspace{{0.2in}}

{self._format_education_sidebar(sections.get('Education', ''))}

\\end{{minipage}}
}};
\\end{{tikzpicture}}

\\end{{document}}"""

        output_file = output_dir / "resume_modern_sidebar.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_two_column_resume(self, frontmatter, sections, output_dir):
        """Create a two-column professional resume"""
        content = f"""\\documentclass[10pt,letterpaper]{{article}}
\\usepackage[left=0.75in,right=0.75in,top=0.75in,bottom=0.75in]{{geometry}}
\\usepackage{{multicol}}
\\usepackage{{xcolor}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}

\\definecolor{{headercolor}}{{RGB}}{{52, 73, 94}}
\\definecolor{{accentcolor}}{{RGB}}{{41, 128, 185}}

\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}

% Custom section formatting
\\titleformat{{\\section}}{{\\large\\bfseries\\color{{headercolor}}}}{{}}{{0em}}{{}}[\\titlerule]
\\titlespacing*{{\\section}}{{0pt}}{{1.5ex plus 1ex minus .2ex}}{{1.3ex plus .2ex}}

\\begin{{document}}

% Header
\\begin{{center}}
{{\\Huge\\bfseries {frontmatter.get('name', 'Ronald Reck')}}}

\\vspace{{0.1in}}
{{\\large\\color{{accentcolor}} {frontmatter.get('target_role', 'Senior AI Architect & Generative AI Specialist')}}}

\\vspace{{0.1in}}
{frontmatter.get('phone', '248-444-0835')} \\textbullet\\, {frontmatter.get('email', 'rreck@rrecktek.com')} \\textbullet\\, {frontmatter.get('address', 'Clifton, VA 20124')}

{frontmatter.get('website', 'www.rrecktek.com')} \\textbullet\\, {frontmatter.get('linkedin', 'linkedin.com/in/ronaldreck')} \\textbullet\\, {frontmatter.get('github', 'github.com/rreck')}
\\end{{center}}

\\vspace{{0.2in}}

\\begin{{multicols}}{{2}}

\\section{{Professional Summary}}
{self._clean_text(sections.get('Professional Summary', ''))}

\\section{{Core Technologies}}
\\textbf{{AI/ML:}} TensorFlow, PyTorch, LangChain, Ollama, Transformers, NLP, Computer Vision

\\textbf{{Programming:}} Python, R, Perl, Shell, PHP, SQL, JavaScript, C, LISP

\\textbf{{Cloud:}} AWS (18+ years), Docker, Kubernetes, Prometheus, Grafana

\\textbf{{Databases:}} MySQL, PostgreSQL, MongoDB, Virtuoso, MarkLogic, VectorDB

\\columnbreak

\\section{{Security Clearance}}
{frontmatter.get('clearance', 'Active DoD Top Secret Clearance & FBI Counterintelligence Polygraph')}

\\section{{Education}}
{self._format_education_simple(sections.get('Education', ''))}

\\section{{Recent AI Projects}}
\\begin{{itemize}}[noitemsep]
\\item Advanced customer segmentation (AI)
\\item NLP on biomedical research and FAERS compliance  
\\item Legal contract NLP/NLU (generative AI)
\\item Computer vision using OpenCV (machine learning)
\\item Language analysis with sentiment detection (AI)
\\end{{itemize}}

\\end{{multicols}}

\\section{{Professional Experience}}
{self._format_experience_detailed(sections.get('Professional Experience', ''))}

\\end{{document}}"""

        output_file = output_dir / "resume_two_column.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_traditional_resume(self, frontmatter, sections, output_dir):
        """Create a traditional single-column resume"""
        content = f"""\\documentclass[11pt,letterpaper]{{article}}
\\usepackage[left=1in,right=1in,top=1in,bottom=1in]{{geometry}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}

\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}

% Custom section formatting
\\titleformat{{\\section}}{{\\Large\\bfseries}}{{}}{{0em}}{{}}[\\titlerule]
\\titlespacing*{{\\section}}{{0pt}}{{2ex plus 1ex minus .2ex}}{{1.5ex plus .2ex}}

\\begin{{document}}

% Header
\\begin{{center}}
{{\\LARGE\\bfseries {frontmatter.get('name', 'Ronald Reck')}}}

\\vspace{{0.1in}}
{frontmatter.get('address', 'Clifton, VA 20124')}

{frontmatter.get('phone', '248-444-0835')} \\textbullet\\, {frontmatter.get('email', 'rreck@rrecktek.com')}

{frontmatter.get('website', 'www.rrecktek.com')} \\textbullet\\, {frontmatter.get('linkedin', 'linkedin.com/in/ronaldreck')}
\\end{{center}}

\\section{{Objective}}
{frontmatter.get('target_role', 'Senior AI Architect')} with expertise in Generative AI, Machine Learning, and Cloud Technologies. {frontmatter.get('clearance', 'Active DoD Top Secret Clearance & FBI Counterintelligence Polygraph')}.

\\section{{Professional Summary}}
{self._clean_text(sections.get('Professional Summary', ''))}

\\section{{Technical Skills}}
\\textbf{{Artificial Intelligence \\& Machine Learning:}} TensorFlow, PyTorch, LangChain, Ollama, Transformers, Natural Language Processing, Computer Vision, Generative AI, Predictive Analytics

\\textbf{{Programming Languages:}} Python, R, Perl, Shell, PHP, SQL, JavaScript, C, LISP, Pascal, Basic

\\textbf{{Cloud \\& DevOps:}} Amazon Web Services (18+ years), Docker, Kubernetes, Prometheus, Grafana, DevOps, Configuration Management

\\textbf{{Databases:}} MySQL, PostgreSQL, MongoDB, Virtuoso, MarkLogic, VectorDB, Oracle, SyBase

\\section{{Professional Experience}}
{self._format_experience_traditional(sections.get('Professional Experience', ''))}

\\section{{Education}}
{self._format_education_traditional(sections.get('Education', ''))}

\\section{{Security Clearance}}
{frontmatter.get('clearance', 'Active DoD Top Secret Clearance & FBI Counterintelligence Polygraph')}

\\end{{document}}"""

        output_file = output_dir / "resume_traditional.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_creative_resume(self, frontmatter, sections, output_dir):
        """Create a creative, design-forward resume"""
        content = f"""\\documentclass[10pt,a4paper]{{article}}
\\usepackage[left=0.4in,right=0.4in,top=0.4in,bottom=0.4in]{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{tikz}}
\\usepackage{{enumitem}}
\\usepackage{{fontawesome}}

% Define colors
\\definecolor{{creative1}}{{RGB}}{{26, 188, 156}}
\\definecolor{{creative2}}{{RGB}}{{52, 152, 219}}
\\definecolor{{creative3}}{{RGB}}{{155, 89, 182}}
\\definecolor{{darkgray}}{{RGB}}{{64, 64, 64}}

\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}

\\begin{{document}}

% Header with creative design
\\begin{{tikzpicture}}[remember picture,overlay]
\\fill[creative1] (current page.north west) rectangle ([yshift=-1.5in]current page.north east);
\\end{{tikzpicture}}

\\vspace{{0.3in}}
\\begin{{center}}
\\color{{white}}
{{\\Huge\\bfseries {frontmatter.get('name', 'Ronald Reck')}}}

\\vspace{{0.1in}}
{{\\Large {frontmatter.get('target_role', 'Senior AI Architect')}}}

\\vspace{{0.1in}}
\\faPhone\\, {frontmatter.get('phone', '248-444-0835')} \\quad
\\faEnvelope\\, {frontmatter.get('email', 'rreck@rrecktek.com')} \\quad
\\faMapMarker\\, {frontmatter.get('address', 'Clifton, VA')}
\\end{{center}}

\\vspace{{0.8in}}

% Three-column layout
\\begin{{minipage}}[t]{{2.3in}}
\\textbf{{\\large\\color{{creative2}} AI \\& MACHINE LEARNING}}
\\vspace{{0.1in}}

\\begin{{itemize}}[leftmargin=*,noitemsep]
\\item TensorFlow \\& PyTorch
\\item LangChain \\& Ollama
\\item Generative AI
\\item Natural Language Processing
\\item Computer Vision
\\item Predictive Analytics
\\item Transformers \\& LLMs
\\end{{itemize}}

\\vspace{{0.3in}}
\\textbf{{\\large\\color{{creative2}} PROGRAMMING}}
\\vspace{{0.1in}}

\\begin{{itemize}}[leftmargin=*,noitemsep]
\\item Python (Expert)
\\item R \\& RMarkdown
\\item Perl \\& Shell
\\item PHP \\& SQL
\\item JavaScript \\& C
\\item LISP \\& Pascal
\\end{{itemize}}

\\vspace{{0.3in}}
\\textbf{{\\large\\color{{creative2}} CLOUD \\& DEVOPS}}
\\vspace{{0.1in}}

\\begin{{itemize}}[leftmargin=*,noitemsep]
\\item AWS (18+ years)
\\item Docker \\& Kubernetes  
\\item Prometheus \\& Grafana
\\item DevOps \\& Automation
\\item Configuration Management
\\end{{itemize}}

\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{2.3in}}

\\textbf{{\\large\\color{{creative3}} RECENT AI PROJECTS}}
\\vspace{{0.1in}}

\\textbf{{Generative AI for Immigration}}
\\\\
Designed L-1 Visa processing using local LLM

\\textbf{{GAN for Counterfeit Detection}}
\\\\
Luxury brands anti-counterfeiting system

\\textbf{{NLP Processing Pipeline}}
\\\\
Multi-domain abstractive/extractive processing

\\textbf{{Customer Segmentation}}
\\\\
Unsupervised categorization for 20k customers

\\textbf{{Semantic Comparison}}
\\\\
Vector-based analysis of 700k news articles

\\textbf{{FAERS Pharmacovigilance}}
\\\\
25MM records semantic modeling (252Gb)

\\vspace{{0.3in}}
\\textbf{{\\large\\color{{creative3}} SECURITY CLEARANCE}}
\\vspace{{0.1in}}

\\textbf{{Active DoD Top Secret}}
\\\\
FBI Counterintelligence Polygraph

\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{2.3in}}

\\textbf{{\\large\\color{{creative2}} PROFESSIONAL SUMMARY}}
\\vspace{{0.1in}}

Experienced AI professional specializing in \\textbf{{Generative AI}} with 18+ years AWS experience. Published author and enterprise architect. Commercial AI software publisher on AWS Marketplace since 2015.

\\vspace{{0.3in}}
\\textbf{{\\large\\color{{creative3}} KEY EXPERIENCE}}
\\vspace{{0.1in}}

\\textbf{{Technica Corporation}}
\\\\
\\textit{{Subject Matter Expert | FBI}}
\\\\
Service Award within 90 days

\\textbf{{RRecktek LLC}}
\\\\
\\textit{{Consultant | 100+ Clients}}
\\\\
J\\&J, DHS, DTIC, Eastman Kodak

\\textbf{{DoD Joint AI Center}}
\\\\
\\textit{{Senior Technology Advisor}}
\\\\
Data Science oversight, tens of millions funding

\\vspace{{0.3in}}
\\textbf{{\\large\\color{{creative3}} EDUCATION}}
\\vspace{{0.1in}}

\\textbf{{Eastern Michigan University}}
\\\\
MA English Linguistics (2007)

\\textbf{{Wayne State University}}
\\\\
BA English Linguistics (1992)

\\end{{minipage}}

\\end{{document}}"""

        output_file = output_dir / "resume_creative.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_academic_resume(self, frontmatter, sections, output_dir):
        """Create an academic CV-style resume"""
        content = f"""\\documentclass[11pt,letterpaper]{{article}}
\\usepackage[left=1in,right=1in,top=1in,bottom=1in]{{geometry}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}
\\usepackage{{url}}

\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}

% Academic formatting
\\titleformat{{\\section}}{{\\large\\bfseries}}{{}}{{0em}}{{}}
\\titlespacing*{{\\section}}{{0pt}}{{2ex plus 1ex minus .2ex}}{{1ex plus .2ex}}

\\begin{{document}}

% Academic header
\\begin{{center}}
{{\\Large\\bfseries {frontmatter.get('name', 'Ronald Reck')}}}

\\vspace{{0.1in}}
{frontmatter.get('address', 'Clifton, VA 20124')} \\textbullet\\, {frontmatter.get('phone', '248-444-0835')} \\textbullet\\, {frontmatter.get('email', 'rreck@rrecktek.com')}

\\url{{{frontmatter.get('website', 'www.rrecktek.com')}}} \\textbullet\\, \\url{{{frontmatter.get('linkedin', 'linkedin.com/in/ronaldreck')}}}
\\end{{center}}

\\section{{Research Interests}}
Artificial Intelligence, Machine Learning, Natural Language Processing, Generative AI, Computational Linguistics, Knowledge Representation, Semantic Web Technologies, Predictive Analytics

\\section{{Education}}
{self._format_education_academic(sections.get('Education', ''))}

\\section{{Professional Appointments}}
{self._format_experience_academic(sections.get('Professional Experience', ''))}

\\section{{Technical Expertise}}
\\textbf{{Artificial Intelligence:}} TensorFlow, PyTorch, LangChain, Ollama, Transformers, Natural Language Processing, Computer Vision, Generative AI, Machine Learning, Predictive Analytics

\\textbf{{Programming:}} Python, R/RMarkdown, Perl, Shell, PHP, SQL, JavaScript, C, LISP, Pascal

\\textbf{{Cloud Computing:}} Amazon Web Services (18+ years), Docker, Kubernetes, Prometheus, Grafana

\\textbf{{Databases:}} MySQL, PostgreSQL, MongoDB, Virtuoso, MarkLogic, VectorDB, Oracle

\\textbf{{Web Technologies:}} Drupal, WordPress, HTML, XML/RDF(S)/OWL, CSS, SOLR, Elasticsearch

\\section{{Security Clearance}}
{frontmatter.get('clearance', 'Active DoD Top Secret Clearance & FBI Counterintelligence Polygraph')}

\\section{{Selected Publications \\& Presentations}}
{self._format_publications(sections.get('Selected Publications, Papers, Posters & Presentations', ''))}

\\section{{Professional Memberships}}
W3C Working Groups: Government Linked Data Working Group (invited expert), Social Web XG (invited expert), GRDDL Working Group (invited expert)

AI Community Groups: Cognitive AI Community Group, Data Privacy and Controls Community Group, AI KR (Artificial Intelligence for Knowledge Representation) Community Group

\\section{{Recent Research Projects}}
\\begin{{itemize}}[noitemsep]
\\item Generative AI for Immigration L-1 Visas using local Large Language Models
\\item GAN-based counterfeit detection for luxury brands  
\\item NLP processing pipeline for biomedical research and FAERS compliance
\\item Unsupervised categorization for customer segmentation (20k records)
\\item Vector-based semantic comparison on 700k news articles
\\item Semantic modeling of FDA FAERS pharmacovigilance data (25MM records, 252Gb)
\\end{{itemize}}

\\end{{document}}"""

        output_file = output_dir / "resume_academic.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def _clean_text(self, text):
        """Clean text for LaTeX"""
        if not text:
            return ""
        
        # Remove markdown headers and clean up
        lines = []
        for line in text.split('\\n'):
            line = line.strip()
            if not line.startswith('#') and line:
                # Escape special LaTeX characters
                line = line.replace('&', '\\&')
                line = line.replace('%', '\\%')
                line = line.replace('$', '\\$')
                lines.append(line)
        
        return ' '.join(lines)

    def _format_experience_compact(self, exp_text):
        """Format experience in compact form"""
        if not exp_text:
            return ""
            
        formatted = ""
        lines = exp_text.split('\\n')
        count = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###') and count < 3:  # Limit to 3 most recent
                company = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    position_line = lines[i + 1].strip()
                    if '|' in position_line:
                        position, dates = position_line.split('|', 1)
                        position = position.strip('*').strip()
                        dates = dates.strip()
                        
                        formatted += f"\\textbf{{{company}}} \\\\\\n"
                        formatted += f"\\textit{{{position}}} \\hfill {dates} \\\\\\n"
                        count += 1
                        
        return formatted

    def _format_experience_detailed(self, exp_text):
        """Format experience with details"""
        if not exp_text:
            return ""
            
        formatted = ""
        lines = exp_text.split('\\n')
        
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
                        
                        formatted += f"\\textbf{{{company}}} \\hfill {dates}\\\\\\n"
                        formatted += f"\\textit{{{position}}}\\\\\\n"
                        
                        # Get description bullets
                        i += 1
                        bullets = []
                        while i < len(lines) and not lines[i].strip().startswith('###'):
                            if lines[i].strip().startswith('-'):
                                bullet = lines[i].strip()[1:].strip()
                                if bullet:
                                    bullets.append(bullet)
                            i += 1
                            
                        if bullets:
                            formatted += "\\begin{itemize}[noitemsep]\\n"
                            for bullet in bullets[:4]:  # Limit bullets
                                formatted += f"\\item {bullet}\\n"
                            formatted += "\\end{itemize}\\n"
                        
                        formatted += "\\vspace{0.1in}\\n"
                        continue
            i += 1
            
        return formatted

    def _format_experience_traditional(self, exp_text):
        """Format experience in traditional style"""
        return self._format_experience_detailed(exp_text)

    def _format_experience_academic(self, exp_text):
        """Format experience for academic CV"""
        if not exp_text:
            return ""
            
        formatted = ""
        lines = exp_text.split('\\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###'):
                company = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    position_line = lines[i + 1].strip()
                    if '|' in position_line:
                        position, dates = position_line.split('|', 1)
                        position = position.strip('*').strip()
                        dates = dates.strip()
                        
                        formatted += f"{dates} \\quad \\textbf{{{position}}}, {company}\\\\\\n"
                        
        return formatted

    def _format_education_sidebar(self, edu_text):
        """Format education for sidebar"""
        if not edu_text:
            return ""
            
        formatted = ""
        lines = edu_text.split('\\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###'):
                school = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    next_line = lines[i + 1].strip()
                    degree, date = next_line.split('|', 1)
                    degree = degree.strip('*').strip()
                    date = date.strip()
                    formatted += f"\\textbf{{{degree}}}\\\\\\n{school} ({date})\\\\\\n\\vspace{{0.1in}}\\n"
                    
        return formatted

    def _format_education_simple(self, edu_text):
        """Format education in simple style"""
        if not edu_text:
            return ""
            
        formatted = ""
        lines = edu_text.split('\\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###'):
                school = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    next_line = lines[i + 1].strip()
                    degree, date = next_line.split('|', 1)
                    degree = degree.strip('*').strip()
                    date = date.strip()
                    formatted += f"\\textbf{{{school}}} \\\\\\n{degree}, {date}\\\\\\n"
                    
        return formatted

    def _format_education_traditional(self, edu_text):
        """Format education in traditional style"""
        return self._format_education_simple(edu_text)

    def _format_education_academic(self, edu_text):
        """Format education for academic CV"""
        if not edu_text:
            return ""
            
        formatted = ""
        lines = edu_text.split('\\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###'):
                school = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    next_line = lines[i + 1].strip()
                    degree, date = next_line.split('|', 1)
                    degree = degree.strip('*').strip()
                    date = date.strip()
                    formatted += f"\\textbf{{{degree}}}, {school}, {date}\\\\\\n"
                    
        return formatted

    def _format_publications(self, pub_text):
        """Format publications for academic CV"""
        if not pub_text:
            return ""
            
        formatted = ""
        lines = pub_text.split('\\n')
        
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit() and '.' in line:
                # This is a numbered publication
                pub = line.split('.', 1)[1].strip()
                if pub:
                    formatted += f"{pub}\\\\\\n\\vspace{{0.1in}}\\n"
                    
        return formatted

    def compile_latex(self, tex_file):
        """Compile LaTeX file to PDF"""
        try:
            work_dir = tex_file.parent
            cmd = ['pdflatex', '-interaction=nonstopmode', str(tex_file)]
            result = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True)
            
            # Check if PDF was actually created, regardless of return code
            pdf_file = tex_file.with_suffix('.pdf')
            if pdf_file.exists():
                logger.info(f"Successfully compiled {tex_file.name}")
                return pdf_file
            else:
                logger.warning(f"Compilation failed for {tex_file.name}")
                # Show actual errors from log file if available
                log_file = tex_file.with_suffix('.log')
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        log_content = f.read()
                        if 'Error:' in log_content or 'Fatal error' in log_content:
                            error_lines = [line for line in log_content.split('\\n') if 'Error:' in line or 'Fatal' in line][:3]
                            if error_lines:
                                logger.warning(f"Errors: {'; '.join(error_lines)}")
                return None
            
        except Exception as e:
            logger.error(f"Error compiling {tex_file}: {e}")
            return None

    def generate_all_distinct_formats(self):
        """Generate all distinct resume formats"""
        frontmatter, markdown_content = self.load_resume_data()
        sections = self.extract_sections(markdown_content)
        
        generated_resumes = []
        
        # Create output directory
        output_dir = self.output_dir / "distinct_formats"
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Generating distinct resume formats in {output_dir}")
        
        # Generate all formats
        formats = [
            ("Modern Sidebar", self.create_modern_sidebar_resume),
            ("Two Column", self.create_two_column_resume), 
            ("Traditional", self.create_traditional_resume),
            ("Creative", self.create_creative_resume),
            ("Academic", self.create_academic_resume)
        ]
        
        for format_name, create_func in formats:
            try:
                tex_file = create_func(frontmatter, sections, output_dir)
                pdf_file = self.compile_latex(tex_file)
                if pdf_file:
                    generated_resumes.append((format_name, pdf_file))
                    logger.info(f"Generated {format_name} format")
                else:
                    logger.warning(f"Failed to compile {format_name} format")
            except Exception as e:
                logger.error(f"Error generating {format_name}: {e}")
        
        logger.info(f"Generated {len(generated_resumes)} distinct resume formats")
        return generated_resumes

if __name__ == "__main__":
    generator = DistinctResumeGenerator()
    resumes = generator.generate_all_distinct_formats()
    
    print(f"\\nGenerated {len(resumes)} distinct resume formats:")
    for name, pdf_path in resumes:
        print(f"  ✓ {name}: {pdf_path}")
        
    if len(resumes) > 0:
        print(f"\\nResumes saved in: {resumes[0][1].parent}")
    else:
        print("\\nNo resumes were successfully generated.")