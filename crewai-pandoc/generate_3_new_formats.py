#!/usr/bin/env python3
"""
Generate 3 New Resume Formats Based on Added Templates
Simplified versions that work with standard LaTeX installations.
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

class NewFormatsGenerator:
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

    def create_format_20_business_insider_style(self, frontmatter, sections, output_dir):
        """Format 20: Business Insider Marissa Mayer Inspired Style"""
        content = f"""\\documentclass[11pt,letterpaper]{{article}}
\\usepackage[left=0.8in,right=0.8in,top=0.8in,bottom=0.8in]{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{enumitem}}
\\usepackage{{multicol}}
\\usepackage{{titlesec}}

% Business Insider inspired colors
\\definecolor{{BusinessBlue}}{{RGB}}{{24, 119, 242}}
\\definecolor{{BusinessGray}}{{RGB}}{{101, 103, 107}}
\\definecolor{{BusinessOrange}}{{RGB}}{{255, 90, 95}}

\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}

% Custom section formatting
\\titleformat{{\\section}}{{\\large\\bfseries\\color{{BusinessBlue}}}}{{}}{{0em}}{{}}[{{\\color{{BusinessGray}}\\titlerule}}]
\\titlespacing*{{\\section}}{{0pt}}{{1.5ex}}{{1ex}}

\\begin{{document}}

% Header with business style
\\begin{{center}}
{{\\Huge\\bfseries\\color{{BusinessBlue}} {frontmatter.get('name', 'Ronald Reck')}}}\\\\[0.2in]
{{\\Large\\color{{BusinessGray}} {frontmatter.get('target_role', 'Senior AI Architect \\& Technology Leader')}}}\\\\[0.1in]
\\rule{{5in}}{{2pt}}\\\\[0.1in]
{frontmatter.get('email', 'rreck@rrecktek.com')} $\\bullet$ {frontmatter.get('phone', '248-444-0835')} $\\bullet$ {frontmatter.get('address', 'Clifton, VA')}\\\\
{frontmatter.get('website', 'www.rrecktek.com')} $\\bullet$ {frontmatter.get('linkedin', 'linkedin.com/in/ronaldreck')}
\\end{{center}}

\\vspace{{0.3in}}

\\section{{Executive Profile}}
\\textcolor{{BusinessGray}}{{{self._clean_text(sections.get('Professional Summary', '')[:500])}}}

\\section{{Leadership Experience}}
\\textbf{{\\color{{BusinessOrange}} Subject Matter Expert}} \\hfill \\textit{{Sep 2023 -- Current}}\\\\
\\textbf{{Technica Corporation / FBI}} - Washington, DC\\\\
$\\bullet$ Service Award within 90 days of assignment\\\\
$\\bullet$ Enterprise AI strategy and implementation leadership\\\\
$\\bullet$ Cross-functional coordination across security enclaves

\\vspace{{0.2in}}
\\textbf{{\\color{{BusinessOrange}} Senior Technology Advisor}} \\hfill \\textit{{May 2020 -- June 2021}}\\\\
\\textbf{{Department of Defense (Joint AI Center)}} - Pentagon\\\\
$\\bullet$ Strategic oversight of multi-million dollar AI initiatives\\\\
$\\bullet$ Technical leadership across all military branches\\\\
$\\bullet$ Advanced NLP pipeline design for mission-critical applications

\\vspace{{0.2in}}
\\textbf{{\\color{{BusinessOrange}} Founder \\& Principal Consultant}} \\hfill \\textit{{Sep 2009 -- Present}}\\\\
\\textbf{{RRecktek LLC}} - Global Operations\\\\
$\\bullet$ Built and scaled consulting practice to 100+ enterprise clients\\\\
$\\bullet$ Published commercial AI software with 8+ years market presence\\\\
$\\bullet$ Specialized in generative AI and cloud architecture solutions

\\section{{Core Competencies}}
\\begin{{multicols}}{{2}}
\\textcolor{{BusinessBlue}}{{\\textbf{{AI \\& Machine Learning}}}}\\\\
$\\bullet$ Generative AI \\& LLMs\\\\
$\\bullet$ TensorFlow \\& PyTorch\\\\
$\\bullet$ Natural Language Processing\\\\
$\\bullet$ Computer Vision\\\\
$\\bullet$ Predictive Analytics

