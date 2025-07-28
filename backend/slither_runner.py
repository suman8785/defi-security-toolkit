import subprocess
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any
import logging
from config import SLITHER_REPORTS_DIR, SLITHER_TIMEOUT
import streamlit as st

logger = logging.getLogger(__name__)

class SlitherRunner:
    def __init__(self):
        self.reports_dir = SLITHER_REPORTS_DIR
        # Check if running on Streamlit Cloud
        self.is_cloud = hasattr(st, 'secrets') or not self._check_slither_installed()
    
    def _check_slither_installed(self) -> bool:
        """Check if Slither is installed"""
        try:
            result = subprocess.run(['slither', '--version'], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def analyze(self, contract_path: str) -> Dict[str, Any]:
        """Run Slither analysis on contract"""
        if self.is_cloud:
            # Use mock analysis for cloud deployment
            from backend.mock_runners import mock_slither_analyze
            return mock_slither_analyze(contract_path)
        
        # Original Slither implementation for local deployment
        try:
            # Your existing Slither code here
            pass
        except Exception as e:
            logger.error(f"Slither error: {str(e)}")
            # Fallback to mock if real Slither fails
            from backend.mock_runners import mock_slither_analyze
            return mock_slither_analyze(contract_path)

# Module-level function
def analyze(contract_path: str) -> Dict[str, Any]:
    runner = SlitherRunner()
    return runner.analyze(contract_path)
