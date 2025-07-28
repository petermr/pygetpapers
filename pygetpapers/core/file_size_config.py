"""
File Size Alert Configuration

This module provides configuration settings for file size alerts and warnings.
"""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    "file_size_alert_threshold_mb": 100,
    "file_size_warning_threshold_mb": 50,
    "enable_file_size_alerts": True,
    "show_ui_warnings": True,
    "log_large_files": True,
    "alert_message_template": "🚨 LARGE FILE ALERT: {file_name} is {size_mb:.1f} MB (exceeds {threshold_mb} MB threshold)",
    "warning_message_template": "⚠️  This large file may take significant time to download and consume substantial disk space."
}

class FileSizeConfig:
    """Configuration manager for file size alerts."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize file size configuration.
        
        Args:
            config: Optional configuration dictionary to override defaults
        """
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
        
        # Allow environment variable overrides
        self._load_from_environment()
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        env_mapping = {
            "PYGETPAPERS_FILE_SIZE_ALERT_THRESHOLD_MB": "file_size_alert_threshold_mb",
            "PYGETPAPERS_FILE_SIZE_WARNING_THRESHOLD_MB": "file_size_warning_threshold_mb",
            "PYGETPAPERS_ENABLE_FILE_SIZE_ALERTS": "enable_file_size_alerts",
            "PYGETPAPERS_SHOW_UI_WARNINGS": "show_ui_warnings",
            "PYGETPAPERS_LOG_LARGE_FILES": "log_large_files"
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                if config_key.endswith("_mb"):
                    try:
                        self.config[config_key] = int(value)
                    except ValueError:
                        pass
                elif config_key.startswith("enable_") or config_key.startswith("show_") or config_key.startswith("log_"):
                    self.config[config_key] = value.lower() in ("true", "1", "yes", "on")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def get_alert_threshold_bytes(self) -> int:
        """Get alert threshold in bytes."""
        return self.config["file_size_alert_threshold_mb"] * 1024 * 1024
    
    def get_warning_threshold_bytes(self) -> int:
        """Get warning threshold in bytes."""
        return self.config["file_size_warning_threshold_mb"] * 1024 * 1024
    
    def is_alerts_enabled(self) -> bool:
        """Check if file size alerts are enabled."""
        return self.config["enable_file_size_alerts"]
    
    def should_show_ui_warnings(self) -> bool:
        """Check if UI warnings should be shown."""
        return self.config["show_ui_warnings"]
    
    def should_log_large_files(self) -> bool:
        """Check if large files should be logged."""
        return self.config["log_large_files"]

# Global configuration instance
file_size_config = FileSizeConfig() 