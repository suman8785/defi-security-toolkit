import ast
import re
from typing import Dict, List, Tuple, Any
from pathlib import Path

class GasAnalyzer:
    """Analyze gas consumption patterns and optimization opportunities"""
    
    # Gas costs for common operations (in gas units)
    GAS_COSTS = {
        'SSTORE': 20000,  # Storage write (first time)
        'SLOAD': 2100,    # Storage read
        'CALL': 2600,     # External call
        'CREATE': 32000,  # Contract creation
        'LOG': 375,       # Event emission
        'MSTORE': 3,      # Memory write
        'MLOAD': 3,       # Memory read
        'ADD': 3,         # Addition
        'MUL': 5,         # Multiplication
        'DIV': 5,         # Division
    }
    
    def analyze_contract(self, contract_path: str) -> Dict[str, Any]:
        """Analyze contract for gas optimization opportunities"""
        with open(contract_path, 'r') as f:
            content = f.read()
        
        analysis = {
            'total_estimated_gas': 0,
            'optimization_opportunities': [],
            'gas_heavy_functions': [],
            'storage_patterns': self._analyze_storage_patterns(content),
            'loop_analysis': self._analyze_loops(content),
            'external_calls': self._analyze_external_calls(content)
        }
        
        # Analyze each function
        functions = self._extract_functions(content)
        for func_name, func_body in functions.items():
            gas_estimate = self._estimate_function_gas(func_body)
            analysis['gas_heavy_functions'].append({
                'name': func_name,
                'estimated_gas': gas_estimate,
                'optimizable': gas_estimate > 50000
            })
            analysis['total_estimated_gas'] += gas_estimate
        
        # Find optimization opportunities
        analysis['optimization_opportunities'] = self._find_optimizations(content)
        
        return analysis
    
    def _analyze_storage_patterns(self, content: str) -> Dict[str, Any]:
        """Analyze storage access patterns"""
        storage_reads = len(re.findall(r'\b\w+\s*\[.*?\]', content))
        storage_writes = len(re.findall(r'\b\w+\s*\[.*?\]\s*=', content))
        
        return {
            'total_reads': storage_reads,
            'total_writes': storage_writes,
            'estimated_gas': storage_reads * self.GAS_COSTS['SLOAD'] + 
                           storage_writes * self.GAS_COSTS['SSTORE'],
            'optimization': 'Consider caching frequently accessed storage variables' 
                          if storage_reads > 10 else None
        }
    
    def _analyze_loops(self, content: str) -> List[Dict[str, Any]]:
        """Analyze loops for gas optimization"""
        loops = []
        
        # Find for loops
        for_loops = re.findall(r'for\s*\(.*?\)\s*{([^}]*)}', content, re.DOTALL)
        for loop in for_loops:
            if 'storage' in loop or '.length' in loop:
                loops.append({
                    'type': 'for',
                    'issue': 'Storage access in loop',
                    'recommendation': 'Cache storage variables outside loop',
                    'potential_savings': 'Up to 2000 gas per iteration'
                })
        
        # Find while loops
        while_loops = re.findall(r'while\s*\(.*?\)\s*{([^}]*)}', content, re.DOTALL)
        for loop in while_loops:
            loops.append({
                'type': 'while',
                'issue': 'Unbounded loop detected',
                'recommendation': 'Add iteration limit to prevent out-of-gas',
                'severity': 'high'
            })
        
        return loops
    
    def _analyze_external_calls(self, content: str) -> List[Dict[str, Any]]:
        """Analyze external calls"""
        calls = []
        
        # Find .call() patterns
        call_patterns = re.findall(r'(\w+)\.call\{.?\}$.?$', content)
        for pattern in call_patterns:
            calls.append({
                'type': 'low_level_call',
                'target': pattern,
                'gas_cost': self.GAS_COSTS['CALL'],
                'risk': 'Reentrancy risk if not protected'
            })
        
        # Find transfer/send patterns
        transfer_patterns = re.findall(r'\.transfer\(|\.send\(', content)
        if transfer_patterns:
            calls.append({
                'type': 'value_transfer',
                'count': len(transfer_patterns),
                'recommendation': 'Consider using call() with proper checks'
            })
        
        return calls
    
    def _extract_functions(self, content: str) -> Dict[str, str]:
        """Extract function bodies"""
        functions = {}
        function_pattern = r'function\s+(\w+)\s*\(.*?\)\s*{([^}]*)}'
        matches = re.findall(function_pattern, content)
        
        for name, body in matches:
            functions[name] = body
        
        return functions
    
    def _estimate_function_gas(self, func_body: str) -> int:
        """Estimate gas consumption for a function"""
        gas = 21000  # Base transaction cost
        
        # Count operations
        gas += func_body.count('=') * 5  # Assignments
        gas += func_body.count('+') * self.GAS_COSTS['ADD']
        gas += func_body.count('*') * self.GAS_COSTS['MUL']
        gas += func_body.count('/') * self.GAS_COSTS['DIV']
        gas += func_body.count('emit') * self.GAS_COSTS['LOG']
        gas += len(re.findall(r'new\s+\w+', func_body)) * self.GAS_COSTS['CREATE']
        
        # Storage operations (rough estimate)
        gas += len(re.findall(r'\b\w+\s*\[.*?\]', func_body)) * self.GAS_COSTS['SLOAD']
        gas += len(re.findall(r'\b\w+\s*\[.*?\]\s*=', func_body)) * self.GAS_COSTS['SSTORE']

        
        return gas
    
    def _find_optimizations(self, content: str) -> List[Dict[str, str]]:
        """Find gas optimization opportunities"""
        optimizations = []
        
        # Check for storage in loops
        if re.search(r'for\s*\(.*?\)\s*{[^}]*\w+\s*\[.*?\]', content):
            optimizations.append({
                'type': 'storage_in_loop',
                'description': 'Storage access detected in loop',
                'recommendation': 'Cache storage variables in memory before loop',
                'potential_savings': 'High'
            })
        
        # Check for redundant storage reads
        storage_vars = re.findall(r'\b\w+\s*\[.*?\]', content)
        if len(storage_vars) != len(set(storage_vars)):
            optimizations.append({
                'type': 'redundant_storage_reads',
                'description': 'Same storage location read multiple times',
                'recommendation': 'Cache frequently accessed storage in memory',
                'potential_savings': 'Medium'
            })
        
        # Check for small data in storage
        if re.search(r'bool\s+public\s+\w+;', content):
            optimizations.append({
                'type': 'inefficient_storage_packing',
                'description': 'Small data types not packed efficiently',
                'recommendation': 'Pack multiple bool/small values in single storage slot',
                'potential_savings': 'Medium'
            })
        
        return optimizations

# Module-level function
def analyze_gas_usage(contract_path: str) -> Dict[str, Any]:
    analyzer = GasAnalyzer()
    return analyzer.analyze_contract(contract_path)