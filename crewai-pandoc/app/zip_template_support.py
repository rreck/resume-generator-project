#!/usr/bin/env python3
"""
ZIP Template Support for CrewAI Pandoc Agent
Handles extraction and management of LaTeX resume templates from ZIP files
"""

import os
import shutil
import tempfile
import zipfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import json
import time

logger = logging.getLogger(__name__)

class ZipTemplateManager:
    """Manages ZIP template extraction and processing"""
    
    def __init__(self, cache_dir: str = "./template_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.template_registry = {}
        self.load_template_registry()
    
    def load_template_registry(self):
        """Load template registry from cache"""
        registry_file = self.cache_dir / "template_registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    self.template_registry = json.load(f)
                logger.info(f"Loaded {len(self.template_registry)} templates from registry")
            except Exception as e:
                logger.warning(f"Failed to load template registry: {e}")
                self.template_registry = {}
    
    def save_template_registry(self):
        """Save template registry to cache"""
        registry_file = self.cache_dir / "template_registry.json"
        try:
            with open(registry_file, 'w') as f:
                json.dump(self.template_registry, f, indent=2)
            logger.debug("Template registry saved")
        except Exception as e:
            logger.error(f"Failed to save template registry: {e}")
    
    def get_zip_hash(self, zip_path: str) -> str:
        """Calculate hash of ZIP file for caching"""
        hasher = hashlib.sha256()
        with open(zip_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]
    
    def is_safe_path(self, path: str, base_path: str) -> bool:
        """Check if extracted path is safe (prevents directory traversal)"""
        abs_base = os.path.abspath(base_path)
        abs_path = os.path.abspath(os.path.join(base_path, path))
        return abs_path.startswith(abs_base)
    
    def extract_zip_safely(self, zip_path: str, extract_dir: str) -> bool:
        """Safely extract ZIP file with security checks"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check for dangerous paths
                for member in zip_ref.namelist():
                    if not self.is_safe_path(member, extract_dir):
                        logger.error(f"Unsafe path detected in ZIP: {member}")
                        return False
                    
                    # Check file size (prevent ZIP bombs)
                    info = zip_ref.getinfo(member)
                    if info.file_size > 100 * 1024 * 1024:  # 100MB limit per file
                        logger.error(f"File too large in ZIP: {member} ({info.file_size} bytes)")
                        return False
                
                # Extract files
                zip_ref.extractall(extract_dir)
                logger.info(f"Successfully extracted ZIP to {extract_dir}")
                return True
                
        except zipfile.BadZipFile:
            logger.error(f"Invalid ZIP file: {zip_path}")
            return False
        except Exception as e:
            logger.error(f"Error extracting ZIP {zip_path}: {e}")
            return False
    
    def detect_template_files(self, extract_dir: str) -> Dict[str, Any]:
        """Detect and analyze template files in extracted directory"""
        template_info = {
            'main_template': None,
            'template_files': [],
            'class_files': [],
            'style_files': [],
            'bibliography_files': [],
            'font_files': [],
            'image_files': [],
            'readme_files': [],
            'type': 'unknown',
            'complexity': 'simple'
        }
        
        extract_path = Path(extract_dir)
        
        # Find all relevant files
        for file_path in extract_path.rglob('*'):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                relative_path = file_path.relative_to(extract_path)
                
                if suffix == '.tex':
                    template_info['template_files'].append(str(relative_path))
                elif suffix == '.cls':
                    template_info['class_files'].append(str(relative_path))
                elif suffix == '.sty':
                    template_info['style_files'].append(str(relative_path))
                elif suffix == '.bib':
                    template_info['bibliography_files'].append(str(relative_path))
                elif suffix in ['.ttf', '.otf', '.woff', '.woff2']:
                    template_info['font_files'].append(str(relative_path))
                elif suffix in ['.png', '.jpg', '.jpeg', '.pdf', '.eps']:
                    template_info['image_files'].append(str(relative_path))
                elif suffix in ['.md', '.txt', '.html'] or file_path.name.lower() == 'readme':
                    template_info['readme_files'].append(str(relative_path))
        
        # Detect main template file
        template_info['main_template'] = self.find_main_template(template_info['template_files'], extract_dir)
        
        # Determine template type and complexity
        template_info['type'] = self.classify_template_type(template_info)
        template_info['complexity'] = self.assess_complexity(template_info)
        
        return template_info
    
    def find_main_template(self, tex_files: List[str], extract_dir: str) -> Optional[str]:
        """Find the main template file among .tex files"""
        if not tex_files:
            return None
        
        # If only one .tex file, it's the main one
        if len(tex_files) == 1:
            return tex_files[0]
        
        # Look for common main file patterns
        main_patterns = [
            'main.tex', 'template.tex', 'cv.tex', 'resume.tex',
            'index.tex', 'document.tex'
        ]
        
        for pattern in main_patterns:
            for tex_file in tex_files:
                if Path(tex_file).name.lower() == pattern:
                    return tex_file
        
        # Look for files with \documentclass
        for tex_file in tex_files:
            try:
                with open(Path(extract_dir) / tex_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # Read first 1000 chars
                    if '\\documentclass' in content:
                        return tex_file
            except Exception:
                continue
        
        # Default to first file if no clear main found
        logger.warning(f"Could not identify main template, using: {tex_files[0]}")
        return tex_files[0]
    
    def classify_template_type(self, template_info: Dict[str, Any]) -> str:
        """Classify template type based on content analysis"""
        main_template = template_info.get('main_template')
        if not main_template:
            return 'unknown'
        
        # Common template type keywords
        template_keywords = {
            'academic': ['cv', 'academic', 'publication', 'research'],
            'professional': ['resume', 'professional', 'business'],
            'creative': ['creative', 'design', 'hipster', 'modern'],
            'technical': ['technical', 'engineering', 'developer'],
            'minimal': ['minimal', 'simple', 'clean', 'basic']
        }
        
        template_name = main_template.lower()
        
        for template_type, keywords in template_keywords.items():
            if any(keyword in template_name for keyword in keywords):
                return template_type
        
        return 'professional'  # Default fallback
    
    def assess_complexity(self, template_info: Dict[str, Any]) -> str:
        """Assess template complexity level"""
        complexity_score = 0
        
        # Count different file types
        complexity_score += len(template_info['class_files']) * 2
        complexity_score += len(template_info['style_files'])
        complexity_score += len(template_info['font_files'])
        complexity_score += len(template_info['image_files'])
        complexity_score += len(template_info['bibliography_files'])
        
        # Multiple .tex files indicate complexity
        if len(template_info['template_files']) > 1:
            complexity_score += 3
        
        if complexity_score == 0:
            return 'simple'
        elif complexity_score <= 3:
            return 'medium'
        else:
            return 'complex'
    
    def process_zip_template(self, zip_path: str) -> Optional[Dict[str, Any]]:
        """Process a ZIP template file and return template information"""
        zip_hash = self.get_zip_hash(zip_path)
        
        # Check if already processed
        if zip_hash in self.template_registry:
            cached_info = self.template_registry[zip_hash]
            cache_path = Path(self.cache_dir) / zip_hash
            if cache_path.exists():
                logger.info(f"Using cached template: {zip_path}")
                return cached_info
        
        # Create temporary extraction directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract ZIP file
            if not self.extract_zip_safely(zip_path, temp_dir):
                return None
            
            # Analyze template files
            template_info = self.detect_template_files(temp_dir)
            template_info['zip_path'] = zip_path
            template_info['zip_hash'] = zip_hash
            template_info['cached_path'] = str(self.cache_dir / zip_hash)
            template_info['processed_time'] = time.time()
            
            # Copy to permanent cache
            cache_path = self.cache_dir / zip_hash
            if cache_path.exists():
                shutil.rmtree(cache_path)
            shutil.copytree(temp_dir, cache_path)
            
            # Update registry
            self.template_registry[zip_hash] = template_info
            self.save_template_registry()
            
            logger.info(f"Processed template: {zip_path} -> {template_info['type']} ({template_info['complexity']})")
            return template_info
    
    def get_template_path(self, zip_hash: str) -> Optional[str]:
        """Get the cached template path for a processed ZIP"""
        if zip_hash in self.template_registry:
            template_info = self.template_registry[zip_hash]
            cache_path = Path(self.cache_dir) / zip_hash
            main_template = template_info.get('main_template')
            
            if cache_path.exists() and main_template:
                return str(cache_path / main_template)
        
        return None
    
    def list_available_templates(self) -> List[Dict[str, Any]]:
        """List all available processed templates"""
        templates = []
        for zip_hash, template_info in self.template_registry.items():
            cache_path = Path(self.cache_dir) / zip_hash
            if cache_path.exists():
                templates.append({
                    'hash': zip_hash,
                    'name': Path(template_info['zip_path']).stem,
                    'type': template_info['type'],
                    'complexity': template_info['complexity'],
                    'main_template': template_info['main_template'],
                    'files': len(template_info['template_files']) + len(template_info['class_files'])
                })
        
        return sorted(templates, key=lambda x: (x['type'], x['name']))
    
    def find_templates_by_type(self, template_type: str) -> List[str]:
        """Find template hashes by type"""
        matches = []
        for zip_hash, template_info in self.template_registry.items():
            if template_info.get('type') == template_type:
                matches.append(zip_hash)
        return matches
    
    def cleanup_cache(self, max_age_days: int = 30):
        """Clean up old cached templates"""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        to_remove = []
        for zip_hash, template_info in self.template_registry.items():
            if template_info.get('processed_time', 0) < cutoff_time:
                to_remove.append(zip_hash)
        
        for zip_hash in to_remove:
            cache_path = self.cache_dir / zip_hash
            if cache_path.exists():
                shutil.rmtree(cache_path)
            del self.template_registry[zip_hash]
        
        if to_remove:
            self.save_template_registry()
            logger.info(f"Cleaned up {len(to_remove)} old templates")

def scan_and_process_templates(template_dir: str) -> ZipTemplateManager:
    """Scan directory for ZIP templates and process them"""
    manager = ZipTemplateManager()
    template_path = Path(template_dir)
    
    if not template_path.exists():
        logger.warning(f"Template directory not found: {template_dir}")
        return manager
    
    zip_files = list(template_path.glob("*.zip"))
    logger.info(f"Found {len(zip_files)} ZIP files to process")
    
    for zip_file in zip_files:
        try:
            result = manager.process_zip_template(str(zip_file))
            if result:
                logger.info(f"✅ Processed: {zip_file.name} -> {result['type']}")
            else:
                logger.error(f"❌ Failed: {zip_file.name}")
        except Exception as e:
            logger.error(f"❌ Error processing {zip_file.name}: {e}")
    
    return manager

if __name__ == "__main__":
    # Test the ZIP template manager
    logging.basicConfig(level=logging.INFO)
    
    # Process templates in the templates directory
    manager = scan_and_process_templates("../templates")
    
    # Show results
    templates = manager.list_available_templates()
    print(f"\n📋 Processed {len(templates)} templates:")
    for template in templates:
        print(f"  • {template['name']} ({template['type']}, {template['complexity']})")
    
    # Show by type
    for template_type in ['academic', 'professional', 'creative', 'technical', 'minimal']:
        type_templates = manager.find_templates_by_type(template_type)
        if type_templates:
            print(f"\n🎯 {template_type.title()} Templates: {len(type_templates)}")
            for hash_id in type_templates:
                info = manager.template_registry[hash_id]
                name = Path(info['zip_path']).stem
                print(f"  • {name} ({info['complexity']})")