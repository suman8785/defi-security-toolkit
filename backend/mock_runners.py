"""
Mock implementations for tools that don't work on Streamlit Cloud
"""
import json
import random
from datetime import datetime
from typing import Dict, List, Any

def mock_slither_analyze(contract_path: str) -> Dict[str, Any]:
    """Mock Slither analysis for cloud deployment"""
    # Simulate some vulnerabilities
    vulnerabilities = [
        {
            'title': 'Reentrancy vulnerability detected',
            'severity': 'high',
            'confidence': 'high',
            'description': 'External call before state update in withdraw function',
            'location': 'Line 25-30',
            'recommendation': 'Use checks-effects-interactions pattern or ReentrancyGuard',
            'code_snippet': ''
        },
        {
            'title': 'Use of tx.origin',
            'severity': 'medium',
            'confidence': 'high',
            'description': 'tx.origin used for authorization',
            'location': 'Line 45',
            'recommendation': 'Use msg.sender instead of tx.origin',
            'code_snippet': ''
        }
    ]
    
    return {
        'success': True,
        'vulnerabilities': vulnerabilities,
        'summary': {
            'total': len(vulnerabilities),
            'critical': 0,
            'high': 1,
            'medium': 1,
            'low': 0,
            'informational': 0
        }
    }

def mock_mythril_analyze(contract_path: str) -> Dict[str, Any]:
    """Mock Mythril analysis for cloud deployment"""
    issues = [
        {
            'title': 'Integer Overflow',
            'severity': 'high',
            'description': 'Potential integer overflow in arithmetic operation',
            'location': 'Line 67',
            'code': '',
            'function': 'transfer',
            'swc_id': 'SWC-101',
            'recommendation': 'Use SafeMath library or Solidity 0.8+'
        }
    ]
    
    return {
        'success': True,
        'issues': issues,
        'summary': {
            'total': len(issues),
            'high': 1,
            'medium': 0,
            'low': 0
        }
    }
