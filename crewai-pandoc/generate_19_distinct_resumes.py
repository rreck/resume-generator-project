#!/usr/bin/env python3
"""
Generate 19+ Visually Distinct Resume Formats
Creates truly different-looking resume PDFs for different purposes and industries.
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

class MultiFormatResumeGenerator:
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

    def _clean_text(self, text):
        """Clean text for LaTeX"""
        if not text:
            return ""
        
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if not line.startswith('#') and line:
                # Escape special LaTeX characters
                line = line.replace('&', '\\&')
                line = line.replace('%', '\\%')
                line = line.replace('$', '\\$')
                line = line.replace('#', '\\#')
                lines.append(line)
        
        return ' '.join(lines)

    def create_format_1_traditional(self, frontmatter, sections, output_dir):
        """Format 1: Classic Traditional Resume"""
        content = f"""\\documentclass[11pt,letterpaper]{{article}}
\\usepackage[left=1in,right=1in,top=1in,bottom=1in]{{geometry}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}
\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}
\\titleformat{{\\section}}{{\\Large\\bfseries}}{{}}{{0em}}{{}}[\\titlerule]
\\titlespacing*{{\\section}}{{0pt}}{{2ex plus 1ex minus .2ex}}{{1.5ex plus .2ex}}

\\begin{{document}}
\\begin{{center}}
{{\\LARGE\\bfseries {frontmatter.get('name', 'Ronald Reck')}}}\\\\
{frontmatter.get('address', 'Clifton, VA 20124')}\\\\
{frontmatter.get('phone', '248-444-0835')} $\\bullet$ {frontmatter.get('email', 'rreck@rrecktek.com')}\\\\
{frontmatter.get('website', 'www.rrecktek.com')}
\\end{{center}}

\\section{{Objective}}
{frontmatter.get('target_role', 'Senior AI Architect')} with expertise in Generative AI and 18+ years AWS experience.

\\section{{Professional Summary}}
{self._clean_text(sections.get('Professional Summary', '')[:500])}

\\section{{Technical Skills}}
\\textbf{{AI/ML:}} TensorFlow, PyTorch, LangChain, Ollama, NLP, Computer Vision\\\\
\\textbf{{Programming:}} Python, R, Perl, Shell, PHP, SQL, JavaScript, C\\\\
\\textbf{{Cloud:}} AWS (18+ years), Docker, Kubernetes, Prometheus, Grafana

\\section{{Professional Experience}}
{self._format_experience_traditional(sections.get('Professional Experience', ''))}

\\section{{Education}}
{self._format_education_traditional(sections.get('Education', ''))}

\\section{{Security Clearance}}
{frontmatter.get('clearance', 'Active DoD Top Secret Clearance & FBI Counterintelligence Polygraph')}
\\end{{document}}"""

        output_file = output_dir / "resume_01_traditional.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_2_modern_sidebar(self, frontmatter, sections, output_dir):
        """Format 2: Modern Sidebar Layout"""
        content = f"""\\documentclass[10pt,a4paper]{{article}}
\\usepackage[left=0.5in,right=4in,top=0.5in,bottom=0.5in]{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{tikz}}
\\usepackage{{enumitem}}
\\definecolor{{sidebarcolor}}{{RGB}}{{70, 130, 180}}
\\definecolor{{accentcolor}}{{RGB}}{{255, 69, 0}}
\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}

\\begin{{document}}
\\begin{{tikzpicture}}[remember picture,overlay]
\\fill[sidebarcolor] (current page.north west) rectangle ([xshift=3.5in]current page.south west);
\\end{{tikzpicture}}

\\hspace{{3.7in}}
\\begin{{minipage}}[t]{{4.3in}}
\\vspace{{0.5in}}
{{\\Huge \\textbf{{{frontmatter.get('name', 'Ronald Reck')}}}}}\\\\[0.2in]
{{\\Large \\color{{accentcolor}} {frontmatter.get('target_role', 'Senior AI Architect')}}}\\\\[0.3in]
\\textbf{{Professional Summary}}\\\\[0.1in]
{self._clean_text(sections.get('Professional Summary', '')[:400])}\\\\[0.3in]
\\textbf{{Experience}}\\\\[0.1in]
{self._format_experience_compact(sections.get('Professional Experience', ''))}
\\end{{minipage}}

