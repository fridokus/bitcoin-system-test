"""Base test class for Robot Framework tests."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.logger import get_logger

# Import config
from . import config


class BaseTest:
    """Base class for Robot Framework tests with common setup/teardown patterns."""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        """Initialize base test class."""
        self.logger = None
        self.test_name = None
    
    def setup_test_logging(self, test_name, log_dir=None):
        """Setup logging for a test.
        
        Args:
            test_name: Name of the test
            log_dir: Directory for log files (default: results/logs)
            
        Returns:
            Logger instance
        """
        self.test_name = test_name
        
        if log_dir is None:
            # Use OUTPUT_DIR if available (set by Robot Framework)
            output_dir = os.environ.get('ROBOT_OUTPUT_DIR', 'results/logs')
            log_dir = Path(output_dir)
        
        self.logger = get_logger(test_name, log_dir=log_dir)
        self.logger.info(f"Starting test: {test_name}")
        
        return self.logger
    
    def teardown_test_logging(self):
        """Teardown logging for a test."""
        if self.logger:
            self.logger.info(f"Completed test: {self.test_name}")
            normal_log, debug_log = self.logger.get_log_paths()
            self.logger.info(f"Logs saved to: {normal_log}, {debug_log}")
    
    def log_info(self, message):
        """Log an info message.
        
        Args:
            message: Message to log
        """
        if self.logger:
            self.logger.info(message)
        else:
            print(f"INFO: {message}")
    
    def log_debug(self, message):
        """Log a debug message.
        
        Args:
            message: Message to log
        """
        if self.logger:
            self.logger.debug(message)
    
    def log_error(self, message):
        """Log an error message.
        
        Args:
            message: Message to log
        """
        if self.logger:
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")
    
    def get_config_value(self, key):
        """Get a configuration value.
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value
        """
        return getattr(config, key, None)