\\columnbreak

\\textcolor{{BusinessBlue}}{{\\textbf{{Technology Leadership}}}}\\\\
$\\bullet$ AWS Architecture (18+ years)\\\\
$\\bullet$ Enterprise Security\\\\
$\\bullet$ Cloud Strategy \\& Implementation\\\\
$\\bullet$ DevOps \\& Automation\\\\
$\\bullet$ Team Leadership
\\end{{multicols}}

\\section{{Notable Achievements}}
$\\bullet$ \\textbf{{FBI Service Award}} - Exceptional performance within first 90 days\\\\
$\\bullet$ \\textbf{{AWS Marketplace Publisher}} - 11 data products online since 2019\\\\
$\\bullet$ \\textbf{{Commercial AI Pioneer}} - Predictive Analytics Framework since 2015\\\\
$\\bullet$ \\textbf{{Security Clearance}} - {frontmatter.get('clearance', 'Active DoD Top Secret with FBI CI-Poly')}

\\section{{Education \\& Credentials}}
\\textbf{{Master of Arts, English Linguistics}} - Eastern Michigan University (2007)\\\\
\\textbf{{Bachelor of Arts, English Linguistics}} - Wayne State University (1992)\\\\
\\textbf{{Professional Recognition}} - W3C Invited Expert, Published Author (McGraw Hill)

\\end{{document}}"""

        output_file = output_dir / "resume_20_business_insider.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_21_creative_hipster(self, frontmatter, sections, output_dir):
        """Format 21: Creative Hipster Design"""
        content = f"""\\documentclass[10pt,letterpaper]{{article}}
\\usepackage[left=0.6in,right=0.6in,top=0.6in,bottom=0.6in]{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{enumitem}}
\\usepackage{{tikz}}

% Hipster color palette
\\definecolor{{HipsterTeal}}{{RGB}}{{26, 188, 156}}
\\definecolor{{HipsterOrange}}{{RGB}}{{230, 126, 34}}
\\definecolor{{HipsterPurple}}{{RGB}}{{155, 89, 182}}
\\definecolor{{HipsterBlue}}{{RGB}}{{52, 152, 219}}

\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}

\\begin{{document}}

% Creative header with geometric elements
\\begin{{tikzpicture}}[remember picture,overlay]
\\fill[HipsterTeal] (current page.north west) rectangle ([yshift=-1.5in]current page.north east);
\\fill[HipsterOrange] ([xshift=0in,yshift=-1.5in]current page.north west) rectangle ([xshift=2in,yshift=-2in]current page.north west);
\\fill[HipsterPurple] ([xshift=2in,yshift=-1.5in]current page.north west) rectangle ([xshift=4in,yshift=-2in]current page.north west);
\\fill[HipsterBlue] ([xshift=4in,yshift=-1.5in]current page.north west) rectangle ([xshift=6in,yshift=-2in]current page.north west);
\\end{{tikzpicture}}

\\vspace{{0.3in}}
\\begin{{center}}
\\color{{white}}
{{\\Huge\\bfseries {frontmatter.get('name', 'Ronald Reck')}}}\\\\[0.1in]
{{\\Large {frontmatter.get('target_role', 'Creative AI Architect')}}}
\\end{{center}}

\\vspace{{1.5in}}

\\textbf{{\\large\\color{{HipsterTeal}} CREATIVE INNOVATION PROFILE}}\\\\[0.1in]
\\textcolor{{HipsterPurple}}{{{self._clean_text(sections.get('Professional Summary', '')[:350])}}}

\\vspace{{0.3in}}

