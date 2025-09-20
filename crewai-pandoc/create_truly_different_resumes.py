#!/usr/bin/env python3
"""
Create TRULY Different Resume Formats
Each one will have completely different visual appearance, layout, colors, and styling
"""

import os
import subprocess
import logging
import shutil
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrulyDifferentResumes:
    """Generate resumes that are actually visually different"""
    
    def __init__(self):
        self.output_dir = Path("./output")
        self.output_dir.mkdir(exist_ok=True)
        self.results = {"successful": [], "failed": []}
        
        # Resume data
        self.name = "Ronald P. Reck"
        self.title = "Senior AI Architect & Technical Specialist"
        self.phone = "248-444-0835"
        self.email = "rreck@rrecktek.com"
        self.website = "www.rrecktek.com"
        self.address = "Clifton, VA 20124"
        
        self.summary = "AI professional with specialization in Generative AI. Author of commercial ARTIFICIAL INTELLIGENCE software Predictive Analytics Framework on Amazon Web Service Marketplace. 18+ Years of Amazon Web Services experience. AWS Marketplace publisher of 11 data products that have been online since 2019."
        
        self.skills = [
            "Python", "TensorFlow", "PyTorch", "langchain", "AWS (18+ years)", 
            "Docker", "Kubernetes", "Machine Learning", "NLP", "Computer Vision",
            "Generative AI", "LLMs", "DevOps", "Prometheus", "Grafana"
        ]
        
        self.experience = [
            {
                "company": "Technica Corporation",
                "title": "Subject Matter Expert",
                "dates": "2023 - Present",
                "location": "FBI Headquarters",
                "items": [
                    "Service Award within 90 days of service",
                    "Onsite at Federal Bureau of Investigation - global admin",
                    "Granted VAR with CI-Poly clearance",
                    "Enterprise application support across enclaves"
                ]
            },
            {
                "company": "RRecktek LLC",
                "title": "Principal Consultant & Founder",
                "dates": "2009 - Present", 
                "location": "Remote",
                "items": [
                    "100+ confidential clients including Johnson & Johnson, DHS, DoD",
                    "Designed generative AI capability for Immigration L-1 Visas using local LLM",
                    "Implemented GAN for luxury brand counterfeit detection",
                    "Created NLP processing pipeline for abstractive/extractive NER",
                    "Designed semantic modeling for FDA FAERS (25MM records, 252GB)"
                ]
            },
            {
                "company": "SanCorpConsulting",
                "title": "Chief Technology Officer",
                "dates": "2020 - 2021",
                "location": "DoD Joint AI Center",
                "items": [
                    "Senior Technology Advisor at Department of Defense JAIC",
                    "Data Science oversight on projects with tens of millions in funding",
                    "Designed NLP pipeline for projects receiving additional funding"
                ]
            }
        ]
        
        self.education = [
            {
                "school": "Eastern Michigan University",
                "degree": "Master of Arts",
                "field": "English Linguistics",
                "year": "2007",
                "details": "Computational linguistics, morphology/syntax, theoretical syntax, NLP"
            },
            {
                "school": "Wayne State University", 
                "degree": "Bachelor of Arts",
                "field": "English Linguistics",
                "year": "1992",
                "details": "Theoretical syntax, morphology, semantics"
            }
        ]

    def create_timeline_cv(self) -> str:
        """Modern timeline CV with sidebar - AltaCV style"""
        exp_text = ""
        for exp in self.experience:
            exp_text += f"\\\\cvevent{{{exp['title']}}}{{{exp['company']}}}{{{exp['dates']}}}{{{exp['location']}}}\\n"
            exp_text += "\\\\begin{itemize}\\n"
            for item in exp['items']:
                exp_text += f"\\\\item {item}\\n"
            exp_text += "\\\\end{itemize}\\n\\\\divider\\n\\n"
        
        skills_tags = ""
        for skill in self.skills[:10]:  # First 10 skills
            skills_tags += f"\\\\cvtag{{{skill}}}\\n"
        
        return f"""\\documentclass[10pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{tikz}}
\\usepackage{{paracol}}
\\usepackage{{fontawesome}}
\\usepackage{{enumitem}}

\\geometry{{left=1cm,right=1cm,top=1.5cm,bottom=1.5cm}}

\\definecolor{{primarycolor}}{{RGB}}{{0,120,215}}
\\definecolor{{darkcolor}}{{RGB}}{{45,45,45}}
\\definecolor{{lightgray}}{{RGB}}{{240,240,240}}

\\newcommand{{\\cvtag}}[1]{{\\colorbox{{primarycolor}}{{\\textcolor{{white}}{{\\small #1}}}}\\hspace{{2pt}}}}
\\newcommand{{\\cvevent}}[4]{{\\textbf{{\\large #1}} \\hfill {{\\color{{primarycolor}} #3}}\\\\
\\textit{{#2}} \\hfill {{\\small #4}}\\\\[0.3em]}}
\\newcommand{{\\divider}}{{\\vspace{{0.5em}}\\textcolor{{primarycolor}}{{\\rule{{\\linewidth}}{{1pt}}}}\\vspace{{0.5em}}}}

\\pagestyle{{empty}}

\\begin{{document}}

\\begin{{paracol}}{{2}}

\\columnratio{{0.65}}

% LEFT COLUMN
\\textbf{{\\Huge \\color{{primarycolor}} {self.name}}}\\\\[0.3em]
{{\\Large \\color{{darkcolor}} {self.title}}}\\\\[1em]

\\section*{{\\color{{primarycolor}} PROFESSIONAL SUMMARY}}
{self.summary}\\\\[1em]

\\section*{{\\color{{primarycolor}} EXPERIENCE}}
{exp_text}

\\switchcolumn

% RIGHT COLUMN (SIDEBAR)
\\colorbox{{lightgray}}{{\\begin{{minipage}}{{\\columnwidth}}
\\vspace{{1em}}

\\section*{{\\textbf{{CONTACT}}}}
\\faPhone\\hspace{{0.5em}} {self.phone}\\\\
\\faEnvelope\\hspace{{0.5em}} {self.email}\\\\
\\faGlobe\\hspace{{0.5em}} {self.website}\\\\
\\faMapMarker\\hspace{{0.5em}} {self.address}\\\\[1em]

\\section*{{\\textbf{{SKILLS}}}}
{skills_tags}\\\\[1em]

\\section*{{\\textbf{{EDUCATION}}}}
\\textbf{{{self.education[0]['degree']}}}\\\\
{self.education[0]['school']} ({self.education[0]['year']})\\\\
{self.education[0]['field']}\\\\[0.5em]

\\textbf{{{self.education[1]['degree']}}}\\\\
{self.education[1]['school']} ({self.education[1]['year']})\\\\
{self.education[1]['field']}\\\\[1em]

\\section*{{\\textbf{{CLEARANCE}}}}
DoD Top Secret\\\\
FBI Counterintelligence Polygraph

\\vspace{{1em}}
\\end{{minipage}}}}

\\end{{paracol}}

\\end{{document}}"""

    def create_modern_deedy_style(self) -> str:
        """Modern Deedy-style resume"""
        exp_text = ""
        for exp in self.experience:
            exp_text += f"\\\\runsubsection{{{exp['company']}}}\\n"
            exp_text += f"\\\\descript{{| {exp['title']} }}\\n"
            exp_text += f"\\\\location{{{exp['dates']} | {exp['location']}}}\\n"
            exp_text += "\\\\begin{tightemize}\\n"
            for item in exp['items']:
                exp_text += f"\\\\item {item}\\n"
            exp_text += "\\\\end{tightemize}\\n\\\\sectionsep\\n\\n"
        
        return f"""\\documentclass[letterpaper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{titlesec}}
\\usepackage{{enumitem}}
\\usepackage{{multicol}}

\\geometry{{top=0.5in,bottom=0.5in,left=0.5in,right=0.5in}}

\\definecolor{{primary}}{{RGB}}{{220,50,47}}
\\definecolor{{headings}}{{RGB}}{{108,108,108}}
\\definecolor{{subheadings}}{{RGB}}{{88,88,88}}

% Custom commands
\\newcommand{{\\namesection}}[3]{{\\centering{{
\\fontsize{{30pt}}{{30pt}}\\selectfont \\color{{primary}} #1 \\textbf{{#2}}
}} \\\\[5pt]
\\centering{{\\color{{headings}} #3}}\\\\[10pt]}}

\\newcommand{{\\runsubsection}}[1]{{\\color{{subheadings}}\\textbf{{\\uppercase{{#1}}}}}}
\\newcommand{{\\descript}}[1]{{\\color{{subheadings}}\\raggedright\\scshape\\fontsize{{11pt}}{{13pt}}\\selectfont #1}}
\\newcommand{{\\location}}[1]{{\\color{{headings}}\\raggedright\\fontsize{{10pt}}{{12pt}}\\selectfont #1}}
\\newcommand{{\\sectionsep}}{{\\vspace{{8pt}}}}

\\newenvironment{{tightemize}}{{\\vspace{{-\\topsep}}\\begin{{itemize}}\\itemsep1pt \\parskip0pt \\parsep0pt}}{{\\end{{itemize}}\\vspace{{-\\topsep}}}}

\\pagestyle{{empty}}

\\begin{{document}}

\\namesection{{{self.name.split()[0]}}}{{{' '.join(self.name.split()[1:])}}}{{{self.phone} | {self.email} | {self.website}}}

\\begin{{minipage}}[t]{{0.33\\textwidth}}

\\section{{Education}}
\\runsubsection{{{self.education[0]['school']}}}\\\\
\\descript{{{self.education[0]['degree']} in {self.education[0]['field']}}}\\\\
\\location{{{self.education[0]['year']}}}\\\\
\\sectionsep

\\runsubsection{{{self.education[1]['school']}}}\\\\
\\descript{{{self.education[1]['degree']} in {self.education[1]['field']}}}\\\\
\\location{{{self.education[1]['year']}}}\\\\
\\sectionsep

\\section{{Skills}}
\\runsubsection{{Programming}}\\\\
\\location{{Expert:}}
Python \\textbullet{{}} TensorFlow \\textbullet{{}} PyTorch \\\\
AWS \\textbullet{{}} Docker \\textbullet{{}} Kubernetes \\\\
\\location{{Proficient:}}
R \\textbullet{{}} Shell \\textbullet{{}} SQL \\textbullet{{}} Perl \\\\
\\sectionsep

\\runsubsection{{AI/ML}}\\\\
Machine Learning \\textbullet{{}} NLP \\\\
Computer Vision \\textbullet{{}} Generative AI \\\\
LLMs \\textbullet{{}} Deep Learning \\\\
\\sectionsep

\\section{{Clearance}}
\\textbf{{DoD Top Secret}}\\\\
FBI Counterintelligence Polygraph\\\\
\\sectionsep

\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{0.66\\textwidth}}

\\section{{Experience}}
{exp_text}

\\section{{Recent AI Projects}}
\\runsubsection{{Generative AI Immigration System}}\\\\
\\descript{{| Local LLM Implementation}}\\\\
\\location{{2024}}\\\\
Designed and implemented generative AI capability for Immigration L-1 Visas using local large language models.\\\\
\\sectionsep

\\runsubsection{{Luxury Brand Protection}}\\\\
\\descript{{| GAN-based Detection}}\\\\
\\location{{2024}}\\\\
Implemented Generative Adversarial Network for luxury brands to detect counterfeit products.\\\\
\\sectionsep

\\end{{minipage}}

\\end{{document}}"""

    def create_classic_academic_cv(self) -> str:
        """Classic academic CV with clean typography"""
        exp_text = ""
        for exp in self.experience:
            exp_text += f"\\\\cventry{{{exp['dates']}}}{{{exp['title']}}}{{{exp['company']}}}{{{exp['location']}}}{{}}{{\\n"
            for item in exp['items']:
                exp_text += f"\\\\item {item}\\n"
            exp_text += "}\\n\\n"
        
        return f"""\\documentclass[11pt,a4paper,sans]{{moderncv}}

\\moderncvstyle{{classic}}
\\moderncvcolor{{blue}}

\\usepackage[scale=0.75]{{geometry}}

\\name{{{self.name.split()[0]}}}{{{' '.join(self.name.split()[1:])})}}
\\title{{{self.title}}}
\\address{{{self.address}}}{{USA}}
\\phone[mobile]{{{self.phone}}}
\\email{{{self.email}}}
\\homepage{{{self.website}}}
\\extrainfo{{DoD Top Secret Clearance}}

\\begin{{document}}

\\makecvtitle

\\section{{Professional Summary}}
\\cvitem{{}}{{{self.summary}}}

\\section{{Experience}}
{exp_text}

\\section{{Education}}
\\cventry{{{self.education[0]['year']}}}{{{self.education[0]['degree']}}}{{{self.education[0]['school']}}}{{}}{{Linguistics}}{{{self.education[0]['details']}}}
\\cventry{{{self.education[1]['year']}}}{{{self.education[1]['degree']}}}{{{self.education[1]['school']}}}{{}}{{Linguistics}}{{{self.education[1]['details']}}}

\\section{{Technical Skills}}
\\cvdoubleitem{{AI/ML}}{{TensorFlow, PyTorch, NLP, Computer Vision}}{{Cloud}}{{AWS (18+ years), Docker, Kubernetes}}
\\cvdoubleitem{{Programming}}{{Python, R, Perl, Shell, SQL}}{{DevOps}}{{Prometheus, Grafana, CI/CD}}

\\section{{Security Clearance}}
\\cvitem{{Level}}{{DoD Top Secret with FBI Counterintelligence Polygraph}}

\\end{{document}}"""

    def create_minimalist_design(self) -> str:
        """Ultra-minimalist resume design"""
        exp_text = ""
        for exp in self.experience:
            exp_text += f"{exp['title']}, {exp['company']} ({exp['dates']})\\n"
            for item in exp['items']:
                exp_text += f"• {item}\\n"
            exp_text += "\\n"
        
        return f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{geometry}}