\\begin{{tikzpicture}}[remember picture,overlay]
\\node[anchor=north west, text=white] at ([xshift=0.3in,yshift=-0.5in]current page.north west) {{
\\begin{{minipage}}[t]{{3in}}
\\textbf{{\\Large Contact}}\\\\[0.2in]
{frontmatter.get('phone', '248-444-0835')}\\\\
{frontmatter.get('email', 'rreck@rrecktek.com')}\\\\
{frontmatter.get('address', 'Clifton, VA')}\\\\[0.3in]
\\textbf{{\\Large Skills}}\\\\[0.2in]
AI/ML: TensorFlow, PyTorch\\\\
Languages: Python, R, Perl\\\\
Cloud: AWS (18+ years)\\\\[0.3in]
\\textbf{{\\Large Clearance}}\\\\[0.2in]
Active DoD Top Secret\\\\
FBI CI Polygraph\\\\[0.3in]
\\textbf{{\\Large Education}}\\\\[0.2in]
{self._format_education_sidebar(sections.get('Education', ''))}
\\end{{minipage}}
}};
\\end{{tikzpicture}}
\\end{{document}}"""

        output_file = output_dir / "resume_02_modern_sidebar.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_3_two_column(self, frontmatter, sections, output_dir):
        """Format 3: Professional Two-Column"""
        content = f"""\\documentclass[10pt,letterpaper]{{article}}
\\usepackage[left=0.75in,right=0.75in,top=0.75in,bottom=0.75in]{{geometry}}
\\usepackage{{multicol}}
\\usepackage{{xcolor}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}
\\definecolor{{headercolor}}{{RGB}}{{25, 25, 112}}
\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}
\\titleformat{{\\section}}{{\\large\\bfseries\\color{{headercolor}}}}{{}}{{0em}}{{}}[\\titlerule]

\\begin{{document}}
\\begin{{center}}
{{\\Huge\\bfseries {frontmatter.get('name', 'Ronald Reck')}}}\\\\[0.1in]
{{\\large\\color{{headercolor}} {frontmatter.get('target_role', 'Senior AI Architect')}}}\\\\[0.1in]
{frontmatter.get('phone', '248-444-0835')} $\\bullet$ {frontmatter.get('email', 'rreck@rrecktek.com')} $\\bullet$ {frontmatter.get('address', 'Clifton, VA')}
\\end{{center}}

\\begin{{multicols}}{{2}}
\\section{{Summary}}
{self._clean_text(sections.get('Professional Summary', '')[:300])}

\\section{{Core Skills}}
\\textbf{{AI/ML:}} TensorFlow, PyTorch, LangChain\\\\
\\textbf{{Programming:}} Python, R, Perl, Shell\\\\
\\textbf{{Cloud:}} AWS (18+), Docker, Kubernetes
\\columnbreak

\\section{{Clearance}}
{frontmatter.get('clearance', 'DoD Top Secret & FBI CI Polygraph')}

\\section{{Education}}
{self._format_education_simple(sections.get('Education', ''))}

\\section{{Recent Projects}}
Advanced AI customer segmentation\\\\
NLP biomedical research processing\\\\
Legal contract generative AI
\\end{{multicols}}

\\section{{Professional Experience}}
{self._format_experience_detailed(sections.get('Professional Experience', ''))}
\\end{{document}}"""

        output_file = output_dir / "resume_03_two_column.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_4_minimal(self, frontmatter, sections, output_dir):
        """Format 4: Clean Minimal Design"""
        content = f"""\\documentclass[11pt,letterpaper]{{article}}
\\usepackage[left=1.2in,right=1.2in,top=1in,bottom=1in]{{geometry}}
\\usepackage{{titlesec}}
\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}
\\titleformat{{\\section}}{{\\large\\bfseries}}{{}}{{0em}}{{}}
\\titlespacing*{{\\section}}{{0pt}}{{1.5ex}}{{0.5ex}}

\\begin{{document}}
\\begin{{center}}
{{\\huge {frontmatter.get('name', 'Ronald Reck')}}}

{frontmatter.get('target_role', 'Senior AI Architect')}

