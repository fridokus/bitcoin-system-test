#!/usr/bin/env python3
"""Test runner script for Robot Framework tests with timestamped results."""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone


def run_robot_test(test_file, test_suite_name=None):
    """Run Robot Framework test with timestamped results directory.
    
    Args:
        test_file: Path to the Robot Framework test file
        test_suite_name: Name for the results directory (defaults to test file name)
    """
    # Determine test suite name
    if test_suite_name is None:
        test_suite_name = Path(test_file).stem
    
    # Create timestamped results directory
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
    results_dir = Path("results") / timestamp / test_suite_name
    results_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Running test: {test_file}")
    print(f"Results directory: {results_dir}")
    
    # Add current directory to PYTHONPATH so resources can be imported
    env = os.environ.copy()
    pythonpath = env.get('PYTHONPATH', '')
    current_dir = os.getcwd()
    if pythonpath:
        env['PYTHONPATH'] = f"{current_dir}:{pythonpath}"
    else:
        env['PYTHONPATH'] = current_dir
    
    # Export results directory for Python libraries to use
    env['ROBOT_OUTPUT_DIR'] = str(results_dir)
    
    # Run robot with the output directory
    cmd = ["robot", "--outputdir", str(results_dir), test_file]
    
    result = subprocess.run(cmd, env=env)
    
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: run_tests.py <test_file> [test_suite_name]")
        sys.exit(1)
    
    test_file = sys.argv[1]
    test_suite_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    exit_code = run_robot_test(test_file, test_suite_name)
    sys.exit(exit_code)
