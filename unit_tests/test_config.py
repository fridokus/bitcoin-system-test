"""Unit tests for config module."""

import unittest
import sys
import os

# Add resources/lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'resources', 'lib'))
import config


class TestConfig(unittest.TestCase):
    """Test cases for configuration module."""
    
    def test_bitcoin_settings(self):
        """Test that Bitcoin settings are defined."""
        self.assertIsInstance(config.BITCOIN_VERSION, str)
        self.assertIsInstance(config.BITCOIN_DOWNLOAD_TIMEOUT, int)
    
    def test_port_settings(self):
        """Test that port settings are defined."""
        self.assertIsInstance(config.DEFAULT_GENERATOR_PORT, int)
        self.assertIsInstance(config.DEFAULT_VICTIM_PORT, int)
        self.assertIsInstance(config.DEFAULT_VICTIM_RPC_PORT, int)
    
    def test_timeout_settings(self):
        """Test that timeout settings are defined."""
        self.assertIsInstance(config.NODE_START_TIMEOUT, int)
        self.assertIsInstance(config.SYNC_TIMEOUT, int)
    
    def test_fault_injection_settings(self):
        """Test that fault injection settings are defined."""
        self.assertIsInstance(config.DEFAULT_FAULT_PROBABILITY_LOW, float)
        self.assertIsInstance(config.DEFAULT_FAULT_PROBABILITY_HIGH, float)
        self.assertIsInstance(config.FAULT_INJECTION_RETRY_MAX, int)


if __name__ == '__main__':
    unittest.main()