\\usepackage{{enumitem}}

\\geometry{{margin=1.2in}}
\\setlist[itemize]{{leftmargin=0em,itemsep=0.1em,label=--}}
\\pagestyle{{empty}}

\\begin{{document}}

{self.name}

{self.address} | {self.phone} | {self.email} | {self.website}

{self.summary}

EXPERIENCE

{exp_text}

EDUCATION

{self.education[0]['degree']}, {self.education[0]['school']} ({self.education[0]['year']})
{self.education[1]['degree']}, {self.education[1]['school']} ({self.education[1]['year']})

SKILLS

{', '.join(self.skills)}

CLEARANCE

DoD Top Secret with FBI Counterintelligence Polygraph

\\end{{document}}"""

    def create_colorful_creative(self) -> str:
        """Colorful creative design with graphics"""
        return f"""\\documentclass[10pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{tikz}}
\\usepackage{{fontawesome}}
\\usepackage{{enumitem}}

\\geometry{{margin=0.5in}}

\\definecolor{{maincolor}}{{RGB}}{{128,0,128}}
\\definecolor{{accentcolor}}{{RGB}}{{255,165,0}}
\\definecolor{{textcolor}}{{RGB}}{{64,64,64}}

\\pagestyle{{empty}}

\\begin{{document}}

