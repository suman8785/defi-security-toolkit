import subprocess
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
import logging
from config import LOGS_DIR

logger = logging.getLogger(__name__)

class EchidnaRunner:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "echidna.yaml"
        self.corpus_dir = LOGS_DIR / "echidna-corpus"
        self.corpus_dir.mkdir(exist_ok=True)
    
    def analyze(self, contract_path: str, contract_name: str = None) -> Dict[str, Any]:
        """Run Echidna fuzzing on contract"""
        try:
            # Prepare Echidna config
            config = self._prepare_config(contract_path, contract_name)
            
            # Write temporary config
            temp_config = LOGS_DIR / "echidna_temp.yaml"
            with open(temp_config, 'w') as f:
                yaml.dump(config, f)
            
            # Run Echidna
            cmd = [
                "echidna-test",
                contract_path,
                #changed
                "--contract", contract_name or Path(contract_path).stem,
                "--config", str(temp_config)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
             #changed
            print("STDOUT:\n", result.stdout),
            print("STDERR:\n", result.stderr),


            
            # Parse results
            return self._parse_results(result.stdout, result.stderr)
            
        except subprocess.TimeoutExpired:
            logger.error(f"Echidna timeout analyzing {contract_path}")
            return {
                'success': False,
                'error': 'Fuzzing timeout',
                'findings': []
            }
        except Exception as e:
            logger.error(f"Echidna error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'findings': []
            }
    
    def _prepare_config(self, contract_path: str, contract_name: str) -> Dict:
        """Prepare Echidna configuration"""
        return {
            'testLimit': 10000,
            'timeout': 300,
            'prefix': 'echidna_',
            'corpusDir': str(self.corpus_dir),
            'coverage': True,
            'format': 'text',
            'seqLen': 50,
            'testMode': 'assertion',
            'shrinkLimit': 5000,
            #'contractName': contract_name or Path(contract_path).stem
        }
    
    def _parse_results(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse Echidna output"""
        findings = []
        
        # Parse assertions failures
        if "echidna_" in stdout:
            lines = stdout.split('\n')
            for line in lines:
                if "failed!" in line:
                    finding = {
                        'type': 'assertion_failure',
                        'function': self._extract_function_name(line),
                        'severity': 'high',
                        'description': f"Property violation detected: {line}",
                        'sequence': self._extract_sequence(stdout, line)
                    }
                    findings.append(finding)
        
        # Check for coverage issues
        if "Coverage:" in stdout:
            coverage = self._parse_coverage(stdout)
            if coverage < 80:
                findings.append({
                    'type': 'low_coverage',
                    'severity': 'medium',
                    'description': f"Low code coverage: {coverage}%",
                    'recommendation': 'Add more test properties to increase coverage'
                })
        
        return {
            'success': True,
            'findings': findings,
            'summary': {
                'total_findings': len(findings),
                'assertion_failures': sum(1 for f in findings if f['type'] == 'assertion_failure'),
                'coverage_issues': sum(1 for f in findings if f['type'] == 'low_coverage')
            },
            'raw_output': stdout
        }
    
    def _extract_function_name(self, line: str) -> str:
        """Extract function name from Echidna output"""
        import re
        match = re.search(r'echidna_(\w+)', line)
        return match.group(1) if match else 'unknown'
    
    def _extract_sequence(self, output: str, failure_line: str) -> List[str]:
        """Extract call sequence that led to failure"""
        # This would parse the actual sequence from Echidna output
        # Simplified for demonstration
        return ["constructor()", "deposit(1000)", "withdraw(2000)"]
    
    def _parse_coverage(self, output: str) -> float:
        """Parse coverage percentage from output"""
        import re
        match = re.search(r'Coverage:\s+(\d+)%', output)
        return float(match.group(1)) if match else 0.0

# Module-level function
def analyze(contract_path: str, contract_name: str = None) -> Dict[str, Any]:
    runner = EchidnaRunner()
    return runner.analyze(contract_path, contract_name)
