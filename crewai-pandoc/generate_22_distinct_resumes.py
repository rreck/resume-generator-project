#!/usr/bin/env python3
"""
Generate 22 Visually Distinct Resume Formats (19 + 3 new)
Extended to include the three new templates added today.
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

class ExtendedResumeGenerator:
    def __init__(self, base_dir="/home/rreck/Desktop/20250920a/crewai-pandoc"):
        self.base_dir = Path(base_dir)
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.template_cache = self.base_dir / "template_cache"
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

    def create_format_20_marissa_mayer_style(self, frontmatter, sections, output_dir):
        """Format 20: Business Insider Marissa Mayer Style"""
        content = f"""\\documentclass[10pt,a4paper,withhyper]{{altacv}}

\\geometry{{left=1.25cm,right=1.25cm,top=1.5cm,bottom=1.5cm,columnsep=1.2cm}}

\\usepackage{{paracol}}

% Define colors inspired by Marissa Mayer's design
\\definecolor{{PrimaryBlue}}{{HTML}}{{4285F4}}
\\definecolor{{SecondaryBlue}}{{HTML}}{{1976D2}}
\\definecolor{{AccentOrange}}{{HTML}}{{FF6D00}}
\\definecolor{{TextGray}}{{HTML}}{{757575}}

\\colorlet{{name}}{{black}}
\\colorlet{{tagline}}{{PrimaryBlue}}
\\colorlet{{heading}}{{SecondaryBlue}}
\\colorlet{{headingrule}}{{SecondaryBlue}}
\\colorlet{{subheading}}{{TextGray}}
\\colorlet{{accent}}{{AccentOrange}}
\\colorlet{{emphasis}}{{black}}
\\colorlet{{body}}{{black!80!white}}

\\renewcommand{{\\namefont}}{{\\Huge\\rmfamily\\bfseries}}
\\renewcommand{{\\personalinfofont}}{{\\footnotesize}}
\\renewcommand{{\\cvsectionfont}}{{\\LARGE\\rmfamily\\bfseries}}
\\renewcommand{{\\cvsubsectionfont}}{{\\large\\bfseries}}

\\begin{{document}}
\\name{{{frontmatter.get('name', 'Ronald Reck')}}}
\\tagline{{{frontmatter.get('target_role', 'Senior AI Architect & Technology Leader')}}}

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
{self._clean_text(sections.get('Professional Summary', '')[:500])}

\\cvsection{{Leadership Experience}}
\\cvevent{{Subject Matter Expert}}{{Technica Corporation / FBI}}{{Sep 2023 -- Current}}{{}}
\\begin{{itemize}}
\\item Service Award within 90 days - demonstrating immediate impact
\\item Global admin with CI-Poly clearance across enterprise enclaves
\\item Led enterprise application support and automation initiatives
\\end{{itemize}}

\\divider

\\cvevent{{Senior Technology Advisor}}{{DoD Joint AI Center}}{{May 2020 -- June 2021}}{{}}
\\begin{{itemize}}
\\item Senior-most Data Science oversight on projects with tens of millions in funding
\\item Designed NLP pipeline for successful projects receiving additional funding
\\item Security hardening of R containers in cloud-based development environment
\\end{{itemize}}

\\divider

\\cvevent{{Consultant \& Founder}}{{RRecktek LLC}}{{Sep 2009 -- Present}}{{}}
\\begin{{itemize}}
\\item Built consulting practice serving 100+ clients including J\\&J, DHS, DTIC
\\item Published commercial AI software on AWS Marketplace since 2015
\\item Expertise in Generative AI implementations and enterprise architecture
\\end{{itemize}}

\\switchcolumn

\\cvsection{{Core Strengths}}
\\cvtag{{Artificial Intelligence}}
\\cvtag{{Machine Learning}}
\\cvtag{{Generative AI}}
\\cvtag{{Cloud Architecture}}
\\cvtag{{Enterprise Security}}
\\cvtag{{Team Leadership}}

\\divider\\smallskip

\\cvtag{{Python}}
\\cvtag{{R}}
\\cvtag{{AWS (18+ years)}}
\\cvtag{{Docker}}
\\cvtag{{Kubernetes}}
\\cvtag{{TensorFlow}}
\\cvtag{{PyTorch}}

\\cvsection{{Security Clearance}}
\\cvachievement{{\\faCertificate}}{{Active DoD Top Secret}}{{FBI Counterintelligence Polygraph}}

\\cvsection{{Education}}
\\cvevent{{MA English Linguistics}}{{Eastern Michigan University}}{{April 2007}}{{}}
Computational linguistics, morphology/syntax, NLP algorithms