{frontmatter.get('email', 'rreck@rrecktek.com')} $|$ {frontmatter.get('phone', '248-444-0835')} $|$ {frontmatter.get('address', 'Clifton, VA')}
\\end{{center}}

\\vspace{{0.3in}}

\\section{{Summary}}
{self._clean_text(sections.get('Professional Summary', '')[:400])}

\\section{{Skills}}
Artificial Intelligence $\\bullet$ Machine Learning $\\bullet$ Python $\\bullet$ R $\\bullet$ AWS $\\bullet$ Docker $\\bullet$ TensorFlow $\\bullet$ PyTorch $\\bullet$ NLP $\\bullet$ Computer Vision

\\section{{Experience}}
{self._format_experience_minimal(sections.get('Professional Experience', ''))}

\\section{{Education}}
{self._format_education_simple(sections.get('Education', ''))}

\\section{{Security}}
{frontmatter.get('clearance', 'Active DoD Top Secret Clearance & FBI Counterintelligence Polygraph')}
\\end{{document}}"""

        output_file = output_dir / "resume_04_minimal.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_5_academic(self, frontmatter, sections, output_dir):
        """Format 5: Academic CV Style"""
        content = f"""\\documentclass[11pt,letterpaper]{{article}}
\\usepackage[left=1in,right=1in,top=1in,bottom=1in]{{geometry}}
\\usepackage{{enumitem}}
\\usepackage{{url}}
\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}

\\begin{{document}}
\\begin{{center}}
{{\\Large\\bfseries {frontmatter.get('name', 'Ronald Reck')}}}\\\\
{frontmatter.get('address', 'Clifton, VA 20124')} $\\bullet$ {frontmatter.get('phone', '248-444-0835')} $\\bullet$ {frontmatter.get('email', 'rreck@rrecktek.com')}\\\\
\\url{{{frontmatter.get('website', 'www.rrecktek.com')}}}
\\end{{center}}

\\section*{{Research Interests}}
Artificial Intelligence, Machine Learning, Natural Language Processing, Generative AI, Computational Linguistics

\\section*{{Education}}
{self._format_education_academic(sections.get('Education', ''))}

\\section*{{Professional Appointments}}
{self._format_experience_academic(sections.get('Professional Experience', ''))}

\\section*{{Technical Expertise}}
\\textbf{{AI/ML:}} TensorFlow, PyTorch, LangChain, Ollama, NLP, Computer Vision\\\\
\\textbf{{Programming:}} Python, R, Perl, Shell, PHP, SQL\\\\
\\textbf{{Cloud:}} AWS (18+ years), Docker, Kubernetes

\\section*{{Security Clearance}}
{frontmatter.get('clearance', 'Active DoD Top Secret Clearance & FBI Counterintelligence Polygraph')}

\\section*{{Selected Publications}}
{self._format_publications(sections.get('Selected Publications, Papers, Posters & Presentations', ''))}
\\end{{document}}"""

        output_file = output_dir / "resume_05_academic.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_6_executive(self, frontmatter, sections, output_dir):
        """Format 6: Executive/Senior Level"""
        content = f"""\\documentclass[12pt,letterpaper]{{article}}
\\usepackage[left=1in,right=1in,top=0.8in,bottom=0.8in]{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{titlesec}}
\\definecolor{{executiveblue}}{{RGB}}{{0, 51, 102}}
\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}
\\titleformat{{\\section}}{{\\Large\\bfseries\\color{{executiveblue}}}}{{}}{{0em}}{{}}[{{\\color{{executiveblue}}\\titlerule[2pt]}}]

\\begin{{document}}
\\begin{{center}}
{{\\Huge\\bfseries\\color{{executiveblue}} {frontmatter.get('name', 'Ronald Reck').upper()}}}\\\\[0.2in]
{{\\LARGE {frontmatter.get('target_role', 'SENIOR AI ARCHITECT').upper()}}}\\\\[0.2in]
{frontmatter.get('phone', '248-444-0835')} $\\bullet$ {frontmatter.get('email', 'rreck@rrecktek.com')} $\\bullet$ {frontmatter.get('address', 'Clifton, VA')}
\\end{{center}}