% Three-column creative layout
\\begin{{minipage}}[t]{{2.2in}}
\\textbf{{\\color{{HipsterOrange}} CREATIVE TECHNOLOGIES}}\\\\[0.1in]
\\textcolor{{HipsterBlue}}{{$\\blacksquare$}} Generative AI \\& LLMs\\\\
\\textcolor{{HipsterBlue}}{{$\\blacksquare$}} Creative Coding (Python/R)\\\\
\\textcolor{{HipsterBlue}}{{$\\blacksquare$}} Visual Data Storytelling\\\\
\\textcolor{{HipsterBlue}}{{$\\blacksquare$}} Interactive Prototyping\\\\
\\textcolor{{HipsterBlue}}{{$\\blacksquare$}} Cloud-Native Solutions\\\\[0.2in]

\\textbf{{\\color{{HipsterPurple}} INNOVATION PROJECTS}}\\\\[0.1in]
\\textcolor{{HipsterTeal}}{{$\\star$}} Immigration AI System\\\\
\\textcolor{{HipsterTeal}}{{$\\star$}} Anti-Counterfeiting GAN\\\\
\\textcolor{{HipsterTeal}}{{$\\star$}} Biomedical NLP Pipeline\\\\
\\textcolor{{HipsterTeal}}{{$\\star$}} Semantic News Analysis\\\\
\\textcolor{{HipsterTeal}}{{$\\star$}} Customer Intelligence AI
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{2.2in}}
\\textbf{{\\color{{HipsterBlue}} ENTREPRENEURIAL JOURNEY}}\\\\[0.1in]
\\textbf{{RRecktek LLC}} \\textit{{(2009-Present)}}\\\\
\\textcolor{{HipsterPurple}}{{Creative consulting practice with 100+ clients}}

\\textbf{{AWS Marketplace}} \\textit{{(2019-Present)}}\\\\
\\textcolor{{HipsterPurple}}{{11 innovative data products published}}

\\textbf{{Commercial AI Software}} \\textit{{(2015-Present)}}\\\\
\\textcolor{{HipsterPurple}}{{Predictive Analytics Framework}}\\\\[0.2in]

\\textbf{{\\color{{HipsterOrange}} CURRENT ROLES}}\\\\[0.1in]
\\textbf{{FBI/Technica}} - Subject Matter Expert\\\\
\\textcolor{{HipsterTeal}}{{Service Award within 90 days}}

\\textbf{{DoD JAIC}} - Senior Tech Advisor\\\\
\\textcolor{{HipsterTeal}}{{Multi-million dollar oversight}}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{2.2in}}
\\textbf{{\\color{{HipsterPurple}} CREATIVE CREDENTIALS}}\\\\[0.1in]
\\textbf{{Security Clearance}}\\\\
{frontmatter.get('clearance', 'DoD Top Secret + FBI CI-Poly')}\\\\[0.1in]

\\textbf{{Academic Foundation}}\\\\
MA English Linguistics - EMU (2007)\\\\
BA English Linguistics - WSU (1992)\\\\[0.1in]

\\textbf{{Recognition}}\\\\
W3C Invited Expert\\\\
Published Author (McGraw Hill)\\\\
Industry Standards Contributor\\\\[0.2in]

\\textbf{{\\color{{HipsterTeal}} CONNECT}}\\\\[0.1in]
\\textcolor{{HipsterBlue}}{{Email:}} {frontmatter.get('email', 'rreck@rrecktek.com')}\\\\
\\textcolor{{HipsterBlue}}{{Phone:}} {frontmatter.get('phone', '248-444-0835')}\\\\
\\textcolor{{HipsterBlue}}{{Web:}} {frontmatter.get('website', 'www.rrecktek.com')}\\\\
\\textcolor{{HipsterBlue}}{{LinkedIn:}} {frontmatter.get('linkedin', 'linkedin.com/in/ronaldreck')}
\\end{{minipage}}

\\end{{document}}"""

        output_file = output_dir / "resume_21_creative_hipster.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_22_enhanced_professional(self, frontmatter, sections, output_dir):
        """Format 22: Enhanced Professional Template"""
        content = f"""\\documentclass[11pt,letterpaper]{{article}}
\\usepackage[left=0.9in,right=0.9in,top=0.9in,bottom=0.9in]{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{enumitem}}
\\usepackage{{multicol}}
\\usepackage{{titlesec}}

