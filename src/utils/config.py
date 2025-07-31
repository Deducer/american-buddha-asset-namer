"""
Configuration management for American Buddha Asset Namer
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

class Config:
    """Configuration manager for the application"""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration"""
        if config_path is None:
            # Get the project root directory
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Return default configuration
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "naming_patterns": {
                "default": "{date}_{description}_{sequence}",
                "documentary": "{project}_{scene}_{date}_{number}",
                "location_based": "{location}_{subject}_{action}_{counter}"
            },
            "supported_formats": {
                "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
                "videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"]
            },
            "ai_settings": {
                "model": "gpt-4-vision-preview",
                "max_tokens": 150,
                "temperature": 0.7,
                "detail_level": "auto"
            },
            "processing": {
                "batch_size": 10,
                "preview_thumbnails": True,
                "backup_originals": True,
                "max_file_size_mb": 100
            },
            "output": {
                "date_format": "%Y-%m-%d",
                "sequence_padding": 3,
                "lowercase_names": False,
                "replace_spaces": "_"
            }
        }
    
    def save(self):
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save()
    
    @property
    def supported_image_formats(self) -> List[str]:
        """Get supported image formats"""
        return self.get("supported_formats.images", [])
    
    @property
    def supported_video_formats(self) -> List[str]:
        """Get supported video formats"""
        return self.get("supported_formats.videos", [])
    
    @property
    def all_supported_formats(self) -> List[str]:
        """Get all supported formats"""
        return self.supported_image_formats + self.supported_video_formats
    
    @property
    def naming_patterns(self) -> Dict[str, str]:
        """Get naming patterns"""
        return self.get("naming_patterns", {})
    
    def add_naming_pattern(self, name: str, pattern: str):
        """Add a new naming pattern"""
        patterns = self.naming_patterns
        patterns[name] = pattern
        self.set("naming_patterns", patterns)