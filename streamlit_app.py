# backend/attack_simulator.py
import random
import time
from datetime import datetime
from typing import Dict, List, Any
import json

class AttackSimulator:
    def __init__(self):
        self.simulation_count = 0
    
    def simulate_flashloan(self, target_address: str, loan_amount: float, attack_steps: str) -> Dict[str, Any]:
        """Simulate a flash loan attack"""
        self.simulation_count += 1
        
        steps = attack_steps.split('\n')
        execution_results = []
        total_gas = 0
        
        for i, step in enumerate(steps, 1):
            gas_used = random.randint(50000, 200000)
            total_gas += gas_used
            
            # Simulate step execution
            success_rate = random.random()
            status = "Success" if success_rate > 0.2 else "Failed"
            
            step_result = {
                "step": i,
                "action": step.strip(),
                "status": status,
                "gas_used": gas_used,
                "details": self._generate_step_details(step.strip(), loan_amount, status)
            }
            execution_results.append(step_result)
        
        # Calculate profits
        gas_cost_eth = total_gas * 30e-9  # 30 gwei gas price
        gross_profit = loan_amount * random.uniform(0.03, 0.08)  # 3-8% profit
        net_profit = gross_profit - gas_cost_eth
        
        successful_steps = sum(1 for step in execution_results if step["status"] == "Success")
        attack_successful = successful_steps >= len(steps) * 0.75  # 75% success rate
        
        return {
            "simulation_id": f"FL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "Flash Loan Attack",
            "target": target_address,
            "timestamp": datetime.now().isoformat(),
            "parameters": {
                "loan_amount": loan_amount,
                "steps": len(steps)
            },
            "execution": execution_results,
            "summary": {
                "total_steps": len(steps),
                "successful_steps": successful_steps,
                "total_gas_used": total_gas,
                "gas_cost_eth": gas_cost_eth,
                "gross_profit": gross_profit,
                "net_profit": net_profit,
                "attack_successful": attack_successful
            },
            "risk_assessment": {
                "risk_score": random.randint(1, 5),
                "risk_level": random.choice(["Low", "Medium", "High"]),
                "factors": {
                    "profitability": "Good" if net_profit > 0 else "Poor",
                    "gas_efficiency": "Good" if gas_cost_eth < gross_profit * 0.1 else "Poor",
                    "execution_complexity": random.choice(["Low", "Medium", "High"])
                }
            }
        }
    
    def simulate_mev_sandwich(self, victim_tx: str, frontrun_amount: float, backrun_amount: float) -> Dict[str, Any]:
        """Simulate MEV sandwich attack"""
        self.simulation_count += 1
        
        # Simulate sandwich attack execution
        frontrun_gas = random.randint(21000, 100000)
        backrun_gas = random.randint(21000, 100000)
        total_gas = frontrun_gas + backrun_gas
        
        # Calculate profits
        frontrun_profit = frontrun_amount * random.uniform(0.02, 0.06)
        backrun_profit = backrun_amount * random.uniform(0.015, 0.04)
        total_profit = frontrun_profit + backrun_profit
        
        gas_cost = total_gas * 30e-9
        net_profit = total_profit - gas_cost
        
        return {
            "simulation_id": f"MEV_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "MEV Sandwich Attack",
            "victim_tx": victim_tx,
            "timestamp": datetime.now().isoformat(),
            "execution": {
                "frontrun": {
                    "amount": frontrun_amount,
                    "gas_used": frontrun_gas,
                    "profit": frontrun_profit,
                    "status": "Success"
                },
                "victim_impact": {
                    "slippage_increased": f"{random.uniform(0.5, 3.0):.2f}%",
                    "extra_cost": random.uniform(0.01, 0.1)
                },
                "backrun": {
                    "amount": backrun_amount,
                    "gas_used": backrun_gas,
                    "profit": backrun_profit,
                    "status": "Success"
                }
            },
            "summary": {
                "total_profit": total_profit,
                "gas_cost": gas_cost,
                "net_profit": net_profit,
                "attack_successful": net_profit > 0,
                "victim_loss": random.uniform(0.01, 0.1)
            }
        }
    
    def simulate_reentrancy(self, contract_address: str, attack_depth: int) -> Dict[str, Any]:
        """Simulate reentrancy attack"""
        self.simulation_count += 1
        
        # Simulate recursive calls
        calls = []
        funds_drained = 0
        total_gas = 0
        
        for i in range(attack_depth):
            call_gas = random.randint(80000, 200000)
            total_gas += call_gas
            
            # Each call drains some funds
            drained_amount = random.uniform(0.5, 2.0)
            funds_drained += drained_amount
            
            calls.append({
                "call_depth": i + 1,
                "gas_used": call_gas,
                "funds_drained": drained_amount,
                "status": "Success" if random.random() > 0.1 else "Reverted"
            })
        
        gas_cost = total_gas * 30e-9
        net_profit = funds_drained - gas_cost
        
        return {
            "simulation_id": f"RE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "Reentrancy Attack",
            "contract": contract_address,
            "timestamp": datetime.now().isoformat(),
            "parameters": {
                "attack_depth": attack_depth,
                "target_function": "withdraw()"
            },
            "execution": {
                "recursive_calls": calls,
                "total_calls": len(calls),
                "successful_calls": sum(1 for call in calls if call["status"] == "Success")
            },
            "summary": {
                "funds_drained": funds_drained,
                "gas_cost": gas_cost,
                "net_profit": net_profit,
                "attack_successful": net_profit > 0,
                "contract_vulnerable": True
            }
        }
    
    def simulate_front_running(self, victim_tx: str, gas_price_boost: int) -> Dict[str, Any]:
        """Simulate front-running attack"""
        self.simulation_count += 1
        
        # Simulate front-running execution
        base_gas_price = 30  # 30 gwei
        boosted_gas_price = base_gas_price * (1 + gas_price_boost / 100)
        gas_used = random.randint(21000, 150000)
        
        # Calculate if front-run was successful
        success_probability = min(0.95, gas_price_boost / 100 + 0.3)  # Higher gas boost = higher success
        front_run_successful = random.random() < success_probability
        
        if front_run_successful:
            profit = random.uniform(0.05, 0.5)  # ETH profit
        else:
            profit = 0
        
        gas_cost = gas_used * boosted_gas_price * 1e-9
        net_profit = profit - gas_cost
        
        return {
            "simulation_id": f"FR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "Front-Running Attack",
            "victim_tx": victim_tx,
            "timestamp": datetime.now().isoformat(),
            "parameters": {
                "gas_price_boost": gas_price_boost,
                "base_gas_price": base_gas_price,
                "boosted_gas_price": boosted_gas_price
            },
            "execution": {
                "front_run_tx": {
                    "gas_price": boosted_gas_price,
                    "gas_used": gas_used,
                    "status": "Success" if front_run_successful else "Failed",
                    "block_position": 1 if front_run_successful else random.randint(2, 10)
                },
                "victim_tx": {
                    "original_gas_price": base_gas_price,
                    "block_position": 2 if front_run_successful else 1,
                    "impact": "Negatively affected" if front_run_successful else "Unaffected"
                }
            },
            "summary": {
                "attack_successful": front_run_successful,
                "profit_extracted": profit,
                "gas_cost": gas_cost,
                "net_profit": net_profit,
                "victim_loss": profit if front_run_successful else 0
            }
        }
    
    def _generate_step_details(self, step: str, loan_amount: float, status: str) -> str:
        """Generate realistic details for attack steps"""
        if "borrow" in step.lower():
            return f"Borrowed {loan_amount} ETH from lending pool"
        elif "manipulate" in step.lower():
            percentage = random.uniform(1, 10)
            return f"Price manipulated by {percentage:.2f}%"
        elif "arbitrage" in step.lower() or "exploit" in step.lower():
            profit = loan_amount * random.uniform(0.02, 0.08)
            return f"Profit: {profit:.4f} ETH"
        elif "repay" in step.lower():
            return f"Repaid {loan_amount} ETH + fees"
        else:
            return f"Step executed with {status.lower()} status"

# Create singleton instance
simulator = AttackSimulator()