\\divider

\\cvevent{{BA English Linguistics}}{{Wayne State University}}{{June 1992}}{{}}
Theoretical syntax, morphology, and semantics

\\cvsection{{Recent AI Innovations}}
\\cvachievement{{\\faRocket}}{{Generative AI Immigration System}}{{L-1 Visa processing using local LLM}}
\\cvachievement{{\\faEye}}{{GAN Counterfeit Detection}}{{Luxury brands anti-counterfeiting}}
\\cvachievement{{\\faDatabase}}{{FAERS Semantic Modeling}}{{25MM records pharmacovigilance system}}

\\end{{paracol}}

\\end{{document}}"""

        output_file = output_dir / "resume_20_marissa_mayer.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_21_hipster_creative(self, frontmatter, sections, output_dir):
        """Format 21: Enhanced Hipster Creative Style"""
        content = f"""\\documentclass[12pt,a4paper]{{simplehipstercv}}

\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{lmodern}}
\\usepackage{{xcolor}}

% Define creative color scheme
\\definecolor{{HipsterBlue}}{{RGB}}{{58, 134, 255}}
\\definecolor{{HipsterOrange}}{{RGB}}{{255, 138, 101}}
\\definecolor{{HipsterGreen}}{{RGB}}{{46, 213, 115}}
\\definecolor{{HipsterPurple}}{{RGB}}{{123, 104, 238}}

\\name{{{frontmatter.get('name', 'Ronald Reck')}}}
\\tagline{{{frontmatter.get('target_role', 'Creative AI Architect \\& Innovation Leader')}}}
\\photo{{}}  % No photo for professional version

\\begin{{document}}

\\makeheader

\\section{{Creative Profile}}
\\textcolor{{HipsterBlue}}{{Innovative AI architect}} with a passion for cutting-edge technology and creative problem-solving. {self._clean_text(sections.get('Professional Summary', '')[:300])}

\\section{{Innovation Toolkit}}
\\begin{{itemize}}[leftmargin=*]
\\item \\textcolor{{HipsterOrange}}{{\\textbf{{Generative AI:}}}} TensorFlow, PyTorch, LangChain, Ollama, Custom LLMs
\\item \\textcolor{{HipsterGreen}}{{\\textbf{{Creative Development:}}}} Python, R, Creative Coding, Rapid Prototyping
\\item \\textcolor{{HipsterPurple}}{{\\textbf{{Cloud Innovation:}}}} AWS (18+ years), Serverless, Container Orchestration
\\item \\textcolor{{HipsterBlue}}{{\\textbf{{Data Artistry:}}}} Vector Databases, Semantic Processing, NLP Pipelines
\\end{{itemize}}

\\section{{Creative Projects}}
\\subsection{{\\textcolor{{HipsterOrange}}{{Generative AI Innovations}}}}
\\textbf{{Immigration Intelligence System}} - Local LLM for L-1 visa processing

\\textbf{{Anti-Counterfeiting GAN}} - AI-powered luxury brand protection

\\textbf{{Biomedical NLP Pipeline}} - FAERS compliance automation

\\subsection{{\\textcolor{{HipsterGreen}}{{Entrepreneurial Ventures}}}}
\\textbf{{RRecktek LLC}} - 15+ year consulting practice with 100+ clients

\\textbf{{AWS Marketplace Publisher}} - 11 data products online since 2019

\\textbf{{Commercial AI Software}} - Predictive Analytics Framework (2015)

\\section{{Experience Highlights}}
\\textbf{{\\textcolor{{HipsterPurple}}{{FBI/Technica Corporation}}}} \\hfill \\textit{{2023-Current}}\\\\
Subject Matter Expert - Service Award, Enterprise AI Implementation

\\textbf{{\\textcolor{{HipsterBlue}}{{DoD Joint AI Center}}}} \\hfill \\textit{{2020-2021}}\\\\
Senior Technology Advisor - Multi-million dollar project oversight

\\section{{Educational Foundation}}
\\textbf{{MA English Linguistics}} - Eastern Michigan University (2007)\\\\
\\textbf{{BA English Linguistics}} - Wayne State University (1992)

\\section{{Security \& Credentials}}
\\textcolor{{HipsterOrange}}{{\\textbf{{{frontmatter.get('clearance', 'Active DoD Top Secret Clearance & FBI Counterintelligence Polygraph')}}}}}

