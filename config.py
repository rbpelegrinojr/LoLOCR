"""
Configuration Management for LoLOCR
Handles loading and managing application configuration
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for LoLOCR."""
    
    DEFAULT_CONFIG = {
        'capture': {
            'method': 'ndi',  # Options: 'ndi', 'window', 'screen'
            'ndi': {
                'source_name': '',  # NDI source name, e.g., "OBS (Main):Main Output"
                'enabled': True,
            },
            'window': {
                'window_title': 'League of Legends',
                'enabled': False,
            },
            'screen': {
                'monitor_index': 0,
                'enabled': False,
            }
        },
        'ocr': {
            'enabled': True,
            'debug': False,
            'save_crops': True,
        },
        'output': {
            'base_dir': 'output',
            'update_interval_ms': 500,  # Update output files every 500ms
            'generate_json': True,
            'generate_txt': True,
            'generate_debug': True,
        },
        'scoring': {
            'enabled': True,
            'scoreboard_crop_region': {
                'x': 0,
                'y': 0,
                'width': 1920,
                'height': 1080,
            }
        },
        'logging': {
            'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
            'file': 'logs/lolecr.log',
            'console': True,
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to config.json file. If not provided,
                        will look for config.json in current directory.
        """
        self.config_path = config_path or 'config.json'
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Load configuration if file exists
        if os.path.exists(self.config_path):
            self.load()
        else:
            # Save default configuration
            self.save()
    
    def load(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # Deep merge with defaults
            self._deep_merge(self.config, loaded_config)
            print(f"Configuration loaded from {self.config_path}")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.config_path}, using defaults")
        except Exception as e:
            print(f"Error loading configuration: {e}, using defaults")
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            # Create directory if needed
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {self.config_path}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to config value, e.g., 'capture.method'
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to config value, e.g., 'capture.method'
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to parent
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set value
        config[keys[-1]] = value
    
    def get_ndi_source(self) -> str:
        """Get configured NDI source name."""
        return self.get('capture.ndi.source_name', '')
    
    def set_ndi_source(self, source_name: str) -> None:
        """Set NDI source name."""
        self.set('capture.ndi.source_name', source_name)
    
    def get_capture_method(self) -> str:
        """Get configured capture method."""
        return self.get('capture.method', 'ndi')
    
    def set_capture_method(self, method: str) -> None:
        """Set capture method."""
        if method not in ['ndi', 'window', 'screen']:
            raise ValueError("Capture method must be 'ndi', 'window', or 'screen'")
        self.set('capture.method', method)
    
    def get_output_dir(self) -> str:
        """Get output directory path."""
        return self.get('output.base_dir', 'output')
    
    def get_update_interval_ms(self) -> int:
        """Get output update interval in milliseconds."""
        return self.get('output.update_interval_ms', 500)
    
    def _deep_merge(self, target: Dict, source: Dict) -> None:
        """Deep merge source into target."""
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config(path={self.config_path})"