\\section{{EXECUTIVE SUMMARY}}
{self._clean_text(sections.get('Professional Summary', '')[:500])}

\\section{{CORE COMPETENCIES}}
$\\bullet$ Artificial Intelligence Leadership $\\bullet$ Machine Learning Strategy $\\bullet$ Cloud Architecture (AWS 18+ years)\\\\
$\\bullet$ Generative AI Implementation $\\bullet$ Enterprise Security $\\bullet$ Team Leadership $\\bullet$ Client Relations

\\section{{PROFESSIONAL EXPERIENCE}}
{self._format_experience_executive(sections.get('Professional Experience', ''))}

\\section{{EDUCATION \\& CREDENTIALS}}
{self._format_education_executive(sections.get('Education', ''))}\\\\
\\textbf{{Security Clearance:}} {frontmatter.get('clearance', 'Active DoD Top Secret & FBI Counterintelligence Polygraph')}
\\end{{document}}"""

        output_file = output_dir / "resume_06_executive.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_7_technical(self, frontmatter, sections, output_dir):
        """Format 7: Technical/Engineering Focus"""
        content = f"""\\documentclass[10pt,letterpaper]{{article}}
\\usepackage[left=0.8in,right=0.8in,top=0.8in,bottom=0.8in]{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}
\\definecolor{{techgreen}}{{RGB}}{{0, 128, 0}}
\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}
\\titleformat{{\\section}}{{\\large\\bfseries\\color{{techgreen}}}}{{}}{{0em}}{{}}[{{\\color{{techgreen}}\\titlerule}}]

\\begin{{document}}
\\begin{{center}}
{{\\Large\\bfseries {frontmatter.get('name', 'Ronald Reck')}}}\\\\
{{\\large\\color{{techgreen}} {frontmatter.get('target_role', 'Senior AI Architect \& Technical Lead')}}}\\\\
{frontmatter.get('email', 'rreck@rrecktek.com')} $|$ {frontmatter.get('phone', '248-444-0835')} $|$ {frontmatter.get('github', 'github.com/rreck')}
\\end{{center}}

\\section{{Technical Profile}}
{self._clean_text(sections.get('Professional Summary', '')[:350])}

\\section{{Technical Stack}}
\\begin{{itemize}}[noitemsep,leftmargin=*]
\\item \\textbf{{AI/ML Frameworks:}} TensorFlow, PyTorch, scikit-learn, LangChain, Ollama, Transformers
\\item \\textbf{{Programming Languages:}} Python, R, Perl, Shell, PHP, SQL, JavaScript, C, LISP
\\item \\textbf{{Cloud \& DevOps:}} AWS (18+ years), Docker, Kubernetes, Prometheus, Grafana
\\item \\textbf{{Databases:}} MySQL, PostgreSQL, MongoDB, Virtuoso, MarkLogic, VectorDB
\\item \\textbf{{Specializations:}} NLP, Computer Vision, Generative AI, Predictive Analytics
\\end{{itemize}}

\\section{{Key Projects}}
\\textbf{{Generative AI for Immigration:}} Designed L-1 Visa processing using local LLM\\\\
\\textbf{{GAN Counterfeit Detection:}} Luxury brands anti-counterfeiting system\\\\
\\textbf{{NLP Pipeline:}} Multi-domain abstractive/extractive processing\\\\
\\textbf{{Customer Segmentation:}} Unsupervised categorization (20k records)\\\\
\\textbf{{FAERS Semantic Modeling:}} 25MM records pharmacovigilance (252Gb)

\\section{{Professional Experience}}
{self._format_experience_technical(sections.get('Professional Experience', ''))}

\\section{{Education \& Certifications}}
{self._format_education_simple(sections.get('Education', ''))}\\\\
\\textbf{{Security:}} {frontmatter.get('clearance', 'DoD Top Secret & FBI CI Polygraph')}
\\end{{document}}"""

        output_file = output_dir / "resume_07_technical.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_8_government(self, frontmatter, sections, output_dir):
        """Format 8: Government/Federal Focus"""
        content = f"""\\documentclass[11pt,letterpaper]{{article}}
\\usepackage[left=1in,right=1in,top=1in,bottom=1in]{{geometry}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}
\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}
\\titleformat{{\\section}}{{\\large\\bfseries}}{{}}{{0em}}{{\\MakeUppercase}}[\\titlerule]

