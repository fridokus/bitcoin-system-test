"""Unit tests for logger utility."""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from util.logger import DualLogger, get_logger


class TestDualLogger(unittest.TestCase):
    """Test cases for DualLogger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.test_dir) / "logs"
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_logger_creation(self):
        """Test that logger is created with correct handlers."""
        logger = DualLogger("test", log_dir=self.log_dir)
        
        # Check that log files are created
        normal_log, debug_log = logger.get_log_paths()
        self.assertTrue(os.path.exists(normal_log))
        self.assertTrue(os.path.exists(debug_log))
    
    def test_logging_levels(self):
        """Test that different log levels work correctly."""
        logger = DualLogger("test_levels", log_dir=self.log_dir)
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Check that messages are written to files
        normal_log, debug_log = logger.get_log_paths()
        
        with open(debug_log, 'r') as f:
            debug_content = f.read()
            self.assertIn("Debug message", debug_content)
            self.assertIn("Info message", debug_content)
        
        with open(normal_log, 'r') as f:
            normal_content = f.read()
            self.assertNotIn("Debug message", normal_content)
            self.assertIn("Info message", normal_content)
    
    def test_get_logger_function(self):
        """Test the get_logger helper function."""
        logger = get_logger("helper_test", log_dir=self.log_dir)
        self.assertIsInstance(logger, DualLogger)


if __name__ == '__main__':
    unittest.main()