% Header with colored background
\\begin{{tikzpicture}}[remember picture,overlay]
\\fill[maincolor] (current page.north west) rectangle ([yshift=-3cm]current page.north east);
\\end{{tikzpicture}}

\\vspace{{1cm}}
\\color{{white}}
{{\\Huge\\textbf{{{self.name}}}}}\\\\[0.3em]
{{\\Large {self.title}}}
\\vspace{{2cm}}

\\color{{textcolor}}

\\begin{{minipage}}[t]{{0.35\\textwidth}}
\\colorbox{{accentcolor!20}}{{\\begin{{minipage}}{{\\textwidth}}
\\vspace{{0.5em}}

\\section*{{\\color{{maincolor}} CONTACT}}
\\faPhone\\hspace{{0.5em}} {self.phone}\\\\
\\faEnvelope\\hspace{{0.5em}} {self.email}\\\\
\\faGlobe\\hspace{{0.5em}} {self.website}\\\\
\\faMapMarker\\hspace{{0.5em}} {self.address}\\\\[1em]

\\section*{{\\color{{maincolor}} SKILLS}}
\\begin{{itemize}}[leftmargin=1em]
\\item Python, TensorFlow, PyTorch
\\item AWS (18+ years experience)
\\item Machine Learning, NLP
\\item Generative AI, LLMs
\\item Docker, Kubernetes
\\item DevOps, Prometheus
\\end{{itemize}}

\\section*{{\\color{{maincolor}} CLEARANCE}}
\\textbf{{DoD Top Secret}}\\\\
FBI Counterintelligence Polygraph

\\vspace{{0.5em}}
\\end{{minipage}}}}
\\end{{minipage}}%
\\hfill
\\begin{{minipage}}[t]{{0.6\\textwidth}}

