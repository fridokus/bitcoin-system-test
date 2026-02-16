"""Unit tests for metrics collector."""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys
import os
import time

# Add resources/lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'resources', 'lib'))
from metrics_collector import MetricsCollector


class TestMetricsCollector(unittest.TestCase):
    """Test cases for MetricsCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.collector = MetricsCollector()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.collector.stop_all_metrics_collection()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_collector_initialization(self):
        """Test that collector is initialized correctly."""
        self.assertIsInstance(self.collector.collection_threads, dict)
        self.assertIsInstance(self.collector.metrics_data, dict)
        self.assertEqual(len(self.collector.collection_threads), 0)
    
    def test_metrics_data_storage(self):
        """Test that metrics data is stored correctly."""
        # Manually add some metrics data
        self.collector.metrics_data['test_node'] = [
            {'timestamp': '2024-01-01T00:00:00', 'blockchain_info': {'blocks': 100}},
            {'timestamp': '2024-01-01T00:00:10', 'blockchain_info': {'blocks': 101}},
        ]
        
        summary = self.collector.get_metrics_summary('test_node')
        self.assertEqual(summary['total_snapshots'], 2)
        self.assertEqual(summary['initial_block_count'], 100)
        self.assertEqual(summary['final_block_count'], 101)
        self.assertEqual(summary['blocks_synced'], 1)
    
    def test_save_metrics_to_file(self):
        """Test saving metrics to file."""
        # Add some test data
        self.collector.metrics_data['test_node'] = [
            {'timestamp': '2024-01-01T00:00:00', 'blockchain_info': {'blocks': 100}},
        ]
        
        output_file = Path(self.test_dir) / 'metrics.json'
        self.collector.save_metrics_to_file('test_node', str(output_file))
        
        # Verify file exists and contains correct data
        self.assertTrue(output_file.exists())
        with open(output_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['blockchain_info']['blocks'], 100)
    
    def test_get_metrics_summary_empty(self):
        """Test getting summary for node with no data."""
        summary = self.collector.get_metrics_summary('nonexistent')
        self.assertEqual(summary, {})


if __name__ == '__main__':
    unittest.main()
