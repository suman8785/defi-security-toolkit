import re
import json
from pathlib import Path
from typing import Dict, List, Any

class ContractParser:
    def _init_(self):
        self.contract_data = {}
    
    def parse_contract(self, file_path: str) -> Dict[str, Any]:
        """Parse Solidity contract and extract key information"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Extract contract name
        contract_name_match = re.search(r'contract\s+(\w+)', content)
        contract_name = contract_name_match.group(1) if contract_name_match else "Unknown"
        
        # Extract functions
        functions = self._extract_functions(content)
        
        # Extract state variables
        state_variables = self._extract_state_variables(content)
        
        # Extract modifiers
        modifiers = self._extract_modifiers(content)
        
        # Extract events
        events = self._extract_events(content)
        
        # Check for common patterns
        patterns = self._check_patterns(content)
        
        return {
            'contract_name': contract_name,
            'functions': functions,
            'state_variables': state_variables,
            'modifiers': modifiers,
            'events': events,
            'patterns': patterns,
            'line_count': len(content.splitlines()),
            'complexity_score': self._calculate_complexity(content)
        }
    
    def _extract_functions(self, content: str) -> List[Dict[str, str]]:
        """Extract function signatures and visibility"""
        function_pattern = r'function\s+(\w+)\s*$[^)]$\s(public|private|internal|external)?'
        matches = re.findall(function_pattern, content)
        
        functions = []
        for name, visibility in matches:
            functions.append({
                'name': name,
                'visibility': visibility or 'public',
                'has_modifier': bool(re.search(f'function\s+{name}.?\s+\w+\s\(', content))
            })
        
        return functions
    
    def _extract_state_variables(self, content: str) -> List[Dict[str, str]]:
        """Extract state variables"""
        # Common types in Solidity
        types = ['uint', 'int', 'address', 'bool', 'string', 'bytes', 'mapping']
        variables = []
        
        for var_type in types:
            pattern = rf'{var_type}[\d]\s+(public|private|internal)?\s(\w+)'
            matches = re.findall(pattern, content)
            for visibility, name in matches:
                variables.append({
                    'name': name,
                    'type': var_type,
                    'visibility': visibility or 'internal'
                })
        
        return variables
    
    def _extract_modifiers(self, content: str) -> List[str]:
        """Extract modifier names"""
        modifier_pattern = r'modifier\s+(\w+)'
        return re.findall(modifier_pattern, content)
    
    def _extract_events(self, content: str) -> List[str]:
        """Extract event names"""
        event_pattern = r'event\s+(\w+)'
        return re.findall(event_pattern, content)
    
    def _check_patterns(self, content: str) -> Dict[str, bool]:
        """Check for common patterns and potential issues"""
        return {
            'uses_delegatecall': 'delegatecall' in content,
            'uses_selfdestruct': 'selfdestruct' in content,
            'uses_assembly': 'assembly' in content,
            'uses_tx_origin': 'tx.origin' in content,
            'has_payable': 'payable' in content,
            'has_receive': 'receive()' in content,
            'has_fallback': 'fallback()' in content,
            'uses_reentrancy_guard': 'ReentrancyGuard' in content or 'nonReentrant' in content
        }
    
    def _calculate_complexity(self, content: str) -> int:
        """Calculate a simple complexity score"""
        score = 0
        score += len(re.findall(r'function', content)) * 10
        score += len(re.findall(r'modifier', content)) * 5
        score += len(re.findall(r'require', content)) * 2
        score += len(re.findall(r'if\s*\(', content)) * 3
        score += len(re.findall(r'for\s*\(', content)) * 5
        score += len(re.findall(r'while\s*\(', content)) * 5
        return score

# Module-level function for easy import
def parse_contract(file_path: str) -> Dict[str, Any]:
    parser = ContractParser()
    return parser.parse_contract(file_path)