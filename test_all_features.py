#!/usr/bin/env python3
"""
Comprehensive test script for DeFi Security Toolkit
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(_file_).parent))

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    try:
        from backend import contract_parser
        from backend import slither_runner
        from backend import mythril_runner
        from backend import monitor
        from backend import attack_simulator
        from backend import report_generator
        from backend import gas_analyzer
        from backend import formal_verifier
        from backend import vulnerability_db
        from backend import defi_analyzer
        from backend import blockchain_forensics
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_contract_parser():
    """Test contract parsing functionality"""
    print("\nTesting contract parser...")
    try:
        from backend import contract_parser
        
        # Test with sample contract
        contract_path = Path("contracts/VulnerableToken.sol")
        if contract_path.exists():
            result = contract_parser.parse_contract(str(contract_path))
            assert 'contract_name' in result
            assert 'functions' in result
            assert 'patterns' in result
            print(f"✅ Contract parser working - found {len(result['functions'])} functions")
            return True
        else:
            print("⚠ Sample contract not found")
            return False
    except Exception as e:
        print(f"❌ Contract parser error: {e}")
        return False

def test_attack_simulator():
    """Test attack simulation"""
    print("\nTesting attack simulator...")
    try:
        from backend import attack_simulator
        
        # Test flash loan simulation
        result = attack_simulator.simulate_flashloan(
            "0x1234567890123456789012345678901234567890",
            10.0,
            "1. Borrow\n2. Attack\n3. Repay"
        )
        assert 'simulation_id' in result
        assert 'execution' in result
        print("✅ Flash loan simulation working")
        
        # Test MEV simulation
        result = attack_simulator.simulate_mev_sandwich(
            "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            1.0,
            1.0
        )
        assert 'simulation_id' in result
        assert 'financial_summary' in result
        print("✅ MEV simulation working")
        
        return True
    except Exception as e:
        print(f"❌ Attack simulator error: {e}")
        return False

def test_gas_analyzer():
    """Test gas analysis"""
    print("\nTesting gas analyzer...")
    try:
        from backend import gas_analyzer
        
        contract_path = Path("contracts/VulnerableToken.sol")
        if contract_path.exists():
            result = gas_analyzer.analyze_gas_usage(str(contract_path))
            assert 'total_estimated_gas' in result
            assert 'optimization_opportunities' in result
            print(f"✅ Gas analyzer working - estimated {result['total_estimated_gas']} gas")
            return True
        else:
            print("⚠ Sample contract not found")
            return False
    except Exception as e:
        print(f"❌ Gas analyzer error: {e}")
        return False

def test_vulnerability_db():
    """Test vulnerability database"""
    print("\nTesting vulnerability database...")
    try:
        from backend import vulnerability_db
        
        # Get patterns
        patterns = vulnerability_db.get_patterns()
        assert len(patterns) > 0
        print(f"✅ Vulnerability DB working - {len(patterns)} patterns loaded")
        
        # Get statistics
        stats = vulnerability_db.get_stats()
        print(f"✅ Statistics available")
        
        return True
    except Exception as e:
        print(f"❌ Vulnerability DB error: {e}")
        return False

def test_defi_analyzer():
    """Test DeFi-specific analysis"""
    print("\nTesting DeFi analyzer...")
    try:
        from backend import defi_analyzer
        
        contract_path = Path("contracts/VulnerableToken.sol")
        if contract_path.exists():
            # Test AMM analysis
            amm_result = defi_analyzer.analyze_amm(str(contract_path))
            assert 'sandwich_protection' in amm_result
            print("✅ AMM analysis working")
            
            # Test lending analysis
            lending_result = defi_analyzer.analyze_lending(str(contract_path))
            assert 'collateral_safety' in lending_result
            print("✅ Lending analysis working")
            
            return True
        else:
            print("⚠ Sample contract not found")
            return False
    except Exception as e:
        print(f"❌ DeFi analyzer error: {e}")
        return False

def test_report_generator():
    """Test report generation"""
    print("\nTesting report generator...")
    try:
        from backend import report_generator
        
        # Mock analysis results
        mock_results = {
            'slither': {
                'vulnerabilities': [
                    {
                        'title': 'Test Vulnerability',
                        'severity': 'high',
                        'description': 'Test description',
                        'location': 'Line 10',
                        'recommendation': 'Fix it'
                    }
                ]
            }
        }
        
        # Generate markdown report
        report = report_generator.generate_report(
            mock_results,
            "Test_Report",
            "Markdown",
            ["Executive Summary", "Vulnerability Details"],
            ["High", "Medium", "Low"]
        )
        
        assert 'content' in report
        assert 'Security Audit Report' in report['content']
        print("✅ Report generator working")
        
        return True
    except Exception as e:
        print(f"❌ Report generator error: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("🧪 Running DeFi Security Toolkit Tests\n")
    
    tests = [
        ("Imports", test_imports),
        ("Contract Parser", test_contract_parser),
        ("Attack Simulator", test_attack_simulator),
        ("Gas Analyzer", test_gas_analyzer),
        ("Vulnerability DB", test_vulnerability_db),
        ("DeFi Analyzer", test_defi_analyzer),
        ("Report Generator", test_report_generator)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! The toolkit is ready to use.")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
    
    return passed == total

if _name_ == "_main_":
    success = run_all_tests()
    sys.exit(0 if success else 1)