% Professional enhanced colors
\\definecolor{{ProfessionalNavy}}{{RGB}}{{25, 42, 86}}
\\definecolor{{ProfessionalBlue}}{{RGB}}{{72, 133, 237}}
\\definecolor{{ProfessionalGold}}{{RGB}}{{251, 188, 52}}
\\definecolor{{ProfessionalGray}}{{RGB}}{{107, 114, 126}}

\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}

% Enhanced section formatting
\\titleformat{{\\section}}{{\\Large\\bfseries\\color{{ProfessionalNavy}}}}{{}}{{0em}}{{}}[{{\\color{{ProfessionalGold}}\\titlerule[2pt]}}]
\\titlespacing*{{\\section}}{{0pt}}{{2ex}}{{1.5ex}}

\\begin{{document}}

% Enhanced professional header
\\begin{{center}}
{{\\LARGE\\bfseries\\color{{ProfessionalNavy}} {frontmatter.get('name', 'Ronald Reck').upper()}}}\\\\[0.2in]
{{\\large\\color{{ProfessionalBlue}} {frontmatter.get('target_role', 'Distinguished AI Architect \\& Technology Strategist')}}}\\\\[0.1in]
\\textcolor{{ProfessionalGray}}{{\\rule{{5in}}{{1pt}}}}\\\\[0.1in]
\\textcolor{{ProfessionalGray}}{{{frontmatter.get('email', 'rreck@rrecktek.com')} $\\bullet$ {frontmatter.get('phone', '248-444-0835')} $\\bullet$ {frontmatter.get('address', 'Clifton, VA 20124')}}}\\\\
\\textcolor{{ProfessionalGray}}{{{frontmatter.get('website', 'www.rrecktek.com')} $\\bullet$ {frontmatter.get('linkedin', 'linkedin.com/in/ronaldreck')}}}
\\end{{center}}

\\section{{Executive Summary}}
\\textcolor{{ProfessionalGray}}{{{self._clean_text(sections.get('Professional Summary', '')[:450])}}}

\\section{{Strategic Leadership Experience}}
\\textbf{{\\color{{ProfessionalBlue}} Subject Matter Expert}} \\hfill \\textcolor{{ProfessionalGold}}{{\\textbf{{Sep 2023 -- Current}}}}\\\\
\\textbf{{Technica Corporation (FBI Assignment)}} - Washington, DC\\\\
\\begin{{itemize}}[noitemsep,leftmargin=*]
\\item Achieved Service Award within 90 days of assignment
\\item Enterprise-wide AI strategy and implementation leadership
\\item Cross-functional team coordination across multiple security enclaves
\\item Advanced AI applications in federal law enforcement context
\\end{{itemize}}

\\textbf{{\\color{{ProfessionalBlue}} Senior Technology Advisor}} \\hfill \\textcolor{{ProfessionalGold}}{{\\textbf{{May 2020 -- June 2021}}}}\\\\
\\textbf{{Department of Defense (Joint AI Center)}} - Pentagon\\\\
\\begin{{itemize}}[noitemsep,leftmargin=*]
\\item Strategic oversight of AI initiatives with tens of millions in funding
\\item Technical leadership spanning all branches of the military
\\item Designed NLP pipeline for mission-critical "successful" projects
\\item Security hardening protocols for cloud-based R development environments
\\end{{itemize}}

\\textbf{{\\color{{ProfessionalBlue}} Founder \\& Principal Consultant}} \\hfill \\textcolor{{ProfessionalGold}}{{\\textbf{{Sep 2009 -- Present}}}}\\\\
\\textbf{{RRecktek LLC}} - Global Operations\\\\
\\begin{{itemize}}[noitemsep,leftmargin=*]
\\item Built and scaled consulting practice serving 100+ enterprise clients
\\item Published commercial AI software with 8+ years continuous market presence
\\item Specialized expertise in generative AI and enterprise cloud architecture
\\item Notable clients: Johnson \\& Johnson, DHS, DTIC, Eastman Kodak
\\end{{itemize}}

\\section{{Core Technology Expertise}}
\\begin{{multicols}}{{2}}
\\textbf{{\\color{{ProfessionalNavy}} Artificial Intelligence}}\\\\
$\\bullet$ Generative AI \\& Large Language Models\\\\
$\\bullet$ Machine Learning \\& Deep Learning\\\\
$\\bullet$ Natural Language Processing\\\\
$\\bullet$ Computer Vision \\& Pattern Recognition\\\\
$\\bullet$ Predictive Analytics \\& Data Science

