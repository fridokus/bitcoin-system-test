"""Bitcoin Core node management for Robot Framework tests."""

import os
import subprocess
import sys
import time
from pathlib import Path

# Import config and logging
from . import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.logger import get_logger


class BitcoinCore:
    """Library for managing Bitcoin Core nodes."""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, bitcoin_version=None):
        """Initialize BitcoinCore library.
        
        Args:
            bitcoin_version: Version of Bitcoin Core to use (default: from config)
        """
        self.bitcoin_version = bitcoin_version or config.BITCOIN_VERSION
        self.bitcoin_dir = f"bitcoin-{self.bitcoin_version}"
        self.bitcoind = f"{self.bitcoin_dir}/bin/bitcoind"
        self.bitcoin_cli = f"{self.bitcoin_dir}/bin/bitcoin-cli"
        self.logger = get_logger('bitcoin_core')

    def download_bitcoin_core(self, version=None):
        """Download and extract Bitcoin Core release.
        
        Args:
            version: Version to download (uses default if not specified)
        """
        if version is None:
            version = self.bitcoin_version
        
        tarball = f"bitcoin-{version}-x86_64-linux-gnu.tar.gz"
        url = f"https://bitcoincore.org/bin/bitcoin-core-{version}/{tarball}"
        
        self.logger.info(f"Downloading Bitcoin Core {version}")
        result = subprocess.run(["wget", url], capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"Failed to download Bitcoin Core: {result.stderr}")
            raise RuntimeError(f"Failed to download Bitcoin Core: {result.stderr}")
        
        if not os.path.exists(tarball):
            raise RuntimeError(f"Download file {tarball} not found")
        
        self.logger.info("Extracting Bitcoin Core")
        result = subprocess.run(["tar", "-xzf", tarball], capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"Failed to extract Bitcoin Core: {result.stderr}")
            raise RuntimeError(f"Failed to extract Bitcoin Core: {result.stderr}")
        
        if not os.path.exists(self.bitcoin_dir):
            raise RuntimeError(f"Bitcoin directory {self.bitcoin_dir} not found after extraction")

    def start_bitcoin_node(self, datadir, port, rpcport=None, connect=None, daemon=True):
        """Start a Bitcoin node in regtest mode.
        
        Args:
            datadir: Data directory for the node
            port: P2P port
            rpcport: RPC port (optional)
            connect: Address to connect to (optional)
            daemon: Run as daemon (default: True)
        """
        self.logger.info(f"Starting Bitcoin node with datadir={datadir}, port={port}")
        
        cmd = [self.bitcoind, "-regtest", f"-datadir={datadir}", f"-port={port}", "-bind=127.0.0.1"]
        
        if rpcport:
            cmd.append(f"-rpcport={rpcport}")
        if connect:
            cmd.append(f"-connect={connect}")
        if daemon:
            cmd.append("-daemon")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"Failed to start Bitcoin node: {result.stderr}")
            raise RuntimeError(f"Failed to start Bitcoin node: {result.stderr}")
        
        time.sleep(2)  # Wait for node to start
        self.logger.debug(f"Bitcoin node started successfully")

    def stop_bitcoin_node(self, datadir):
        """Stop a Bitcoin node.
        
        Args:
            datadir: Data directory of the node to stop
        """
        print(f"Stopping Bitcoin node with datadir={datadir}")
        pid_file = Path(datadir) / "regtest" / "bitcoind.pid"
        
        if pid_file.exists():
            subprocess.run(["pkill", "-F", str(pid_file)], capture_output=True)
        
        time.sleep(1)  # Wait for node to stop

    def execute_bitcoin_cli(self, datadir, command, rpcport=None, rpcwallet=None):
        """Execute bitcoin-cli command.
        
        Args:
            datadir: Data directory
            command: Command string to execute
            rpcport: RPC port (optional)
            rpcwallet: Wallet name (optional)
            
        Returns:
            Command output as string
        """
        cmd = [self.bitcoin_cli, "-regtest", f"-datadir={datadir}"]
        
        if rpcport:
            cmd.append(f"-rpcport={rpcport}")
        if rpcwallet:
            cmd.append(f"-rpcwallet={rpcwallet}")
        
        cmd.extend(command.split())
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"CLI command failed: {result.stderr}")
        
        return result.stdout.strip()

    def get_block_count(self, datadir, rpcport=None):
        """Get the current block count.
        
        Args:
            datadir: Data directory
            rpcport: RPC port (optional)
            
        Returns:
            Block count as integer
        """
        output = self.execute_bitcoin_cli(datadir, "getblockcount", rpcport=rpcport)
        return int(output.strip())

    def create_wallet(self, datadir, wallet_name, rpcport=None):
        """Create a wallet.
        
        Args:
            datadir: Data directory
            wallet_name: Name of wallet to create
            rpcport: RPC port (optional)
        """
        output = self.execute_bitcoin_cli(datadir, f"createwallet {wallet_name}", rpcport=rpcport)
        print(f"Wallet created: {output}")

    def generate_blocks(self, datadir, wallet_name, count, rpcport=None):
        """Generate blocks to an address.
        
        Args:
            datadir: Data directory
            wallet_name: Wallet to use
            count: Number of blocks to generate
            rpcport: RPC port (optional)
        """
        address = self.execute_bitcoin_cli(
            datadir, "getnewaddress", rpcport=rpcport, rpcwallet=wallet_name
        )
        
        output = self.execute_bitcoin_cli(
            datadir, 
            f"generatetoaddress {count} {address.strip()}", 
            rpcport=rpcport, 
            rpcwallet=wallet_name
        )
        print(f"Generated {count} blocks")

    def wait_for_node_to_start(self, datadir, rpcport=None, timeout=30):
        """Wait for node to be responsive.
        
        Args:
            datadir: Data directory
            rpcport: RPC port (optional)
            timeout: Timeout in seconds (default: 30)
        """
        for i in range(timeout):
            try:
                self.execute_bitcoin_cli(datadir, "getblockchaininfo", rpcport=rpcport)
                return  # Success
            except RuntimeError:
                time.sleep(1)
        
        raise RuntimeError(f"Node did not start within {timeout} seconds")

    def clean_node_directory(self, datadir):
        """Remove all files in a node directory.
        
        Args:
            datadir: Directory to clean
        """
        print(f"Cleaning directory {datadir}")
        import shutil
        
        if os.path.exists(datadir):
            shutil.rmtree(datadir)
        os.makedirs(datadir, exist_ok=True)

    def get_debug_log_path(self, datadir):
        """Get the path to the debug.log file.
        
        Args:
            datadir: Data directory
            
        Returns:
            Path to debug.log
        """
        return str(Path(datadir) / "regtest" / "debug.log")

    def monitor_debug_log(self, datadir, lines=50):
        """Get the last N lines from debug.log.
        
        Args:
            datadir: Data directory
            lines: Number of lines to retrieve (default: 50)
            
        Returns:
            Last N lines of debug.log as string
        """
        log_path = Path(datadir) / "regtest" / "debug.log"
        
        if not log_path.exists():
            return "Debug log not found"
        
        result = subprocess.run(
            ["tail", "-n", str(lines), str(log_path)],
            capture_output=True,
            text=True
        )
        
        return result.stdout

    def check_node_is_running(self, datadir):
        """Check if a node is running.
        
        Args:
            datadir: Data directory
            
        Returns:
            True if node is running, False otherwise
        """
        pid_file = Path(datadir) / "regtest" / "bitcoind.pid"
        
        if not pid_file.exists():
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            return False
