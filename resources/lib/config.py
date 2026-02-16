"""Centralized configuration for Bitcoin Core tests."""

# Bitcoin Core settings
BITCOIN_VERSION = "30.2"
BITCOIN_DOWNLOAD_TIMEOUT = 300  # seconds

# Node settings
DEFAULT_GENERATOR_PORT = 18444
DEFAULT_VICTIM_PORT = 18445
DEFAULT_VICTIM_RPC_PORT = 18446

# Network settings
DEFAULT_BIND_ADDRESS = "127.0.0.1"

# Timeout settings
NODE_START_TIMEOUT = 30  # seconds
NODE_STOP_TIMEOUT = 10  # seconds
BLOCK_GENERATION_TIMEOUT = 60  # seconds
SYNC_TIMEOUT = 120  # seconds

# Fault injection settings
DEFAULT_FAULT_PROBABILITY_LOW = 0.005
DEFAULT_FAULT_PROBABILITY_HIGH = 0.01
FAULT_INJECTION_RETRY_MAX = 3
FAULT_INJECTION_RETRY_WAIT = 5  # seconds

# Test settings
INITIAL_BLOCK_COUNT = 150
ADDITIONAL_BLOCK_COUNT = 10

# Logging settings
LOG_LEVEL_CONSOLE = "INFO"
LOG_LEVEL_FILE = "DEBUG"
DEBUG_LOG_TAIL_LINES = 50

# Metrics collection settings
METRICS_COLLECTION_INTERVAL = 10  # seconds
METRICS_ENABLED = True

# Directory settings
DEFAULT_GENERATOR_DIR = "/tmp/node_generator"
DEFAULT_VICTIM_DIR = "/tmp/node_victim"

# Wallet settings
DEFAULT_WALLET_NAME = "miner"
