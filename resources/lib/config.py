"""Centralized configuration for Bitcoin Core tests."""

import configparser
import os
from pathlib import Path


def _get_config_path():
    """Get the path to the config.ini file."""
    # Allow override via environment variable
    env_config_path = os.environ.get("BITCOIN_TEST_CONFIG")
    if env_config_path:
        config_path = Path(env_config_path)
        if config_path.exists():
            return config_path
        raise FileNotFoundError(f"Config file specified in BITCOIN_TEST_CONFIG not found: {env_config_path}")
    
    # Search up the directory tree for config.ini
    current_dir = Path(__file__).resolve().parent
    for parent in [current_dir] + list(current_dir.parents):
        config_path = parent / "config.ini"
        if config_path.exists():
            return config_path
    
    raise FileNotFoundError("config.ini not found in repository. Please ensure it exists in the repository root.")


def _load_config():
    """Load configuration from config.ini file."""
    config = configparser.ConfigParser()
    config_path = _get_config_path()
    
    # Check if file is readable
    if not os.access(config_path, os.R_OK):
        raise PermissionError(f"Cannot read configuration file {config_path}. Check file permissions.")
    
    try:
        files_read = config.read(config_path)
        if not files_read:
            raise RuntimeError(f"Failed to read configuration from {config_path}.")
    except configparser.Error as e:
        raise ValueError(f"Invalid INI syntax in {config_path}: {e}")
    
    return config


# Load configuration
_config = _load_config()

# Bitcoin Core settings
BITCOIN_VERSION = _config.get("bitcoin", "version")
BITCOIN_DOWNLOAD_TIMEOUT = _config.getint("bitcoin", "download_timeout")

# Node settings
DEFAULT_GENERATOR_PORT = _config.getint("node", "default_generator_port")
DEFAULT_VICTIM_PORT = _config.getint("node", "default_victim_port")
DEFAULT_VICTIM_RPC_PORT = _config.getint("node", "default_victim_rpc_port")

# Network settings
DEFAULT_BIND_ADDRESS = _config.get("network", "default_bind_address")

# Timeout settings
NODE_START_TIMEOUT = _config.getint("timeouts", "node_start_timeout")
NODE_STOP_TIMEOUT = _config.getint("timeouts", "node_stop_timeout")
BLOCK_GENERATION_TIMEOUT = _config.getint("timeouts", "block_generation_timeout")
SYNC_TIMEOUT = _config.getint("timeouts", "sync_timeout")

# Fault injection settings
DEFAULT_FAULT_PROBABILITY_LOW = _config.getfloat("fault_injection", "default_fault_probability_low")
DEFAULT_FAULT_PROBABILITY_HIGH = _config.getfloat("fault_injection", "default_fault_probability_high")
FAULT_INJECTION_RETRY_MAX = _config.getint("fault_injection", "fault_injection_retry_max")
FAULT_INJECTION_RETRY_WAIT = _config.getint("fault_injection", "fault_injection_retry_wait")

# Test settings
INITIAL_BLOCK_COUNT = _config.getint("test", "initial_block_count")
ADDITIONAL_BLOCK_COUNT = _config.getint("test", "additional_block_count")

# Logging settings
LOG_LEVEL_CONSOLE = _config.get("logging", "log_level_console")
LOG_LEVEL_FILE = _config.get("logging", "log_level_file")
DEBUG_LOG_TAIL_LINES = _config.getint("logging", "debug_log_tail_lines")

# Metrics collection settings
METRICS_COLLECTION_INTERVAL = _config.getint("metrics", "metrics_collection_interval")
METRICS_ENABLED = _config.getboolean("metrics", "metrics_enabled")

# Directory settings
DEFAULT_GENERATOR_DIR = _config.get("directories", "default_generator_dir")
DEFAULT_VICTIM_DIR = _config.get("directories", "default_victim_dir")

# Wallet settings
DEFAULT_WALLET_NAME = _config.get("wallet", "default_wallet_name")
