"""Test setup library for Robot Framework."""

import os
import sys
from pathlib import Path

# Add src to path to import test_setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.test_setup import setup_results_directory


class TestSetup:
    """Library for test setup operations."""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        """Initialize TestSetup library."""
        self.results_dir = None
    
    def setup_results_directory(self, test_suite_name):
        """Create and return results directory with timestamp.
        
        Creates directory in format: results/YYYY-MM-DD-HH-MM-SS/testsuite-name
        Also creates an environment variable ROBOT_RESULTS_DIR for use in command line.
        
        Args:
            test_suite_name: Name of the test suite
            
        Returns:
            Path to the created results directory
        """
        self.results_dir = setup_results_directory(test_suite_name)
        
        # Set environment variable so it can be used outside Robot Framework
        os.environ['ROBOT_RESULTS_DIR'] = self.results_dir
        
        return self.results_dir
    
    def get_results_directory(self):
        """Get the current results directory.
        
        Returns:
            Path to the results directory or None if not set
        """
        return self.results_dir
