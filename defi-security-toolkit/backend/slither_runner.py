import subprocess
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any
import logging
from config import SLITHER_REPORTS_DIR, SLITHER_TIMEOUT

logger = logging.getLogger(_name_)

class SlitherRunner:
    def _init_(self):
        self.reports_dir = SLITHER_REPORTS_DIR
    
    def analyze(self, contract_path: str) -> Dict[str, Any]:
        """Run Slither analysis on contract"""
        try:
            # Generate output path
            contract_name = Path(contract_path).stem
            output_path = self.reports_dir / f"{contract_name}_slither.json"
            
            # Run Slither
            cmd = [
                "slither",
                contract_path,
                "--json", str(output_path),
                "--json-types", "detectors",
                "--exclude", "naming-convention,solc-version"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=SLITHER_TIMEOUT
            )
            
            # Parse results
            if output_path.exists():
                with open(output_path, 'r') as f:
                    raw_results = json.load(f)
                
                return self._parse_results(raw_results)
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'vulnerabilities': []
                }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Slither timeout analyzing {contract_path}")
            return {
                'success': False,
                'error': 'Analysis timeout',
                'vulnerabilities': []
            }
        except Exception as e:
            logger.error(f"Slither error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'vulnerabilities': []
            }
    
    def _parse_results(self, raw_results: Dict) -> Dict[str, Any]:
                """Parse Slither JSON output into structured format"""
        vulnerabilities = []
        
        if 'results' in raw_results and 'detectors' in raw_results['results']:
            for detector in raw_results['results']['detectors']:
                vulnerability = {
                    'title': detector.get('check', 'Unknown'),
                    'severity': detector.get('impact', 'unknown').lower(),
                    'confidence': detector.get('confidence', 'unknown').lower(),
                    'description': detector.get('description', ''),
                    'location': self._format_location(detector.get('elements', [])),
                    'recommendation': self._get_recommendation(detector.get('check', '')),
                    'code_snippet': self._extract_code_snippet(detector.get('elements', []))
                }
                vulnerabilities.append(vulnerability)
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'informational': 4}
        vulnerabilities.sort(key=lambda x: severity_order.get(x['severity'], 5))
        
        return {
            'success': True,
            'vulnerabilities': vulnerabilities,
            'summary': {
                'total': len(vulnerabilities),
                'critical': sum(1 for v in vulnerabilities if v['severity'] == 'critical'),
                'high': sum(1 for v in vulnerabilities if v['severity'] == 'high'),
                'medium': sum(1 for v in vulnerabilities if v['severity'] == 'medium'),
                'low': sum(1 for v in vulnerabilities if v['severity'] == 'low'),
                'informational': sum(1 for v in vulnerabilities if v['severity'] == 'informational')
            }
        }
    
    def _format_location(self, elements: List[Dict]) -> str:
        """Format element locations"""
        if not elements:
            return "Unknown"
        
        locations = []
        for element in elements:
            if 'source_mapping' in element:
                lines = element['source_mapping'].get('lines', [])
                if lines:
                    locations.append(f"Lines {min(lines)}-{max(lines)}")
        
        return ", ".join(locations) if locations else "Unknown"
    
    def _extract_code_snippet(self, elements: List[Dict]) -> str:
        """Extract relevant code snippet"""
        # This would extract actual code in a real implementation
        # For now, return a placeholder
        return ""
    
    def _get_recommendation(self, check_name: str) -> str:
        """Get recommendation based on vulnerability type"""
        recommendations = {
            'reentrancy': 'Use ReentrancyGuard or check-effects-interactions pattern',
            'arbitrary-send': 'Validate recipient addresses and amounts',
            'unchecked-transfer': 'Check return values of transfer calls',
            'uninitialized-state': 'Initialize all state variables',
            'tx-origin': 'Use msg.sender instead of tx.origin',
            'timestamp': 'Avoid using block.timestamp for critical logic',
            'weak-prng': 'Use chainlink VRF for secure randomness'
        }
        
        for key, rec in recommendations.items():
            if key in check_name.lower():
                return rec
        
        return "Review and fix the identified issue"

# Module-level function
def analyze(contract_path: str) -> Dict[str, Any]:
    runner = SlitherRunner()
    return runner.analyze(contract_path)