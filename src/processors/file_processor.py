"""
File processor for renaming media files
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from processors.ai_analyzer import AIAnalyzer
from utils.logger import get_logger
from utils.config import Config

logger = get_logger("FileProcessor")

class FileProcessor:
    """Handles file processing and renaming operations"""
    
    def __init__(self, config: Config, ai_analyzer: AIAnalyzer = None):
        """Initialize file processor"""
        self.config = config
        self.ai_analyzer = ai_analyzer or AIAnalyzer()
        self.processed_files = []
        self.errors = []
    
    def scan_directory(self, directory: Path) -> List[Path]:
        """Scan directory for supported media files"""
        files = []
        supported_formats = self.config.all_supported_formats
        
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                # Check file size
                max_size_mb = self.config.get("processing.max_file_size_mb", 100)
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                
                if file_size_mb <= max_size_mb:
                    files.append(file_path)
                else:
                    logger.warning(f"Skipping {file_path.name} - exceeds size limit ({file_size_mb:.1f}MB)")
        
        logger.info(f"Found {len(files)} media files in {directory}")
        return sorted(files)
    
    def process_files(self, files: List[Path], pattern_name: str = "default", 
                     custom_pattern: str = None, progress_callback=None) -> Dict[str, Any]:
        """Process multiple files for renaming"""
        results = {
            "total": len(files),
            "processed": 0,
            "errors": 0,
            "suggestions": []
        }
        
        # Get naming pattern
        if custom_pattern:
            pattern = custom_pattern
        else:
            patterns = self.config.naming_patterns
            pattern = patterns.get(pattern_name, patterns.get("default"))
        
        # Process files in batches
        batch_size = self.config.get("processing.batch_size", 10)
        
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            
            # Process batch concurrently
            with ThreadPoolExecutor(max_workers=min(4, len(batch))) as executor:
                futures = {
                    executor.submit(self._process_single_file, file_path, pattern, i + j): file_path
                    for j, file_path in enumerate(batch)
                }
                
                for future in as_completed(futures):
                    file_path = futures[future]
                    try:
                        suggestion = future.result()
                        if suggestion:
                            results["suggestions"].append(suggestion)
                            results["processed"] += 1
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        results["errors"] += 1
                    
                    # Update progress
                    if progress_callback:
                        current = i + len(futures) - len([f for f in futures if not f.done()])
                        progress_callback(current, len(files))
        
        return results
    
    def _process_single_file(self, file_path: Path, pattern: str, sequence: int) -> Optional[Dict[str, Any]]:
        """Process a single file and generate naming suggestion"""
        try:
            # Get file metadata
            metadata = self._get_file_metadata(file_path)
            
            # Analyze content with AI
            if file_path.suffix.lower() in self.config.supported_video_formats:
                analysis = self.ai_analyzer.analyze_video(file_path)
            else:
                analysis = self.ai_analyzer.analyze_image(file_path)
            
            # Merge metadata and analysis
            context = {**metadata, **analysis, "sequence": sequence + 1}
            
            # Generate new name
            new_name = self._generate_name(pattern, context)
            new_path = file_path.parent / f"{new_name}{file_path.suffix}"
            
            # Handle duplicates
            new_path = self._handle_duplicates(new_path)
            
            return {
                "original_path": file_path,
                "new_path": new_path,
                "original_name": file_path.name,
                "new_name": new_path.name,
                "analysis": analysis,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None
    
    def _get_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract file metadata"""
        stat = file_path.stat()
        
        return {
            "date": datetime.fromtimestamp(stat.st_mtime),
            "size": stat.st_size,
            "size_mb": stat.st_size / (1024 * 1024),
            "extension": file_path.suffix.lower(),
            "original_name": file_path.stem
        }
    
    def _generate_name(self, pattern: str, context: Dict[str, Any]) -> str:
        """Generate new name based on pattern and context"""
        # Format date
        date_format = self.config.get("output.date_format", "%Y-%m-%d")
        date_str = context.get("date", datetime.now()).strftime(date_format)
        
        # Format sequence number
        padding = self.config.get("output.sequence_padding", 3)
        sequence_str = str(context.get("sequence", 1)).zfill(padding)
        
        # Build replacements
        replacements = {
            "date": date_str,
            "description": context.get("description", "untitled"),
            "sequence": sequence_str,
            "number": sequence_str,
            "project": context.get("project", "project"),
            "scene": context.get("scene_type", "scene"),
            "location": context.get("location", "location"),
            "subject": "_".join(context.get("subjects", ["subject"])[:2]),
            "action": context.get("action", "action"),
            "counter": sequence_str,
            "original": context.get("original_name", "file")
        }
        
        # Replace placeholders
        name = pattern
        for key, value in replacements.items():
            name = name.replace(f"{{{key}}}", str(value))
        
        # Clean up the name
        name = self._sanitize_filename(name)
        
        # Apply output settings
        if self.config.get("output.lowercase_names", False):
            name = name.lower()
        
        replace_char = self.config.get("output.replace_spaces", "_")
        if replace_char:
            name = name.replace(" ", replace_char)
        
        return name
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename for filesystem compatibility"""
        # Remove invalid characters
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        
        # Replace multiple underscores/dashes with single
        name = re.sub(r'[_-]{2,}', '_', name)
        
        # Remove leading/trailing underscores
        name = name.strip('_- ')
        
        # Ensure name is not empty
        return name or "untitled"
    
    def _handle_duplicates(self, path: Path) -> Path:
        """Handle duplicate filenames by adding counter"""
        if not path.exists():
            return path
        
        counter = 1
        stem = path.stem
        suffix = path.suffix
        
        while True:
            new_path = path.parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    def apply_renames(self, suggestions: List[Dict[str, Any]], 
                     backup: bool = None, progress_callback=None) -> Dict[str, Any]:
        """Apply the suggested renames"""
        if backup is None:
            backup = self.config.get("processing.backup_originals", True)
        
        results = {
            "total": len(suggestions),
            "renamed": 0,
            "errors": 0,
            "backups": []
        }
        
        # Create backup directory if needed
        if backup:
            backup_dir = Path("backup") / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir.mkdir(parents=True, exist_ok=True)
        
        for i, suggestion in enumerate(suggestions):
            try:
                original_path = suggestion["original_path"]
                new_path = suggestion["new_path"]
                
                # Skip if paths are the same
                if original_path == new_path:
                    logger.info(f"Skipping {original_path.name} - no change needed")
                    continue
                
                # Create backup if requested
                if backup:
                    backup_path = backup_dir / original_path.name
                    shutil.copy2(original_path, backup_path)
                    results["backups"].append(backup_path)
                    logger.info(f"Backed up {original_path.name}")
                
                # Rename the file
                original_path.rename(new_path)
                results["renamed"] += 1
                logger.info(f"Renamed: {original_path.name} -> {new_path.name}")
                
            except Exception as e:
                logger.error(f"Error renaming {original_path}: {e}")
                results["errors"] += 1
            
            # Update progress
            if progress_callback:
                progress_callback(i + 1, len(suggestions))
        
        return results