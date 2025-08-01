import json
from datetime import datetime
from typing import Dict, Any, List
from web3 import Web3
import random

class AttackSimulator:
    def __init__(self):
        self.simulations = []
    
    def simulate_flashloan(self, target_address: str, loan_amount: float, attack_steps: str) -> Dict[str, Any]:
        """Simulate a flash loan attack"""
        simulation_id = f"FL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Parse attacking steps
        if isinstance(attack_steps, str):
            try:
                
                import json
                steps = json.loads(attack_steps)
            except:
               
                steps = [s.strip() for s in attack_steps.split('\n') if s.strip()]
        else:
            steps = attack_steps if isinstance(attack_steps, list) else []
        
        # Simulate execution
        execution_results = []
        total_profit = 0
        
        for i, step in enumerate(steps):
            # Simulate step execution
            gas_used = random.randint(50000, 200000)
            success = random.choice([True, True, True, False])  # 75% success rate
            
            result = {
                'step': i + 1,
                'action': step,
                'status': 'Success' if success else 'Failed',
                'gas_used': gas_used  # Make sure this is always present
            }
            
            # Add specific details based on step content
            step_lower = step.lower()
            
            if 'borrow' in step_lower:
                result['details'] = f"Borrowed {loan_amount} ETH from lending pool"
            elif 'manipulate' in step_lower or 'oracle' in step_lower:
                manipulation_impact = random.uniform(0.05, 0.20)  # 5-20% price impact
                result['details'] = f"Price manipulated by {manipulation_impact*100:.2f}%"
            elif 'buy' in step_lower or 'sell' in step_lower or 'arbitrage' in step_lower:
                profit = loan_amount * random.uniform(0.01, 0.05) if success else 0
                total_profit += profit
                result['details'] = f"Profit: {profit:.4f} ETH"
            elif 'repay' in step_lower:
                result['details'] = f"Repaid {loan_amount} ETH + fees"
            else:
                result['details'] = 'Step executed'
            
            execution_results.append(result)
        
        # Calculate totals 
        total_gas = sum(r['gas_used'] for r in execution_results)
        gas_cost_eth = total_gas * 0.00000003  
        net_profit = total_profit - gas_cost_eth
        
        simulation = {
            'simulation_id': simulation_id,
            'type': 'Flash Loan Attack',
            'target': target_address,
            'timestamp': datetime.now().isoformat(),
            'parameters': {
                'loan_amount': loan_amount,
                'steps': len(steps)
            },
            'execution': execution_results,
            'summary': {
                'total_steps': len(steps),
                'successful_steps': sum(1 for r in execution_results if r['status'] == 'Success'),
                'total_gas_used': total_gas,
                'gas_cost_eth': gas_cost_eth,
                'gross_profit': total_profit,
                'net_profit': net_profit,
                'attack_successful': net_profit > 0
            },
            'risk_assessment': self._assess_flashloan_risk(net_profit, total_gas)
        }
        
        self.simulations.append(simulation)
        return simulation
    
    def simulate_mev_sandwich(self, victim_tx: str, frontrun_amount: float, backrun_amount: float) -> Dict[str, Any]:
        """Simulate MEV sandwich attack"""
        simulation_id = f"MEV_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Simulate victim transaction analysis
        victim_data = {
            'hash': victim_tx,
            'token_in': 'ETH',
            'token_out': 'USDC',
            'amount': random.uniform(1, 10),
            'slippage': random.uniform(0.005, 0.03)  # 0.5% - 3%
        }
        
        # Calculate price impact
        price_impact = random.uniform(0.001, 0.005)  # 0.1% - 0.5%
        
        # Simulate frontrun transaction
        frontrun_result = {
            'type': 'Frontrun',
            'amount': frontrun_amount,
            'gas_price': random.randint(50, 200),  # gwei
            'gas_used': random.randint(150000, 300000),
            'price_before': 1000,  # USDC per ETH
            'price_after': 1000 * (1 + price_impact),
            'tokens_received': frontrun_amount * 1000
        }
        
        # Simulate backrun transaction
        backrun_result = {
            'type': 'Backrun',
            'amount': backrun_amount,
            'gas_price': random.randint(40, 150),  # gwei
            'gas_used': random.randint(150000, 300000),
            'price_before': frontrun_result['price_after'] * (1 + victim_data['slippage']),
            'price_after': frontrun_result['price_before'],
            'eth_received': backrun_amount / (frontrun_result['price_after'] * (1 + victim_data['slippage']))
        }
        
        # Calculate profit
        total_gas_cost = (
            (frontrun_result['gas_used'] * frontrun_result['gas_price'] +
             backrun_result['gas_used'] * backrun_result['gas_price']) * 1e-9
        )
        
        sandwich_profit = (
            backrun_result['eth_received'] - frontrun_amount - total_gas_cost
        )
        
        simulation = {
            'simulation_id': simulation_id,
            'type': 'MEV Sandwich Attack',
            'timestamp': datetime.now().isoformat(),
            'victim_transaction': victim_data,
            'attack_transactions': {
                'frontrun': frontrun_result,
                'backrun': backrun_result
            },
            'financial_summary': {
                'total_eth_used': frontrun_amount,
                'total_gas_cost_eth': total_gas_cost,
                'gross_profit_eth': backrun_result['eth_received'] - frontrun_amount,
                'net_profit_eth': sandwich_profit,
                'profit_percentage': (sandwich_profit / frontrun_amount) * 100 if frontrun_amount > 0 else 0
            },
            'risk_assessment': self._assess_mev_risk(sandwich_profit, victim_data['slippage'])
        }
        
        self.simulations.append(simulation)
        return simulation
    
    def _assess_flashloan_risk(self, profit: float, gas_used: int) -> Dict[str, Any]:
        """Assess risk of flash loan attack"""
        risk_score = 0
        
        # Profit-based risk
        if profit < 0:
            risk_score += 40
        elif profit < 0.1:
            risk_score += 20
        
        # Gas-based risk
        if gas_used > 1000000:
            risk_score += 30
        elif gas_used > 500000:
            risk_score += 15
        
        # Random factors
        risk_score += random.randint(0, 20)
        
        return {
            'risk_score': min(risk_score, 100),
            'risk_level': 'High' if risk_score > 70 else 'Medium' if risk_score > 40 else 'Low',
            'factors': {
                'profitability': 'Poor' if profit < 0 else 'Good',
                'gas_efficiency': 'Poor' if gas_used > 1000000 else 'Good',
                'execution_complexity': 'High'
            }
        }
    
    def _assess_mev_risk(self, profit: float, slippage: float) -> Dict[str, Any]:
        """Assess risk of MEV attack"""
        risk_score = 0
        
        # Profit-based risk
        if profit < 0:
            risk_score += 35
        elif profit < 0.05:
            risk_score += 20
        
        # Slippage-based risk
        if slippage < 0.01:
            risk_score += 25  # Low slippage = harder to exploit
        
        # Competition risk
        risk_score += random.randint(10, 30)  # MEV competition
        
        return {
            'risk_score': min(risk_score, 100),
            'risk_level': 'High' if risk_score > 70 else 'Medium' if risk_score > 40 else 'Low',
            'factors': {
                'profitability': 'Poor' if profit < 0 else 'Good',
                'victim_protection': 'Strong' if slippage < 0.01 else 'Weak',
                'mev_competition': 'High',
                'detection_risk': 'Medium'
            }
        }


    def simulate_reentrancy(self, target_address: str, attack_depth: int) -> Dict[str, Any]:
        """Simulate a reentrancy attack"""
        simulation_id = f"RE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
        calls = []
        for i in range(attack_depth):
            gas_used = random.randint(30000, 90000)
            success = random.choice([True, True, False])
            calls.append({
                "call_number": i + 1,
                "gas_used": gas_used,
                "status": "Success" if success else "Failed",
                "description": f"Recursive call {i+1} to vulnerable function"
            })

        total_gas = sum(call["gas_used"] for call in calls)
        net_effect = "Contract drained" if all(c["status"] == "Success" for c in calls) else "Partial failure"

        simulation = {
            "simulation_id": simulation_id,
            "type": "Reentrancy Attack",
            "target": target_address,
            "timestamp": datetime.now().isoformat(),
            "parameters": {
                "attack_depth": attack_depth
            },
            "calls": calls,
            "summary": {
                "total_calls": len(calls),
                "successful_calls": sum(1 for c in calls if c["status"] == "Success"),
                "total_gas_used": total_gas,
                "net_effect": net_effect
            },
            "risk_assessment": {
                "risk_score": min(100, attack_depth * 10),
                "risk_level": "High" if attack_depth > 5 else "Medium" if attack_depth > 2 else "Low"
            }
        }

        self.simulations.append(simulation)
        return simulation
    



# Module-level functions
simulator = AttackSimulator()
def run_reentrancy_simulation(target_address: str, attack_depth: int) -> Dict[str, Any]:
    return simulator.simulate_reentrancy(target_address, attack_depth)
def simulate_flashloan(target_address: str, loan_amount: float, attack_steps: str) -> Dict[str, Any]:
    return simulator.simulate_flashloan(target_address, loan_amount, attack_steps)

def simulate_mev_sandwich(victim_tx: str, frontrun_amount: float, backrun_amount: float) -> Dict[str, Any]:
    return simulator.simulate_mev_sandwich(victim_tx, frontrun_amount, backrun_amount)
