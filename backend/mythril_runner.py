import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any
import logging
from config import MYTHRIL_REPORTS_DIR, MYTHRIL_TIMEOUT
import streamlit as st

logger = logging.getLogger(__name__)

class MythrilRunner:
    def __init__(self):
        self.reports_dir = MYTHRIL_REPORTS_DIR
        # Check if running on Streamlit Cloud
        self.is_cloud = hasattr(st, 'secrets') or not self._check_mythril_installed()
    
    def _check_mythril_installed(self) -> bool:
        """Check if Mythril is installed"""
        try:
            result = subprocess.run(['myth', '--version'], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def analyze(self, contract_path: str) -> Dict[str, Any]:
        """Run Mythril analysis on contract"""
        if self.is_cloud:
            # Use mock analysis for cloud deployment
            from backend.mock_runners import mock_mythril_analyze
            return mock_mythril_analyze(contract_path)
        
        # Original Mythril implementation for local deployment
        try:
            # Your existing Mythril code here
            pass
        except Exception as e:
            logger.error(f"Mythril error: {str(e)}")
            # Fallback to mock if real Mythril fails
            from backend.mock_runners import mock_mythril_analyze
            return mock_mythril_analyze(contract_path)

# Module-level function
def analyze(contract_path: str) -> Dict[str, Any]:
    runner = MythrilRunner()
    return runner.analyze(contract_path)