\\textbf{{\\color{{ProfessionalNavy}} Enterprise Architecture}}\\\\
$\\bullet$ Amazon Web Services (18+ years)\\\\
$\\bullet$ Cloud-Native Solutions \\& Microservices\\\\
$\\bullet$ DevOps \\& Container Orchestration\\\\
$\\bullet$ Enterprise Security \\& Compliance\\\\
$\\bullet$ Scalable System Design
\\end{{multicols}}

\\section{{Distinguished Achievements}}
\\begin{{itemize}}[noitemsep]
\\item \\textbf{{\\color{{ProfessionalBlue}} FBI Service Award}} - Exceptional performance within first 90 days of federal assignment
\\item \\textbf{{\\color{{ProfessionalBlue}} AWS Marketplace Publisher}} - 11 data products continuously online since 2019
\\item \\textbf{{\\color{{ProfessionalBlue}} Commercial AI Pioneer}} - Predictive Analytics Framework launched 2015
\\item \\textbf{{\\color{{ProfessionalBlue}} Industry Recognition}} - W3C Invited Expert, Published Author (McGraw Hill)
\\end{{itemize}}

\\section{{Security Credentials \\& Education}}
\\textbf{{\\color{{ProfessionalGold}} Security Clearance:}} {frontmatter.get('clearance', 'Active DoD Top Secret Clearance with FBI Counterintelligence Polygraph')}

\\textbf{{\\color{{ProfessionalGold}} Education:}}\\\\
Master of Arts, English Linguistics - Eastern Michigan University (2007)\\\\
Bachelor of Arts, English Linguistics - Wayne State University (1992)

\\end{{document}}"""

        output_file = output_dir / "resume_22_enhanced_professional.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

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

    def generate_new_formats(self):
        """Generate the 3 new resume formats"""
        frontmatter, markdown_content = self.load_resume_data()
        sections = self.extract_sections(markdown_content)
        
        generated_resumes = []
        
        # Create output directory
        output_dir = self.output_dir / "3_new_formats"
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Generating 3 new resume formats based on added templates")
        logger.info(f"Output directory: {output_dir}")
        
        # Generate the 3 new formats
        new_formats = [
            ("Business Insider Style", self.create_format_20_business_insider_style),
            ("Creative Hipster", self.create_format_21_creative_hipster),
            ("Enhanced Professional", self.create_format_22_enhanced_professional)
        ]
        
        for format_name, create_func in new_formats:
            try:
                tex_file = create_func(frontmatter, sections, output_dir)
                pdf_file = self.compile_latex(tex_file)
                if pdf_file:
                    generated_resumes.append((format_name, pdf_file))
                    logger.info(f"Generated: {format_name}")
                else:
                    logger.warning(f"Failed to compile: {format_name}")
            except Exception as e:
                logger.error(f"Error generating {format_name}: {e}")
        
        logger.info(f"Generated {len(generated_resumes)} new distinct resume formats")
        return generated_resumes

if __name__ == "__main__":
    generator = NewFormatsGenerator()
    resumes = generator.generate_new_formats()
    
    print(f"\\n🎯 Generated {len(resumes)} new resume formats based on your added templates:")
    for i, (name, pdf_path) in enumerate(resumes, 20):
        print(f"   {i:2d}. {name}: {pdf_path.name}")
        
    if len(resumes) > 0:
        print(f"\\n📁 New resumes saved in: {resumes[0][1].parent}")
        print(f"\\n✨ These are inspired by the 3 ZIP templates you added:")
        print("   • Recreating_Business_Insider_s_CV_of_Marissa_Mayer__1_.zip")
        print("   • Simple_Hipster_CV__5_.zip") 
        print("   • AltaCV_Template__2_.zip")
        print(f"\\n🎉 You now have {19 + len(resumes)} total distinct resume formats!")
    else:
        print("\\n❌ No new resumes were successfully generated.")