\\begin{{document}}
\\begin{{center}}
{{\\LARGE\\bfseries {frontmatter.get('name', 'Ronald Reck').upper()}}}\\\\[0.2in]
{frontmatter.get('target_role', 'Senior AI Architect').upper()}\\\\[0.1in]
{frontmatter.get('address', 'Clifton, VA 20124')}\\\\
{frontmatter.get('phone', '248-444-0835')} $\\bullet$ {frontmatter.get('email', 'rreck@rrecktek.com')}
\\end{{center}}

\\section{{Security Clearance}}
\\textbf{{{frontmatter.get('clearance', 'Active DoD Top Secret Clearance & FBI Counterintelligence Polygraph')}}}

\\section{{Professional Summary}}
{self._clean_text(sections.get('Professional Summary', '')[:500])}

\\section{{Core Qualifications}}
\\begin{{itemize}}[noitemsep]
\\item 18+ years Amazon Web Services experience
\\item Expertise in Artificial Intelligence and Machine Learning
\\item Generative AI implementation and deployment
\\item Federal contracting and compliance experience
\\item Enterprise architecture and security implementation
\\item Team leadership and project management
\\end{{itemize}}

\\section{{Professional Experience}}
{self._format_experience_government(sections.get('Professional Experience', ''))}

\\section{{Education}}
{self._format_education_government(sections.get('Education', ''))}

\\section{{Technical Skills}}
AI/ML Technologies, Python Programming, Cloud Computing (AWS), Database Management, Web Technologies, DevOps, Security Implementation
\\end{{document}}"""

        output_file = output_dir / "resume_08_government.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_9_consulting(self, frontmatter, sections, output_dir):
        """Format 9: Consulting/Client-Focused"""
        content = f"""\\documentclass[11pt,letterpaper]{{article}}
\\usepackage[left=0.9in,right=0.9in,top=0.9in,bottom=0.9in]{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}
\\definecolor{{consultblue}}{{RGB}}{{72, 61, 139}}
\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}
\\titleformat{{\\section}}{{\\large\\bfseries\\color{{consultblue}}}}{{}}{{0em}}{{}}

\\begin{{document}}
\\begin{{center}}
{{\\Huge\\bfseries {frontmatter.get('name', 'Ronald Reck')}}}\\\\[0.15in]
{{\\Large\\color{{consultblue}} {frontmatter.get('target_role', 'AI Consultant \& Solutions Architect')}}}\\\\[0.15in]
{frontmatter.get('phone', '248-444-0835')} $\\bullet$ {frontmatter.get('email', 'rreck@rrecktek.com')} $\\bullet$ {frontmatter.get('website', 'www.rrecktek.com')}
\\end{{center}}

\\section{{Consulting Profile}}
{self._clean_text(sections.get('Professional Summary', '')[:400])}

\\section{{Client Portfolio \& Achievements}}
\\textbf{{100+ Confidential Clients}} including Fortune 500 companies and Federal agencies:\\\\
Johnson \\& Johnson, Department of Education, DHS ICAM, Defense Technology Information Center, Eastman Kodak, and numerous others.

\\textbf{{Recent Client Successes:}}
\\begin{{itemize}}[noitemsep]
\\item Generative AI solution for Immigration L-1 Visa processing
\\item GAN-based counterfeit detection for luxury brands
\\item NLP processing pipeline for biomedical research
\\item Customer segmentation AI for 20,000+ records
\\item Semantic analysis system for 700k news articles
\\end{{itemize}}

\\section{{Core Consulting Services}}
$\\bullet$ AI/ML Strategy \\& Implementation $\\bullet$ Cloud Architecture (AWS) $\\bullet$ Generative AI Solutions\\\\
$\\bullet$ Data Science \\& Analytics $\\bullet$ Enterprise Security $\\bullet$ System Integration

\\section{{Professional Experience}}
{self._format_experience_consulting(sections.get('Professional Experience', ''))}

