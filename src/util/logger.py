"""Logger wrapper for dual file and console logging."""

import logging
import sys
from pathlib import Path
from datetime import datetime, timezone


class DualLogger:
    """Logger that writes to console and two log files (normal and debug)."""
    
    def __init__(self, name, log_dir=None, console_level=logging.INFO):
        """Initialize the dual logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files (default: results/logs)
            console_level: Console logging level (default: INFO)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Capture everything
        self.logger.handlers.clear()  # Clear any existing handlers
        
        # Determine log directory
        if log_dir is None:
            log_dir = Path("results") / "logs"
        else:
            log_dir = Path(log_dir)
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler (INFO level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        # Normal log file handler (INFO level)
        normal_log = log_dir / f"{name}.log"
        normal_handler = logging.FileHandler(normal_log, mode='a')
        normal_handler.setLevel(logging.INFO)
        normal_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(normal_handler)
        
        # Debug log file handler (DEBUG level)
        debug_log = log_dir / f"{name}.debug.log"
        debug_handler = logging.FileHandler(debug_log, mode='a')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(debug_handler)
        
        self.normal_log_path = str(normal_log)
        self.debug_log_path = str(debug_log)
    
    def debug(self, message):
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message):
        """Log an error message."""
        self.logger.error(message)
    
    def critical(self, message):
        """Log a critical message."""
        self.logger.critical(message)
    
    def get_log_paths(self):
        """Get paths to the log files.
        
        Returns:
            Tuple of (normal_log_path, debug_log_path)
        """
        return self.normal_log_path, self.debug_log_path


def get_logger(name, log_dir=None, console_level=logging.INFO):
    """Get or create a DualLogger instance.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        console_level: Console logging level
        
    Returns:
        DualLogger instance
    """
    return DualLogger(name, log_dir, console_level)
