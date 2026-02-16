"""Bitcoin Core metrics collection for observability."""

import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from datetime import datetime, timezone

# Import config and logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.logger import get_logger


class MetricsCollector:
    """Collects Bitcoin Core metrics periodically during test execution."""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        """Initialize MetricsCollector."""
        self.logger = get_logger('metrics_collector')
        self.collection_threads = {}
        self.stop_events = {}
        self.metrics_data = {}
        self.metrics_lock = threading.Lock()
    
    def start_metrics_collection(self, node_name, datadir, bitcoin_cli_path, interval=10, rpcport=None):
        """Start collecting metrics for a Bitcoin Core node.
        
        Args:
            node_name: Name identifier for the node (e.g., 'generator', 'victim')
            datadir: Data directory of the node
            bitcoin_cli_path: Path to bitcoin-cli executable
            interval: Collection interval in seconds (default: 10)
            rpcport: RPC port (optional)
        """
        if node_name in self.collection_threads:
            self.logger.warning(f"Metrics collection already running for {node_name}")
            return
        
        self.logger.info(f"Starting metrics collection for {node_name} (interval: {interval}s)")
        
        # Initialize storage for this node
        with self.metrics_lock:
            self.metrics_data[node_name] = []
        
        # Create stop event
        stop_event = threading.Event()
        self.stop_events[node_name] = stop_event
        
        # Start collection thread
        thread = threading.Thread(
            target=self._collect_metrics_loop,
            args=(node_name, datadir, bitcoin_cli_path, interval, rpcport, stop_event),
            daemon=True
        )
        thread.start()
        self.collection_threads[node_name] = thread
        
        self.logger.debug(f"Metrics collection thread started for {node_name}")
    
    def stop_metrics_collection(self, node_name):
        """Stop collecting metrics for a node.
        
        Args:
            node_name: Name identifier for the node
        """
        if node_name not in self.collection_threads:
            self.logger.warning(f"No metrics collection running for {node_name}")
            return
        
        self.logger.info(f"Stopping metrics collection for {node_name}")
        
        # Signal the thread to stop
        self.stop_events[node_name].set()
        
        # Wait for thread to finish
        self.collection_threads[node_name].join(timeout=5)
        
        # Cleanup
        del self.collection_threads[node_name]
        del self.stop_events[node_name]
        
        self.logger.debug(f"Metrics collection stopped for {node_name}")
    
    def stop_all_metrics_collection(self):
        """Stop all metrics collection threads."""
        self.logger.info("Stopping all metrics collection")
        
        node_names = list(self.collection_threads.keys())
        for node_name in node_names:
            self.stop_metrics_collection(node_name)
    
    def save_metrics_to_file(self, node_name, output_file):
        """Save collected metrics to a JSON file.
        
        Args:
            node_name: Name identifier for the node
            output_file: Output file path
        """
        with self.metrics_lock:
            if node_name not in self.metrics_data:
                self.logger.warning(f"No metrics data found for {node_name}")
                return
            
            metrics_snapshot = self.metrics_data[node_name].copy()
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(metrics_snapshot, f, indent=2)
        
        self.logger.info(f"Saved {len(metrics_snapshot)} metrics snapshots for {node_name} to {output_file}")
    
    def get_metrics_summary(self, node_name):
        """Get a summary of collected metrics.
        
        Args:
            node_name: Name identifier for the node
            
        Returns:
            Dictionary with metrics summary
        """
        with self.metrics_lock:
            if node_name not in self.metrics_data:
                return {}
            
            metrics = self.metrics_data[node_name].copy()
        
        if not metrics:
            return {}
        
        # Calculate summary statistics
        block_counts = [m.get('blockchain_info', {}).get('blocks', 0) for m in metrics]
        peer_counts = [len(m.get('peer_info', [])) for m in metrics]
        
        summary = {
            'total_snapshots': len(metrics),
            'first_snapshot': metrics[0].get('timestamp'),
            'last_snapshot': metrics[-1].get('timestamp'),
            'initial_block_count': block_counts[0] if block_counts else 0,
            'final_block_count': block_counts[-1] if block_counts else 0,
            'blocks_synced': block_counts[-1] - block_counts[0] if block_counts else 0,
            'avg_peer_count': sum(peer_counts) / len(peer_counts) if peer_counts else 0,
            'max_peer_count': max(peer_counts) if peer_counts else 0,
        }
        
        return summary
    
    def _collect_metrics_loop(self, node_name, datadir, bitcoin_cli_path, interval, rpcport, stop_event):
        """Background loop to collect metrics periodically.
        
        Args:
            node_name: Name identifier for the node
            datadir: Data directory of the node
            bitcoin_cli_path: Path to bitcoin-cli executable
            interval: Collection interval in seconds
            rpcport: RPC port (optional)
            stop_event: Threading event to signal stop
        """
        while not stop_event.is_set():
            try:
                metrics = self._collect_node_metrics(node_name, datadir, bitcoin_cli_path, rpcport)
                if metrics:
                    with self.metrics_lock:
                        self.metrics_data[node_name].append(metrics)
                    self.logger.debug(f"Collected metrics for {node_name}: blocks={metrics.get('blockchain_info', {}).get('blocks', 'N/A')}, peers={len(metrics.get('peer_info', []))}")
            except Exception as e:
                self.logger.error(f"Error collecting metrics for {node_name}: {e}")
            
            # Wait for interval or stop signal
            stop_event.wait(timeout=interval)
    
    def _collect_node_metrics(self, node_name, datadir, bitcoin_cli_path, rpcport):
        """Collect metrics from a Bitcoin Core node.
        
        Args:
            node_name: Name identifier for the node
            datadir: Data directory of the node
            bitcoin_cli_path: Path to bitcoin-cli executable
            rpcport: RPC port (optional)
            
        Returns:
            Dictionary with collected metrics
        """
        metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'node_name': node_name,
        }
        
        # Collect getblockchaininfo
        blockchain_info = self._execute_rpc(bitcoin_cli_path, datadir, 'getblockchaininfo', rpcport)
        if blockchain_info:
            metrics['blockchain_info'] = blockchain_info
        
        # Collect getpeerinfo
        peer_info = self._execute_rpc(bitcoin_cli_path, datadir, 'getpeerinfo', rpcport)
        if peer_info:
            metrics['peer_info'] = peer_info
        
        return metrics
    
    def _execute_rpc(self, bitcoin_cli_path, datadir, command, rpcport=None):
        """Execute an RPC command and return parsed JSON result.
        
        Args:
            bitcoin_cli_path: Path to bitcoin-cli executable
            datadir: Data directory
            command: RPC command to execute
            rpcport: RPC port (optional)
            
        Returns:
            Parsed JSON result or None on error
        """
        cmd = [bitcoin_cli_path, "-regtest", f"-datadir={datadir}"]
        
        if rpcport:
            cmd.append(f"-rpcport={rpcport}")
        
        cmd.append(command)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                # Node might not be ready yet, don't log error
                return None
        except Exception:
            # Silently handle errors (node might not be ready)
            return None