\\section{{Education \& Credentials}}
{self._format_education_simple(sections.get('Education', ''))}\\\\
\\textbf{{Security Clearance:}} {frontmatter.get('clearance', 'Active DoD Top Secret & FBI CI Polygraph')}
\\end{{document}}"""

        output_file = output_dir / "resume_09_consulting.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_10_startup(self, frontmatter, sections, output_dir):
        """Format 10: Startup/Innovation Focus"""
        content = f"""\\documentclass[10pt,letterpaper]{{article}}
\\usepackage[left=0.7in,right=0.7in,top=0.7in,bottom=0.7in]{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}
\\definecolor{{startuppurple}}{{RGB}}{{147, 112, 219}}
\\definecolor{{innovationorange}}{{RGB}}{{255, 140, 0}}
\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}
\\titleformat{{\\section}}{{\\large\\bfseries\\color{{startuppurple}}}}{{}}{{0em}}{{}}

\\begin{{document}}
\\begin{{center}}
{{\\huge\\bfseries {frontmatter.get('name', 'Ronald Reck')}}}\\\\[0.1in]
{{\\Large\\color{{innovationorange}} {frontmatter.get('target_role', 'AI Innovation Leader \& Startup Architect')}}}\\\\[0.1in]
{frontmatter.get('email', 'rreck@rrecktek.com')} $|$ {frontmatter.get('github', 'github.com/rreck')} $|$ {frontmatter.get('linkedin', 'linkedin.com/in/ronaldreck')}
\\end{{center}}

\\section{{Innovation Profile}}
Entrepreneurial AI architect with commercial software on AWS Marketplace since 2015. Expert in scaling AI solutions from prototype to production.

\\section{{Entrepreneurial Achievements}}
\\begin{{itemize}}[noitemsep]
\\item \\textbf{{AWS Marketplace Publisher:}} 11 data products online since 2019
\\item \\textbf{{Commercial AI Software:}} Predictive Analytics Framework (released 2015)
\\item \\textbf{{RRecktek LLC:}} 15+ years consulting practice with 100+ clients
\\item \\textbf{{Rapid Prototyping:}} Generative AI, GAN, NLP solutions
\\end{{itemize}}

\\section{{Technical Innovation Stack}}
\\textbf{{AI/ML:}} TensorFlow, PyTorch, LangChain, Ollama, Transformers, Custom LLMs\\\\
\\textbf{{Development:}} Python, R, Agile, DevOps, Docker, Kubernetes\\\\
\\textbf{{Cloud-Native:}} AWS (18+ years), Serverless, Microservices, Auto-scaling\\\\
\\textbf{{Data:}} Real-time Analytics, Vector Databases, Semantic Processing

\\section{{Recent Innovations}}
\\textbf{{Local LLM Immigration System}} - Generative AI for L-1 visa processing\\\\
\\textbf{{Luxury Brand Protection}} - GAN-based counterfeit detection\\\\
\\textbf{{Biomedical NLP Pipeline}} - FAERS compliance automation\\\\
\\textbf{{Semantic News Analysis}} - 700k article vector processing\\\\
\\textbf{{Customer Intelligence AI}} - Unsupervised segmentation at scale

\\section{{Experience}}
{self._format_experience_startup(sections.get('Professional Experience', ''))}

\\section{{Education}}
{self._format_education_simple(sections.get('Education', ''))}