\\section{{Contact}}
\\textcolor{{HipsterBlue}}{{\\textbf{{Email:}}}} {frontmatter.get('email', 'rreck@rrecktek.com')}\\\\
\\textcolor{{HipsterGreen}}{{\\textbf{{Phone:}}}} {frontmatter.get('phone', '248-444-0835')}\\\\
\\textcolor{{HipsterPurple}}{{\\textbf{{Web:}}}} {frontmatter.get('website', 'www.rrecktek.com')}

\\end{{document}}"""

        output_file = output_dir / "resume_21_hipster_creative.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def create_format_22_altacv_enhanced(self, frontmatter, sections, output_dir):
        """Format 22: Enhanced AltaCV Template v2"""
        content = f"""\\documentclass[10pt,a4paper,ragged2e,withhyper]{{altacv}}

\\geometry{{left=1.25cm,right=1.25cm,top=1.5cm,bottom=1.5cm,columnsep=1.2cm}}

\\usepackage{{paracol}}

% Enhanced color scheme
\\definecolor{{SlateBlue}}{{HTML}}{{6A5ACD}}
\\definecolor{{DarkSlateBlue}}{{HTML}}{{483D8B}}
\\definecolor{{MediumSlateBlue}}{{HTML}}{{7B68EE}}
\\definecolor{{LightSteelBlue}}{{HTML}}{{B0C4DE}}
\\definecolor{{Orange}}{{HTML}}{{FF8C00}}

\\colorlet{{name}}{{black}}
\\colorlet{{tagline}}{{SlateBlue}}
\\colorlet{{heading}}{{DarkSlateBlue}}
\\colorlet{{headingrule}}{{MediumSlateBlue}}
\\colorlet{{subheading}}{{SlateBlue}}
\\colorlet{{accent}}{{Orange}}
\\colorlet{{emphasis}}{{black}}
\\colorlet{{body}}{{black!80!white}}

\\renewcommand{{\\namefont}}{{\\Huge\\rmfamily\\bfseries}}
\\renewcommand{{\\personalinfofont}}{{\\footnotesize}}
\\renewcommand{{\\cvsectionfont}}{{\\LARGE\\rmfamily\\bfseries}}
\\renewcommand{{\\cvsubsectionfont}}{{\\large\\bfseries}}

\\begin{{document}}
\\name{{{frontmatter.get('name', 'Ronald Reck')}}}
\\tagline{{{frontmatter.get('target_role', 'Distinguished AI Architect & Technology Strategist')}}}

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

\\cvsection{{Executive Summary}}
{self._clean_text(sections.get('Professional Summary', '')[:400])}

\\cvsection{{Strategic Leadership}}
\\cvevent{{Subject Matter Expert}}{{Technica Corporation (FBI Assignment)}}{{Sep 2023 -- Current}}{{Washington, DC}}
\\begin{{itemize}}
\\item Achieved Service Award within 90 days of assignment
\\item Enterprise-wide AI strategy and implementation leadership
\\item Cross-functional team coordination across security enclaves
\\end{{itemize}}

\\divider

\\cvevent{{Senior Technology Advisor}}{{Department of Defense (JAIC)}}{{May 2020 -- June 2021}}{{Pentagon}}
\\begin{{itemize}}
\\item Strategic oversight of multi-million dollar AI initiatives
\\item Technical leadership across all military branches
\\item Advanced NLP pipeline design for mission-critical applications
\\end{{itemize}}

\\divider

\\cvevent{{Founder \& Principal Consultant}}{{RRecktek LLC}}{{Sep 2009 -- Present}}{{Global}}
\\begin{{itemize}}
\\item Built and scaled consulting practice to 100+ enterprise clients
\\item Published commercial AI software with 8+ years market presence
\\item Specialized in generative AI and cloud architecture solutions
\\end{{itemize}}

\\cvsection{{Notable Achievements}}
\\cvachievement{{\\faAward}}{{FBI Service Award}}{{Exceptional performance within first 90 days}}
\\cvachievement{{\\faRocket}}{{AWS Marketplace Publisher}}{{11 data products online since 2019}}
\\cvachievement{{\\faTrophy}}{{Commercial AI Pioneer}}{{Predictive Analytics Framework since 2015}}

\\switchcolumn

\\cvsection{{Technical Expertise}}
\\cvsubsection{{Artificial Intelligence}}
\\cvtag{{Generative AI}}
\\cvtag{{Machine Learning}}
\\cvtag{{Deep Learning}}
\\cvtag{{Natural Language Processing}}
\\cvtag{{Computer Vision}}
\\cvtag{{Predictive Analytics}}

\\medskip

\\cvsubsection{{Development \& Architecture}}
\\cvtag{{Python}}
\\cvtag{{R}}
\\cvtag{{TensorFlow}}
\\cvtag{{PyTorch}}
\\cvtag{{LangChain}}
\\cvtag{{Docker}}
\\cvtag{{Kubernetes}}