\\section*{{\\color{{maincolor}} SUMMARY}}
{self.summary}\\\\[1em]

\\section*{{\\color{{maincolor}} EXPERIENCE}}

\\textbf{{\\large Subject Matter Expert}} \\hfill {{\\color{{maincolor}} 2023 - Present}}\\\\
\\textit{{Technica Corporation, FBI Headquarters}}\\\\
Service Award within 90 days. FBI global admin with CI-Poly clearance.\\\\[0.5em]

\\textbf{{\\large Principal Consultant \\& Founder}} \\hfill {{\\color{{maincolor}} 2009 - Present}}\\\\
\\textit{{RRecktek LLC, Remote}}\\\\
100+ confidential clients. Designed generative AI solutions and cloud architecture.\\\\[0.5em]

\\textbf{{\\large Chief Technology Officer}} \\hfill {{\\color{{maincolor}} 2020 - 2021}}\\\\
\\textit{{SanCorpConsulting, DoD JAIC}}\\\\
Senior Technology Advisor at Department of Defense Joint AI Center.\\\\[1em]

\\section*{{\\color{{maincolor}} EDUCATION}}
\\textbf{{{self.education[0]['degree']}}} \\hfill {self.education[0]['year']}\\\\
{self.education[0]['school']}\\\\
{self.education[0]['field']}\\\\[0.3em]

