"""Robustness testing library with fault injection support."""

import os
import subprocess
import sys
import time
from pathlib import Path

# Add paths for importing config and util modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

# Import config and logging
import config
from util.decorators import retry_on_error
from util.logger import get_logger


class RobustnessLib:
    """Library for fault injection and robustness testing."""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, bitcoin_version=None):
        """Initialize RobustnessLib.
        
        Args:
            bitcoin_version: Version of Bitcoin Core to use (default: from config)
        """
        self.bitcoin_version = bitcoin_version or config.BITCOIN_VERSION
        self.bitcoin_dir = f"bitcoin-{self.bitcoin_version}"
        self.bitcoind = f"{self.bitcoin_dir}/bin/bitcoind"
        self.bitcoin_cli = f"{self.bitcoin_dir}/bin/bitcoin-cli"
        self.logger = get_logger('robustness')

    def install_libfiu(self):
        """Install libfiu development package and utilities."""
        self.logger.info("Installing libfiu-dev and fiu-utils")
        
        # Update package list
        result = subprocess.run(
            ["sudo", "apt-get", "update", "-qq"],
            capture_output=True,
            text=True
        )
        
        # Install libfiu
        result = subprocess.run(
            ["sudo", "apt-get", "install", "-y", "libfiu-dev", "fiu-utils"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.logger.error(f"Failed to install libfiu: {result.stderr}")
            raise RuntimeError(f"Failed to install libfiu: {result.stderr}")
        
        self.logger.info("libfiu installed successfully")

    def _check_node_exited(self, datadir):
        """Check if node has exited by checking PID file and process.
        
        Args:
            datadir: Data directory
            
        Returns:
            True if node has exited, False if still running
        """
        pid_file = Path(datadir) / "regtest" / "bitcoind.pid"
        
        if not pid_file.exists():
            return True  # PID file doesn't exist, node not running
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)
            return False  # Process exists, still running
        except (OSError, ValueError):
            return True  # Process doesn't exist or error reading PID

    @retry_on_error(max_retries=config.FAULT_INJECTION_RETRY_MAX, wait_time=config.FAULT_INJECTION_RETRY_WAIT)
    def _start_victim_node(self, bitcoind_path, datadir, port, rpcport, connect, probability):
        """Start victim node with libfiu.
        
        This is wrapped with retry_on_error decorator to handle random failures.
        """
        self.logger.info(f"Starting victim node with fault injection (probability={probability})")
        
        fault_spec = f"enable_random name=posix/io/*,probability={probability}"
        
        cmd = [
            "fiu-run", "-x", "-c", fault_spec,
            bitcoind_path, "-regtest", f"-datadir={datadir}", 
            f"-port={port}", f"-rpcport={rpcport}", f"-connect={connect}",
            "-daemon"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"Failed to start victim node: {result.stderr}")
            raise RuntimeError(f"Failed to start victim node: {result.stderr}")
        
        # Give it a moment to start
        time.sleep(3)
        
        # Check if node is actually running after start
        if self._check_node_exited(datadir):
            self.logger.warning("Victim node exited shortly after start (likely due to fault injection)")
            raise RuntimeError("Victim node exited shortly after start (likely due to fault injection)")
        
        self.logger.info("Victim node started successfully")

    def start_victim_node_with_fault_injection(self, datadir, port, rpcport, connect, probability=0.005):
        """Start a victim node with libfiu fault injection and retry on failure.
        
        This keyword uses retry_on_error decorator to handle random failures
        caused by fault injection during startup.
        
        Args:
            datadir: Data directory for the node
            port: P2P port
            rpcport: RPC port
            connect: Address to connect to
            probability: Fault injection probability (default: 0.005)
        """
        self._start_victim_node(
            self.bitcoind, datadir, port, rpcport, connect, probability
        )

    def start_generator_node(self, datadir, port, daemon=True):
        """Start a generator node (normal node without fault injection).
        
        Args:
            datadir: Data directory for the node
            port: P2P port
            daemon: Run as daemon (default: True)
        """
        print(f"Starting generator node with datadir={datadir}, port={port}")
        
        cmd = [
            self.bitcoind, "-regtest", f"-datadir={datadir}",
            f"-port={port}", "-bind=127.0.0.1"
        ]
        
        if daemon:
            cmd.append("-daemon")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to start generator node: {result.stderr}")
        
        time.sleep(2)  # Wait for node to start

    def tail_debug_log(self, datadir, lines=100):
        """Display the last N lines of debug.log.
        
        Args:
            datadir: Data directory
            lines: Number of lines to display (default: 100)
            
        Returns:
            Last N lines as string
        """
        log_path = Path(datadir) / "regtest" / "debug.log"
        
        if not log_path.exists():
            return "Debug log not found"
        
        result = subprocess.run(
            ["tail", "-n", str(lines), str(log_path)],
            capture_output=True,
            text=True
        )
        
        print(f"=== Last {lines} lines of {log_path} ===")
        print(result.stdout)
        
        return result.stdout

    def copy_debug_log_to(self, datadir, destination):
        """Copy debug.log to a destination for artifacts.
        
        Args:
            datadir: Data directory
            destination: Destination file path
        """
        log_path = Path(datadir) / "regtest" / "debug.log"
        
        if not log_path.exists():
            print(f"Debug log not found at {log_path}")
            return
        
        import shutil
        dest_path = Path(destination)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(log_path, dest_path)
        print(f"Copied debug.log to {destination}")
