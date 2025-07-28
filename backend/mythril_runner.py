import subprocess
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any
import logging
from config import MYTHRIL_REPORTS_DIR, MYTHRIL_TIMEOUT

logger = logging.getLogger(__name__)

class MythrilRunner:
    def _init_(self):
        self.reports_dir = MYTHRIL_REPORTS_DIR
    
    def analyze(self, contract_path: str) -> Dict[str, Any]:
        """Run Mythril analysis on contract"""
        try:
            # Generate output path
            contract_name = Path(contract_path).stem
            output_path = self.reports_dir / f"{contract_name}_mythril.json"
            
            # Run Mythril
            cmd = [
                "myth", "analyze",
                contract_path,
                "-o", "json",
                "--execution-timeout", str(MYTHRIL_TIMEOUT),
                "--solver-timeout", "10000"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=MYTHRIL_TIMEOUT
            )
            
            # Parse results
            if result.stdout:
                try:
                    raw_results = json.loads(result.stdout)
                    # Save to file
                    with open(output_path, 'w') as f:
                        json.dump(raw_results, f, indent=2)
                    
                    return self._parse_results(raw_results)
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': 'Failed to parse Mythril output',
                        'issues': []
                    }
            else:
                return {
                    'success': True,
                    'issues': [],
                    'message': 'No issues found'
                }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Mythril timeout analyzing {contract_path}")
            return {
                'success': False,
                'error': 'Analysis timeout',
                'issues': []
            }
        except Exception as e:
            logger.error(f"Mythril error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'issues': []
            }
    
    def _parse_results(self, raw_results: Dict) -> Dict[str, Any]:
        """Parse Mythril JSON output"""
        issues = []
        
        if 'issues' in raw_results:
            for issue in raw_results['issues']:
                parsed_issue = {
                    'title': issue.get('title', 'Unknown Issue'),
                    'severity': issue.get('severity', 'Unknown').lower(),
                    'description': issue.get('description', ''),
                    'location': f"Line {issue.get('lineno', 'Unknown')}",
                    'code': issue.get('code', ''),
                    'function': issue.get('function', 'Unknown'),
                    'swc_id': issue.get('swc-id', ''),
                    'recommendation': self._get_swc_recommendation(issue.get('swc-id', ''))
                }
                issues.append(parsed_issue)
        
        return {
            'success': True,
            'issues': issues,
            'summary': {
                'total': len(issues),
                'high': sum(1 for i in issues if i['severity'] == 'high'),
                'medium': sum(1 for i in issues if i['severity'] == 'medium'),
                'low': sum(1 for i in issues if i['severity'] == 'low')
            }
        }
    
    def _get_swc_recommendation(self, swc_id: str) -> str:
        """Get recommendation based on SWC ID"""
        swc_recommendations = {
            'SWC-101': 'Use SafeMath library or Solidity 0.8+ for arithmetic operations',
            'SWC-105': 'Implement reentrancy guards',
            'SWC-106': 'Avoid using delegatecall with user input',
            'SWC-107': 'Use check-effects-interactions pattern',
            'SWC-115': 'Use msg.sender instead of tx.origin',
            'SWC-116': 'Avoid using block.timestamp for critical logic',
            'SWC-120': 'Use secure randomness sources like Chainlink VRF'
        }
        
        return swc_recommendations.get(swc_id, 'Review the Smart Contract Weakness Classification for details')

# Module-level function
def analyze(contract_path: str) -> Dict[str, Any]:
    runner = MythrilRunner()
    return runner.analyze(contract_path)