\\textbf{{{self.education[1]['degree']}}} \\hfill {self.education[1]['year']}\\\\
{self.education[1]['school']}\\\\
{self.education[1]['field']}

\\end{{minipage}}

\\end{{document}}"""

    def compile_resume(self, latex_content: str, template_name: str, description: str) -> bool:
        """Compile LaTeX content to PDF"""
        work_dir = Path(f"./work_{int(time.time())}_{template_name}")
        work_dir.mkdir(exist_ok=True)
        
        try:
            # Write LaTeX file
            tex_file = work_dir / f"{template_name}.tex"
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # Try compilation
            engines = ['pdflatex', 'xelatex', 'lualatex']
            
            for engine in engines:
                try:
                    logger.info(f"🔄 Compiling {template_name} with {engine}")
                    
                    cmd = [
                        engine,
                        '-interaction=nonstopmode',
                        '-output-directory', str(work_dir),
                        str(tex_file)
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    
                    pdf_file = work_dir / f"{template_name}.pdf"
                    if pdf_file.exists() and pdf_file.stat().st_size > 5000:
                        # Copy to output
                        output_pdf = self.output_dir / f"ronald-reck-DIFFERENT-{template_name}.pdf"
                        shutil.copy2(pdf_file, output_pdf)
                        
                        file_size = output_pdf.stat().st_size
                        logger.info(f"✅ SUCCESS: {template_name} with {engine} ({file_size/1024:.1f}KB)")
                        
                        self.results["successful"].append({
                            "template": template_name,
                            "description": description,
                            "output_file": str(output_pdf),
                            "size": file_size,
                            "engine": engine
                        })
                        return True
                        
                except subprocess.TimeoutExpired:
                    continue
                except Exception:
                    continue
            
            logger.warning(f"❌ FAILED: {template_name}")
            self.results["failed"].append({"template": template_name, "description": description})
            return False
            
        finally:
            if work_dir.exists():
                try:
                    shutil.rmtree(work_dir)
                except:
                    pass

    def generate_truly_different_resumes(self):
        """Generate genuinely different resume designs"""
        logger.info("🚀 Creating TRULY DIFFERENT resume designs...")
        
        templates = [
            ("Timeline_Sidebar", self.create_timeline_cv(), "Modern timeline CV with blue sidebar - AltaCV inspired"),
            ("Modern_Deedy", self.create_modern_deedy_style(), "Modern two-column Deedy-style with red accents"),
            ("Academic_Classic", self.create_classic_academic_cv(), "Classic academic CV using moderncv class"), 
            ("Minimalist_Clean", self.create_minimalist_design(), "Ultra-minimalist text-only design"),
            ("Creative_Colorful", self.create_colorful_creative(), "Colorful creative design with purple/orange theme")
        ]
        
        for template_name, latex_content, description in templates:
            success = self.compile_resume(latex_content, template_name, description)
            time.sleep(0.5)
        
        self.print_results()
    
    def print_results(self):
        """Print generation results"""
        successful = len(self.results["successful"])
        failed = len(self.results["failed"])
        total = successful + failed
        
        print("\\n📊 TRULY DIFFERENT RESUME GENERATION RESULTS")
        print("=" * 55)
        print(f"📋 Templates Created: {total}")
        print(f"✅ Successfully Generated: {successful}")
        print(f"❌ Failed: {failed}")
        
        if self.results["successful"]:
            print("\\n✅ TRULY DIFFERENT RESUME DESIGNS:")
            print("-" * 45)
            for result in self.results["successful"]:
                size_kb = result["size"] / 1024
                engine = result["engine"]
                print(f"  📄 {result['template']}.pdf ({size_kb:.1f}KB) [{engine}]")
                print(f"      {result['description']}")
                print()
        
        print(f"\\n📁 Files are in: {self.output_dir}")
        print("🎨 Each PDF is VISUALLY DIFFERENT with unique layouts, colors, and designs!")

def main():
    generator = TrulyDifferentResumes()
    generator.generate_truly_different_resumes()
    return 0

if __name__ == "__main__":
    exit(main())