import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
CONTRACTS_DIR = BASE_DIR / "contracts"
SLITHER_REPORTS_DIR = BASE_DIR / "slither-reports"
MYTHRIL_REPORTS_DIR = BASE_DIR / "mythril-reports"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for dir_path in [SLITHER_REPORTS_DIR, MYTHRIL_REPORTS_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# API Configuration
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "YourEtherscanAPIKey")
TENDERLY_API_KEY = os.getenv("TENDERLY_API_KEY", "YourTenderlyAPIKey")
TENDERLY_PROJECT = os.getenv("TENDERLY_PROJECT", "project")
TENDERLY_USERNAME = os.getenv("TENDERLY_USERNAME", "username")

# Network Configuration
NETWORK = os.getenv("NETWORK", "sepolia")
RPC_URL = os.getenv("RPC_URL", "https://sepolia.infura.io/v3/YOUR_INFURA_KEY")

# Analysis Configuration
SLITHER_TIMEOUT = 300  # seconds
MYTHRIL_TIMEOUT = 600  # seconds
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Security thresholds
CRITICAL_SEVERITY = ["high", "critical"]
WARNING_SEVERITY = ["medium", "low"]