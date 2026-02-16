"""Test setup utilities for Robot Framework tests."""

import os
from datetime import datetime, timezone
from pathlib import Path


def setup_results_directory(test_suite_name):
    """Create results directory with timestamp and test suite name.
    
    Creates directory in format: results/YYYY-MM-DD-HH-MM-SS/testsuite-name
    
    Args:
        test_suite_name: Name of the test suite
        
    Returns:
        Path to the created results directory
    """
    # Get current UTC timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
    
    # Create results path
    results_path = Path("results") / timestamp / test_suite_name
    results_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Created results directory: {results_path}")
    
    return str(results_path)


def get_results_directory(test_suite_name):
    """Get or create results directory for a test suite.
    
    Args:
        test_suite_name: Name of the test suite
        
    Returns:
        Path to the results directory
    """
    return setup_results_directory(test_suite_name)
