import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(_file_).parent.parent))

from backend import contract_parser, slither_runner, mythril_runner
from backend import attack_simulator, report_generator

class TestSecurityTools:
    
    def test_contract_parser(self):
        """Test contract parsing functionality"""
        contract_path = Path(_file_).parent.parent / "contracts" / "VulnerableToken.sol"
        result = contract_parser.parse_contract(str(contract_path))
        
        assert 'contract_name' in result
        assert result['contract_name'] == 'VulnerableToken'
        assert len(result['functions']) > 0
        assert 'patterns' in result
        assert result['patterns']['uses_tx_origin'] == True
    
    def test_attack_simulator(self):
        """Test attack simulation"""
        result = attack_simulator.simulate_flashloan(
            "0x1234567890123456789012345678901234567890",
            10.0,
            "1. Borrow\n2. Attack\n3. Repay"
        )
        
        assert 'simulation_id' in result
        assert result['type'] == 'Flash Loan Attack'
        assert 'execution' in result
        assert len(result['execution']) == 3
    
    def test_report_generator(self):
        """Test report generation"""
        mock_results = {
            'slither': {
                'vulnerabilities': [
                    {
                        'title': 'Test Vulnerability',
                        'severity': 'high',
                        'description': 'Test description'
                    }
                ]
            }
        }
        
        report = report_generator.generate_report(
            mock_results,
            "Test_Report",
            "Markdown",
            ["Executive Summary"],
            ["High"]
        )
        
        assert 'content' in report
        assert 'Security Audit Report' in report['content']

if _name_ == "_main_":
    pytest.main([_file_, "-v"])