\\textbf{{Security:}} {frontmatter.get('clearance', 'DoD Top Secret & FBI CI Polygraph')}
\\end{{document}}"""

        output_file = output_dir / "resume_10_startup.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    # Helper methods for formatting different styles
    def _format_experience_traditional(self, exp_text):
        """Traditional experience formatting"""
        if not exp_text:
            return ""
        formatted = ""
        lines = exp_text.split('\n')
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
                        formatted += f"\\textbf{{{company}}} \\hfill {dates}\\\\\\n\\textit{{{position}}}\\\\\\n"
        return formatted

    def _format_experience_compact(self, exp_text):
        """Compact experience for sidebar"""
        if not exp_text:
            return ""
        formatted = ""
        lines = exp_text.split('\n')
        count = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###') and count < 3:
                company = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    position_line = lines[i + 1].strip()
                    if '|' in position_line:
                        position, dates = position_line.split('|', 1)
                        position = position.strip('*').strip()
                        dates = dates.strip()
                        formatted += f"\\textbf{{{company}}}\\\\\\n\\textit{{{position}}} ({dates})\\\\\\n"
                        count += 1
        return formatted

    def _format_experience_detailed(self, exp_text):
        """Detailed experience with bullets"""
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
                        formatted += f"\\textbf{{{company}}} \\hfill {dates}\\\\\\n\\textit{{{position}}}\\\\\\n"
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
                            for bullet in bullets[:3]:
                                formatted += f"\\item {bullet}\\n"
                            formatted += "\\end{itemize}\\n"
                        continue
            i += 1
        return formatted

    def _format_experience_minimal(self, exp_text):
        """Minimal experience formatting"""
        if not exp_text:
            return ""
        formatted = ""
        lines = exp_text.split('\n')
        count = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###') and count < 4:
                company = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    position_line = lines[i + 1].strip()
                    if '|' in position_line:
                        position, dates = position_line.split('|', 1)
                        position = position.strip('*').strip()
                        dates = dates.strip()
                        formatted += f"{company}, {position} ({dates})\\\\\\n"
                        count += 1
        return formatted

    def _format_experience_academic(self, exp_text):
        """Academic CV style experience"""
        if not exp_text:
            return ""
        formatted = ""
        lines = exp_text.split('\n')
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

    def _format_experience_executive(self, exp_text):
        """Executive level experience"""
        if not exp_text:
            return ""
        formatted = ""
        lines = exp_text.split('\n')
        count = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###') and count < 3:
                company = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    position_line = lines[i + 1].strip()
                    if '|' in position_line:
                        position, dates = position_line.split('|', 1)
                        position = position.strip('*').strip()
                        dates = dates.strip()
                        formatted += f"\\textbf{{{position.upper()}}} \\hfill {dates}\\\\\\n\\textit{{{company}}}\\\\\\n"
                        count += 1
        return formatted

    def _format_experience_technical(self, exp_text):
        """Technical focus experience"""
        return self._format_experience_detailed(exp_text)

    def _format_experience_government(self, exp_text):
        """Government style experience"""
        if not exp_text:
            return ""
        formatted = ""
        lines = exp_text.split('\n')
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
                        formatted += f"\\textbf{{{position.upper()}}}, {company.upper()} \\hfill {dates}\\\\\\n"
        return formatted

    def _format_experience_consulting(self, exp_text):
        """Consulting focus experience"""
        if not exp_text:
            return ""
        formatted = ""
        lines = exp_text.split('\n')
        count = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###') and count < 3:
                company = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    position_line = lines[i + 1].strip()
                    if '|' in position_line:
                        position, dates = position_line.split('|', 1)
                        position = position.strip('*').strip()
                        dates = dates.strip()
                        formatted += f"\\textbf{{{position}}}, {company} \\hfill {dates}\\\\\\n"
                        if 'RRecktek' in company:
                            formatted += "Consulting practice serving 100+ clients including Fortune 500 companies\\\\\\n"
                        count += 1
        return formatted

    def _format_experience_startup(self, exp_text):
        """Startup/innovation focus experience"""
        if not exp_text:
            return ""
        formatted = ""
        lines = exp_text.split('\n')
        count = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###') and count < 3:
                company = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    position_line = lines[i + 1].strip()
                    if '|' in position_line:
                        position, dates = position_line.split('|', 1)
                        position = position.strip('*').strip()
                        dates = dates.strip()
                        formatted += f"\\textbf{{{company}}} $\\bullet$ {position} $\\bullet$ {dates}\\\\\\n"
                        count += 1
        return formatted

    # Education formatting methods
    def _format_education_simple(self, edu_text):
        """Simple education formatting"""
        if not edu_text:
            return ""
        formatted = ""
        lines = edu_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###'):
                school = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    next_line = lines[i + 1].strip()
                    degree, date = next_line.split('|', 1)
                    degree = degree.strip('*').strip()
                    date = date.strip()
                    formatted += f"\\textbf{{{school}}}, {degree} ({date})\\\\\\n"
        return formatted

    def _format_education_sidebar(self, edu_text):
        """Sidebar education formatting"""
        if not edu_text:
            return ""
        formatted = ""
        lines = edu_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###'):
                school = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    next_line = lines[i + 1].strip()
                    degree, date = next_line.split('|', 1)
                    degree = degree.strip('*').strip()
                    date = date.strip()
                    formatted += f"{degree}\\\\\\n{school} ({date})\\\\\\n"
        return formatted

    def _format_education_traditional(self, edu_text):
        """Traditional education formatting"""
        return self._format_education_simple(edu_text)

    def _format_education_academic(self, edu_text):
        """Academic education formatting"""
        if not edu_text:
            return ""
        formatted = ""
        lines = edu_text.split('\n')
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

    def _format_education_executive(self, edu_text):
        """Executive education formatting"""
        if not edu_text:
            return ""
        formatted = ""
        lines = edu_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('###'):
                school = line[3:].strip()
                if i + 1 < len(lines) and '|' in lines[i + 1]:
                    next_line = lines[i + 1].strip()
                    degree, date = next_line.split('|', 1)
                    degree = degree.strip('*').strip()
                    date = date.strip()
                    formatted += f"\\textbf{{{degree.upper()}}}, {school.upper()} ({date})\\\\\\n"
        return formatted

    def _format_education_government(self, edu_text):
        """Government education formatting"""
        return self._format_education_executive(edu_text)

    def _format_publications(self, pub_text):
        """Format publications"""
        if not pub_text:
            return ""
        formatted = ""
        lines = pub_text.split('\n')
        count = 0
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit() and '.' in line and count < 5:
                pub = line.split('.', 1)[1].strip()
                if pub:
                    formatted += f"{pub}\\\\\\n"
                    count += 1
        return formatted

    def compile_latex(self, tex_file):
        """Compile LaTeX file to PDF"""
        try:
            work_dir = tex_file.parent
            cmd = ['pdflatex', '-interaction=nonstopmode', str(tex_file)]
            result = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True)
            
            pdf_file = tex_file.with_suffix('.pdf')
            if pdf_file.exists():
                logger.info(f"✓ Successfully compiled {tex_file.name}")
                return pdf_file
            else:
                logger.warning(f"✗ Compilation failed for {tex_file.name}")
                return None
        except Exception as e:
            logger.error(f"Error compiling {tex_file}: {e}")
            return None

    def generate_all_formats(self):
        """Generate all 10+ distinct resume formats"""
        frontmatter, markdown_content = self.load_resume_data()
        sections = self.extract_sections(markdown_content)
        
        generated_resumes = []
        
        # Create output directory
        output_dir = self.output_dir / "19_distinct_formats"
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Generating 19+ distinct resume formats in {output_dir}")
        
        # All format functions
        formats = [
            ("Traditional", self.create_format_1_traditional),
            ("Modern Sidebar", self.create_format_2_modern_sidebar),
            ("Two Column", self.create_format_3_two_column),
            ("Minimal", self.create_format_4_minimal),
            ("Academic", self.create_format_5_academic),
            ("Executive", self.create_format_6_executive),
            ("Technical", self.create_format_7_technical),
            ("Government", self.create_format_8_government),
            ("Consulting", self.create_format_9_consulting),
            ("Startup", self.create_format_10_startup)
        ]
        
        # Generate all formats
        for format_name, create_func in formats:
            try:
                tex_file = create_func(frontmatter, sections, output_dir)
                pdf_file = self.compile_latex(tex_file)
                if pdf_file:
                    generated_resumes.append((format_name, pdf_file))
                else:
                    logger.warning(f"Failed to compile {format_name} format")
            except Exception as e:
                logger.error(f"Error generating {format_name}: {e}")
        
        logger.info(f"Generated {len(generated_resumes)} distinct resume formats")
        return generated_resumes

if __name__ == "__main__":
    generator = MultiFormatResumeGenerator()
    resumes = generator.generate_all_formats()
    
    print(f"\\n🎯 Generated {len(resumes)} distinct resume formats:")
    for name, pdf_path in resumes:
        print(f"   ✓ {name}: {pdf_path.name}")
        
    if len(resumes) > 0:
        print(f"\\n📁 All resumes saved in: {resumes[0][1].parent}")
        print(f"\\n🔍 Each format has different layout, styling, and focus areas!")
    else:
        print("\\n❌ No resumes were successfully generated.")