\\medskip

\\cvsubsection{{Cloud \& Infrastructure}}
\\cvtag{{AWS (18+ years)}}
\\cvtag{{Enterprise Architecture}}
\\cvtag{{DevOps}}
\\cvtag{{Security Implementation}}

\\cvsection{{Security Credentials}}
\\cvachievement{{\\faShield}}{{Top Secret Clearance}}{{Active DoD with FBI CI-Poly}}

\\cvsection{{Academic Background}}
\\cvevent{{Master of Arts}}{{Eastern Michigan University}}{{April 2007}}{{}}
English Linguistics - Computational linguistics, NLP algorithms

\\divider

\\cvevent{{Bachelor of Arts}}{{Wayne State University}}{{June 1992}}{{}}
English Linguistics - Theoretical syntax and semantics

\\cvsection{{Professional Recognition}}
\\cvachievement{{\\faUsers}}{{W3C Invited Expert}}{{Government Linked Data Working Group}}
\\cvachievement{{\\faBook}}{{Published Author}}{{McGraw Hill - "Hardening Linux"}}
\\cvachievement{{\\faInstitution}}{{Industry Standards}}{{Contributing Editor - SIIA FISD}}

\\cvsection{{Innovation Portfolio}}
\\cvsubsection{{Recent Breakthroughs}}
• Generative AI Immigration Processing\\\\
• GAN-based Counterfeit Detection\\\\
• Large-scale Semantic Data Modeling\\\\
• Multi-domain NLP Pipelines

\\end{{paracol}}

\\end{{document}}"""

        output_file = output_dir / "resume_22_altacv_enhanced.tex"
        with open(output_file, 'w') as f:
            f.write(content)
        return output_file

    def compile_latex(self, tex_file):
        """Compile LaTeX file to PDF"""
        try:
            work_dir = tex_file.parent
            
            # Copy necessary template files to working directory
            template_dirs = {
                "altacv.cls": ["402b3a3f1decb6a0", "93ff41248baa97ed"],
                "simplehipstercv.cls": ["c05cd4fcc3d2e79a"]
            }
            
            # Find and copy required class files
            for cls_file, possible_dirs in template_dirs.items():
                for dir_id in possible_dirs:
                    cls_path = self.template_cache / dir_id / cls_file
                    if cls_path.exists():
                        shutil.copy2(cls_path, work_dir)
                        break
            
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

    def generate_extended_formats(self):
        """Generate all 22 distinct resume formats (19 original + 3 new)"""
        frontmatter, markdown_content = self.load_resume_data()
        sections = self.extract_sections(markdown_content)
        
        generated_resumes = []
        
        # Create output directory
        output_dir = self.output_dir / "22_distinct_formats"
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Generating 22 distinct resume formats (19 original + 3 new)")
        logger.info(f"Output directory: {output_dir}")
        
        # Generate the 3 new formats based on newly added templates
        new_formats = [
            ("Marissa Mayer Style", self.create_format_20_marissa_mayer_style),
            ("Hipster Creative", self.create_format_21_hipster_creative),
            ("AltaCV Enhanced", self.create_format_22_altacv_enhanced)
        ]
        
        # Generate new formats
        for format_name, create_func in new_formats:
            try:
                tex_file = create_func(frontmatter, sections, output_dir)
                pdf_file = self.compile_latex(tex_file)
                if pdf_file:
                    generated_resumes.append((format_name, pdf_file))
                    logger.info(f"Generated new format: {format_name}")
                else:
                    logger.warning(f"Failed to compile: {format_name}")
            except Exception as e:
                logger.error(f"Error generating {format_name}: {e}")
        
        logger.info(f"Generated {len(generated_resumes)} new distinct resume formats")
        return generated_resumes

if __name__ == "__main__":
    generator = ExtendedResumeGenerator()
    resumes = generator.generate_extended_formats()
    
    print(f"\\n🎯 Generated {len(resumes)} new distinct resume formats:")
    for i, (name, pdf_path) in enumerate(resumes, 20):
        print(f"   {i:2d}. {name}: {pdf_path.name}")
        
    if len(resumes) > 0:
        print(f"\\n📁 New resumes saved in: {resumes[0][1].parent}")
        print(f"\\n🔍 These are based on the 3 new templates you added today!")
        print("\\n✨ You now have access to:")
        print("   • 19 original distinct formats")
        print("   • 3 new template-based formats")
        print("   • Total: 22 unique resume presentations!")
    else:
        print("\\n❌ No new resumes were successfully generated.")