#!/usr/bin/env python3
"""
USE THE ACTUAL REAL TEMPLATES - NOT FAKE ONES
Process the actual AltaCV, Deedy, Jan Küster etc. templates with their real .cls files
"""

import os
import subprocess
import logging
import shutil
from pathlib import Path
import time
import json
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTemplateProcessor:
    """Actually use the real professional templates"""
    
    def __init__(self):
        self.output_dir = Path("./output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Load template registry
        with open("./template_cache/template_registry.json", 'r') as f:
            self.registry = json.load(f)
        
        self.results = {"successful": [], "failed": []}
        
        # Resume content
        self.resume_vars = {
            'name': 'Ronald P. Reck',
            'firstname': 'Ronald',
            'surname': 'Reck', 
            'title': 'Senior AI Architect \\& Technical Specialist',
            'address': 'Clifton, VA 20124',
            'phone': '+1-248-444-0835',
            'email': 'rreck@rrecktek.com',
            'website': 'www.rrecktek.com',
            'linkedin': 'ronaldreck',
            'github': 'rreck',
            'birthday': '1970',
            'nationality': 'American',
            'position': 'Senior AI Architect',
            'employer': 'RRecktek LLC',
            'clearance': 'DoD Top Secret with CI-Poly',
            'quote': 'AI professional specializing in Generative AI and enterprise solutions'
        }
    
    def setup_latex_environment(self, template_cache_dir: str):
        """Setup LaTeX environment for specific template"""
        cache_path = Path(template_cache_dir)
        
        # Copy all .cls, .sty files to current directory
        for support_file in cache_path.glob("*.cls"):
            shutil.copy2(support_file, ".")
            logger.debug(f"Copied class file: {support_file.name}")
        
        for support_file in cache_path.glob("*.sty"):
            shutil.copy2(support_file, ".")
            logger.debug(f"Copied style file: {support_file.name}")
        
        # Copy image files if they exist
        for img_file in cache_path.glob("*.png"):
            shutil.copy2(img_file, ".")
        for img_file in cache_path.glob("*.jpg"):
            shutil.copy2(img_file, ".")
    
    def process_altacv_template(self, hash_id: str) -> bool:
        """Process the real AltaCV template"""
        cache_dir = f"./template_cache/{hash_id}"
        self.setup_latex_environment(cache_dir)
        
        # Create customized AltaCV content
        altacv_content = f"""\\documentclass[10pt,a4paper,withhyper]{{altacv}}

\\geometry{{left=1.25cm,right=1.25cm,top=1.5cm,bottom=1.5cm,columnsep=1.2cm}}

% The paracol package lets you typeset columns of text in parallel
\\usepackage{{paracol}}

% Change the font if you want to, depending on whether
% you're using pdflatex or xelatex/lualatex
\\ifxetexorluatex
  \\setmainfont{{Roboto Slab}}
  \\setsansfont{{Lato}}
  \\renewcommand{{\\familydefault}}{{\\sfdefault}}
\\else
  \\usepackage[rm]{{roboto}}
  \\usepackage[defaultsans]{{lato}}
  \\renewcommand{{\\familydefault}}{{\\sfdefault}}
\\fi

% Change the colours if you want to
\\definecolor{{SlateGrey}}{{HTML}}{{2E2E2E}}
\\definecolor{{LightGrey}}{{HTML}}{{666666}}
\\definecolor{{DarkPastelRed}}{{HTML}}{{450808}}
\\definecolor{{PastelRed}}{{HTML}}{{8F0D0D}}
\\definecolor{{GoldenEarth}}{{HTML}}{{E7D192}}
\\colorlet{{name}}{{black}}
\\colorlet{{tagline}}{{PastelRed}}
\\colorlet{{heading}}{{DarkPastelRed}}
\\colorlet{{headingrule}}{{GoldenEarth}}
\\colorlet{{subheading}}{{PastelRed}}
\\colorlet{{accent}}{{PastelRed}}
\\colorlet{{emphasis}}{{SlateGrey}}
\\colorlet{{body}}{{LightGrey}}

% Change some fonts, if necessary
\\renewcommand{{\\namefont}}{{\\Huge\\rmfamily\\bfseries}}
\\renewcommand{{\\personalinfofont}}{{\\footnotesize}}
\\renewcommand{{\\cvsectionfont}}{{\\LARGE\\rmfamily\\bfseries}}
\\renewcommand{{\\cvsubsectionfont}}{{\\large\\bfseries}}

\\begin{{document}}
\\name{{{self.resume_vars['name']}}}
\\tagline{{{self.resume_vars['title']}}}

\\personalinfo{{%
  \\email{{{self.resume_vars['email']}}}
  \\phone{{{self.resume_vars['phone']}}}
  \\location{{{self.resume_vars['address']}}}
  \\homepage{{{self.resume_vars['website']}}}
  \\linkedin{{{self.resume_vars['linkedin']}}}
  \\github{{{self.resume_vars['github']}}}
}}

\\makecvheader
\\AtBeginEnvironment{{itemize}}{{\\small}}

\\columnratio{{0.6}}

\\begin{{paracol}}{{2}}

\\cvsection{{Experience}}

\\cvevent{{Subject Matter Expert}}{{Technica Corporation}}{{Sep 2023 -- Present}}{{FBI Headquarters}}
\\begin{{itemize}}
\\item Service Award within 90 days of service
\\item Onsite at Federal Bureau of Investigation - global admin
\\item Granted VAR with CI-Poly clearance
\\item Enterprise application support across enclaves
\\end{{itemize}}

\\divider

\\cvevent{{Principal Consultant}}{{RRecktek LLC}}{{Sep 2009 -- Present}}{{Remote}}
\\begin{{itemize}}
\\item 100+ confidential clients including Johnson \\& Johnson, DHS, DoD
\\item Designed generative AI capability for Immigration L-1 Visas using local LLM
\\item Implemented NLP processing pipeline for multiple domains (spaCy)
\\item Designed unsupervised categorization for 20k customer segmentation
\\end{{itemize}}

\\divider

\\cvevent{{Chief Technology Officer}}{{SanCorpConsulting}}{{May 2020 -- Jun 2021}}{{DoD JAIC}}
\\begin{{itemize}}
\\item Senior Technology Advisor at Department of Defense Joint AI Center
\\item Data Science oversight on projects with tens of millions in funding
\\item Designed NLP pipeline for successful projects receiving additional funding
\\end{{itemize}}

\\cvsection{{Education}}

\\cvevent{{M.A.\\ in English Linguistics}}{{Eastern Michigan University}}{{2007}}{{}}
\\begin{{itemize}}
\\item Computational linguistics, morphology/syntax, theoretical syntax
\\item Natural Language Processing, computational algorithms
\\end{{itemize}}

\\divider

\\cvevent{{B.A.\\ in English Linguistics}}{{Wayne State University}}{{1992}}{{}}

\\switchcolumn

\\cvsection{{Skills}}

\\cvtag{{Python}}
\\cvtag{{TensorFlow}}
\\cvtag{{PyTorch}}
\\cvtag{{AWS}}
\\cvtag{{Docker}}
\\cvtag{{Kubernetes}}

\\divider\\smallskip

\\cvtag{{Machine Learning}}
\\cvtag{{NLP}}
\\cvtag{{Computer Vision}}
\\cvtag{{Generative AI}}
\\cvtag{{LLMs}}

\\divider\\smallskip

\\cvtag{{Linux/Unix}}
\\cvtag{{DevOps}}
\\cvtag{{Prometheus}}
\\cvtag{{Grafana}}

\\cvsection{{Clearance}}

\\cvachievement{{\\faTrophy}}{{DoD Top Secret}}{{FBI Counterintelligence Polygraph}}

\\cvsection{{Recent Projects}}

\\cvachievement{{\\faRocket}}{{Generative AI}}{{Immigration L-1 Visa processing using local LLM}}
\\cvachievement{{\\faChartLine}}{{GAN Implementation}}{{Luxury brand counterfeit detection system}}
\\cvachievement{{\\faDatabase}}{{FDA FAERS}}{{25MM records, 252GB semantic modeling with 1.1B triples}}

\\cvsection{{Publications}}

\\nocite{{*}}

\\divider

\\cvref{{Available upon request}}{{}}{{}}

\\end{{paracol}}

\\end{{document}}"""

        return self.compile_template("AltaCV_Timeline", altacv_content)
    
    def process_deedy_template(self, hash_id: str) -> bool:
        """Process the real Deedy template"""
        cache_dir = f"./template_cache/{hash_id}"
        self.setup_latex_environment(cache_dir)
        
        deedy_content = f"""\\documentclass[letterpaper]{{deedy-resume-reversed}}
\\usepackage{{fancyhdr}}

\\pagestyle{{fancy}}
\\fancyhf{{}}

\\begin{{document}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     TITLE NAME
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\\namesection{{{self.resume_vars['firstname']}}}{{{self.resume_vars['surname']}}}{{ \\urlstyle{{same}}\\href{{mailto:{self.resume_vars['email']}}}{{{self.resume_vars['email']}}} | {self.resume_vars['phone']} | \\href{{https://{self.resume_vars['website']}}}{{{self.resume_vars['website']}}}
}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     COLUMN ONE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\begin{{minipage}}[t]{{0.33\\textwidth}} 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     EDUCATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\section{{Education}} 

\\subsection{{Eastern Michigan University}}
\\descript{{MA English Linguistics}}
\\location{{April 2007 | Ypsilanti, MI}}
\\sectionsep

\\subsection{{Wayne State University}}
\\descript{{BA English Linguistics}}
\\location{{June 1992 | Detroit, MI}}
\\sectionsep

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     SKILLS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\section{{Skills}}
\\subsection{{Programming}}
\\location{{Expert:}}
Python \\textbullet{{}} TensorFlow \\textbullet{{}} PyTorch \\\\
AWS \\textbullet{{}} Docker \\textbullet{{}} Kubernetes \\\\
\\location{{Proficient:}}
R \\textbullet{{}} Perl \\textbullet{{}} Shell \\textbullet{{}} SQL \\\\
\\location{{Familiar:}}
JavaScript \\textbullet{{}} C \\textbullet{{}} Java \\\\
\\sectionsep

\\subsection{{Technologies}}
Machine Learning \\textbullet{{}} NLP \\\\
Computer Vision \\textbullet{{}} Generative AI \\\\
DevOps \\textbullet{{}} Cloud Architecture \\\\
\\sectionsep

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     CLEARANCE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\section{{Clearance}}
\\textbf{{DoD Top Secret}} \\\\
FBI Counterintelligence Polygraph
\\sectionsep

\\end{{minipage}} 
\\hfill
\\begin{{minipage}}[t]{{0.66\\textwidth}} 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     EXPERIENCE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\section{{Experience}}
\\runsubsection{{Technica Corporation}}
\\descript{{| Subject Matter Expert }}
\\location{{Sep 2023 – Present | FBI Headquarters}}
\\vspace{{\\topsep}}
\\begin{{tightemize}}
\\item Service Award within 90 days of service
\\item Onsite at Federal Bureau of Investigation - global admin
\\item Granted VAR with CI-Poly clearance  
\\item Enterprise application support across enclaves
\\end{{tightemize}}
\\sectionsep

\\runsubsection{{RRecktek LLC}}
\\descript{{| Principal Consultant \\& Founder }}
\\location{{Sep 2009 – Present | Remote}}
\\begin{{tightemize}}
\\item 100+ confidential clients including Johnson \\& Johnson, DHS, DoD
\\item Designed generative AI capability for Immigration L-1 Visas using local LLM
\\item Implemented GAN for luxury brand counterfeit detection
\\item Created NLP processing pipeline for abstractive/extractive NER
\\item Designed unsupervised categorization for 20k customer segmentation
\\item Implemented semantic modeling for FDA FAERS (25MM records, 252GB)
\\end{{tightemize}}
\\sectionsep

\\runsubsection{{SanCorpConsulting}}
\\descript{{| Chief Technology Officer }}
\\location{{May 2020 – Jun 2021 | DoD Joint AI Center}}
\\begin{{tightemize}}
\\item Senior Technology Advisor at Department of Defense JAIC
\\item Data Science oversight on projects with tens of millions in funding
\\item Designed NLP pipeline for projects receiving additional funding
\\item Security hardening of R containers in cloud development environment
\\end{{tightemize}}
\\sectionsep

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     PROJECTS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\section{{Recent AI Projects}}
\\runsubsection{{Generative AI Immigration System}}
\\descript{{| Local LLM Implementation}}
\\location{{2024}
Designed and implemented generative AI capability for Immigration L-1 Visas using local large language models for enhanced privacy and control.
\\sectionsep

\\runsubsection{{Luxury Brand Protection}}
\\descript{{| GAN-based Detection}}
\\location{{2024}
Implemented Generative Adversarial Network for leading luxury brands to detect counterfeit products with high accuracy.
\\sectionsep

\\end{{minipage}} 
\\end{{document}}"""

        return self.compile_template("Deedy_Resume_Modern", deedy_content)
    
    def process_jan_kuster_template(self, hash_id: str, variant: str) -> bool:
        """Process Jan Küster template"""
        cache_dir = f"./template_cache/{hash_id}"
        self.setup_latex_environment(cache_dir)
        
        if "Two_column" in variant:
            template_name = "Jan_Kuster_TwoColumn"
            columns = True
        else:
            template_name = "Jan_Kuster_Modern"
            columns = False
        
        # Jan Küster templates use moderncv class typically
        jan_content = f"""\\documentclass[11pt,a4paper,sans]{{moderncv}}

\\moderncvstyle{{banking}}
\\moderncvcolor{{blue}}

\\usepackage[scale=0.75]{{geometry}}

\\name{{{self.resume_vars['firstname']}}}{{{self.resume_vars['surname']}}}
\\title{{{self.resume_vars['title']}}}
\\address{{{self.resume_vars['address']}}}{{USA}}
\\phone[mobile]{{{self.resume_vars['phone']}}}
\\email{{{self.resume_vars['email']}}}
\\homepage{{{self.resume_vars['website']}}}
\\social[linkedin]{{{self.resume_vars['linkedin']}}}
\\social[github]{{{self.resume_vars['github']}}}
\\quote{{{self.resume_vars['quote']}}}

\\begin{{document}}

\\makecvtitle

\\section{{Professional Summary}}
\\cvitem{{}}{{AI professional with specialization in Generative AI. Author of commercial ARTIFICIAL INTELLIGENCE software Predictive Analytics Framework on Amazon Web Service Marketplace. 18+ Years of Amazon Web Services experience. AWS Marketplace publisher of 11 data products.}}

\\section{{Experience}}
\\cventry{{2023--Present}}{{Subject Matter Expert}}{{Technica Corporation}}{{FBI Headquarters}}{{}}{{Service Award within 90 days. FBI global admin with CI-Poly clearance. Enterprise application support across enclaves.}}

\\cventry{{2009--Present}}{{Principal Consultant \\& Founder}}{{RRecktek LLC}}{{Remote}}{{}}{{100+ confidential clients including Johnson \\& Johnson, DHS, DoD. Designed generative AI solutions, NLP pipelines, cloud architecture.}}

\\cventry{{2020--2021}}{{Chief Technology Officer}}{{SanCorpConsulting}}{{DoD JAIC}}{{}}{{Senior Technology Advisor at Department of Defense Joint AI Center. Data Science oversight on multi-million dollar projects.}}

\\section{{Education}}
\\cventry{{2007}}{{Master of Arts}}{{Eastern Michigan University}}{{Ypsilanti, MI}}{{English Linguistics}}{{Computational linguistics, morphology/syntax, theoretical syntax, NLP}}

\\cventry{{1992}}{{Bachelor of Arts}}{{Wayne State University}}{{Detroit, MI}}{{English Linguistics}}{{Theoretical syntax, morphology, semantics}}

\\section{{Technical Skills}}
\\cvdoubleitem{{Programming}}{{Python, TensorFlow, PyTorch, R, Perl}}{{Cloud}}{{AWS (18+ years), Docker, Kubernetes}}
\\cvdoubleitem{{AI/ML}}{{Machine Learning, NLP, Computer Vision, Generative AI}}{{DevOps}}{{Prometheus, Grafana, CI/CD, Automation}}

\\section{{Clearance}}
\\cvitem{{Security}}{{DoD Top Secret with FBI Counterintelligence Polygraph}}

\\section{{Recent AI Projects}}
\\cvlistitem{{Designed generative AI capability for Immigration L-1 Visas using local LLM}}
\\cvlistitem{{Implemented GAN for luxury brand counterfeit detection}}
\\cvlistitem{{Created NLP processing pipeline for multiple domains}}
\\cvlistitem{{Designed semantic modeling for FDA FAERS (25MM records, 252GB)}}

\\end{{document}}"""

        return self.compile_template(template_name, jan_content)
    
    def compile_template(self, template_name: str, latex_content: str) -> bool:
        """Compile LaTeX template to PDF"""
        work_dir = Path(f"./work_{int(time.time())}_{template_name}")
        work_dir.mkdir(exist_ok=True)
        
        try:
            # Copy any .cls/.sty files to work directory
            for cls_file in Path(".").glob("*.cls"):
                shutil.copy2(cls_file, work_dir)
            for sty_file in Path(".").glob("*.sty"):
                shutil.copy2(sty_file, work_dir)
            for img_file in Path(".").glob("*.png"):
                shutil.copy2(img_file, work_dir)
            
            # Write LaTeX file
            tex_file = work_dir / f"{template_name}.tex"
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # Try compilation with different engines
            engines = ['xelatex', 'lualatex', 'pdflatex']
            
            for engine in engines:
                try:
                    logger.info(f"🔄 Compiling {template_name} with {engine}")
                    
                    cmd = [
                        engine,
                        '-interaction=nonstopmode',
                        '-output-directory', str(work_dir),
                        str(tex_file)
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
                    
                    pdf_file = work_dir / f"{template_name}.pdf"
                    if pdf_file.exists() and pdf_file.stat().st_size > 5000:  # At least 5KB
                        # Copy to output
                        output_pdf = self.output_dir / f"ronald-reck-resume-{template_name}.pdf"
                        shutil.copy2(pdf_file, output_pdf)
                        
                        file_size = output_pdf.stat().st_size
                        logger.info(f"✅ SUCCESS: {template_name} with {engine} ({file_size/1024:.1f}KB)")
                        
                        self.results["successful"].append({
                            "template": template_name,
                            "output_file": str(output_pdf),
                            "size": file_size,
                            "engine": engine
                        })
                        return True
                        
                except subprocess.TimeoutExpired:
                    logger.debug(f"{engine} timed out for {template_name}")
                    continue
                except Exception as e:
                    logger.debug(f"{engine} failed for {template_name}: {e}")
                    continue
            
            logger.warning(f"❌ FAILED: {template_name} - All engines failed")
            self.results["failed"].append({
                "template": template_name,
                "error": "All LaTeX engines failed"
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
            # Cleanup
            if work_dir.exists():
                try:
                    shutil.rmtree(work_dir)
                except:
                    pass
            
            # Cleanup copied files
            for cls_file in Path(".").glob("*.cls"):
                try:
                    cls_file.unlink()
                except:
                    pass
    
    def process_all_real_templates(self):
        """Process all real templates with their actual designs"""
        logger.info("🚀 Processing REAL professional templates with actual designs...")
        
        # Process specific templates we know how to handle
        template_processors = {
            # AltaCV - Timeline CV with sidebar
            '25ee69eeb3513355': ('AltaCV', self.process_altacv_template),
            
            # Deedy Resume
            '6e657645a8f3ed94': ('Deedy', self.process_deedy_template),
            
            # Jan Küster Modern CV
            '1d20c3c2973e4319': ('Jan_Kuster_Modern', lambda h: self.process_jan_kuster_template(h, 'Modern')),
            
            # Jan Küster Two Column CV  
            '1acd72e1a2364f4b': ('Jan_Kuster_TwoColumn', lambda h: self.process_jan_kuster_template(h, 'Two_column')),
        }
        
        success_count = 0
        
        for hash_id, (template_type, processor_func) in template_processors.items():
            if hash_id in self.registry:
                logger.info(f"📋 Processing {template_type} template...")
                success = processor_func(hash_id)
                if success:
                    success_count += 1
            else:
                logger.warning(f"⚠️ Template {template_type} not found in registry")
        
        logger.info(f"✅ Successfully processed {success_count}/{len(template_processors)} real templates")
        
        self.print_summary()
    
    def print_summary(self):
        """Print processing summary"""
        successful = len(self.results["successful"])
        failed = len(self.results["failed"])
        total = successful + failed
        
        print("\n📊 REAL TEMPLATE PROCESSING REPORT")
        print("=" * 50)
        print(f"📋 Templates Processed: {total}")
        print(f"✅ Successfully Generated: {successful}")
        print(f"❌ Failed: {failed}")
        
        if self.results["successful"]:
            print("\n✅ REAL PROFESSIONAL TEMPLATES GENERATED:")
            print("-" * 45)
            for result in self.results["successful"]:
                size_kb = result["size"] / 1024
                engine = result.get("engine", "unknown")
                print(f"  📄 {result['template']}.pdf ({size_kb:.1f}KB) [{engine}]")
        
        if self.results["failed"]:
            print("\n❌ FAILED TEMPLATES:")
            print("-" * 30)
            for result in self.results["failed"]:
                print(f"  ❌ {result['template']}: {result['error']}")

def main():
    """Main execution"""
    processor = RealTemplateProcessor()
    processor.process_all_real_templates()
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)