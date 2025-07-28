from typing import Dict, List, Any
import json
import re
from web3 import Web3


class DeFiAnalyzer:
    """Specialized analyzer for DeFi protocols"""

    def __init__(self):
        self.common_defi_vulnerabilities = {
            'flash_loan_attack': {
                'pattern': ['flashLoan', 'executeOperation', 'onFlashLoan'],
                'severity': 'critical',
                'description': 'Potential flash loan attack vector'
            },
            'price_manipulation': {
                'pattern': ['getPrice', 'oracle', 'priceFeed'],
                'severity': 'high',
                'description': 'Price oracle manipulation risk'
            },
            'reentrancy_in_withdraw': {
                'pattern': ['withdraw', '.call', 'balances['],
                'severity': 'critical',
                'description': 'Reentrancy in withdrawal function'
            }
        }

    def analyze_amm_contract(self, contract_path: str) -> Dict[str, Any]:
        """Analyze AMM/DEX specific vulnerabilities"""
        with open(contract_path, 'r') as f:
            content = f.read()

        findings = {
            'sandwich_protection': self._check_sandwich_protection(content),
            'slippage_protection': self._check_slippage_protection(content),
            'price_impact': self._analyze_price_impact(content),
            'fee_structure': self._analyze_fee_structure(content)
        }

        return findings

    def analyze_lending_protocol(self, contract_path: str) -> Dict[str, Any]:
        """Analyze lending protocol vulnerabilities"""
        with open(contract_path, 'r') as f:
            content = f.read()

        findings = {
            'collateral_safety': self._check_collateral_ratios(content),
            'liquidation_mechanism': self._analyze_liquidation(content),
            'interest_rate_model': self._check_interest_model(content),
            'oracle_dependencies': self._check_oracle_deps(content)
        }

        return findings

    def _check_sandwich_protection(self, content: str) -> Dict[str, Any]:
        """Check for sandwich attack protections"""
        protections = {
            'has_deadline': 'deadline' in content.lower(),
            'has_slippage_check': 'amountOutMin' in content or 'minAmountOut' in content,
            'has_commit_reveal': 'commit' in content and 'reveal' in content,
            'has_private_pool': 'privatePool' in content or 'whitelist' in content
        }

        score = sum(protections.values())
        return {
            'protections': protections,
            'score': score,
            'rating': 'Good' if score >= 3 else 'Fair' if score >= 2 else 'Poor'
        }

    def _check_slippage_protection(self, content: str) -> Dict[str, Any]:
        """Analyze slippage protection mechanisms"""
        slippage_params = re.findall(r'slippage|tolerance|minOutput|maxInput', content, re.I)
        has_validation = bool(re.search(r'require.amount.>=.*min', content, re.I))

        return {
            'has_slippage_params': len(slippage_params) > 0,
            'param_count': len(slippage_params),
            'has_validation': has_validation,
            'recommendation': None if has_validation else 'Add slippage validation'
        }

    def _analyze_price_impact(self, content: str) -> Dict[str, Any]:
        """Analyze price impact calculations"""
        has_impact_calc = bool(re.search(r'priceImpact|impactPrice|getAmountOut', content))
        has_warnings = bool(re.search(r'largeTrade|highImpact|maxTrade', content))

        return {
            'calculates_impact': has_impact_calc,
            'has_warnings': has_warnings,
            'recommendation': 'Implement price impact limits for large trades'
        }

    def _analyze_fee_structure(self, content: str) -> Dict[str, Any]:
        """Analyze fee structure and potential issues"""
        fee_vars = re.findall(r'fee\s*=\s*(\d+)', content, re.I)
        has_dynamic_fees = bool(re.search(r'updateFee|setFee|dynamicFee', content))
        has_fee_limits = bool(re.search(r'fee\s*<=?\s*MAX_FEE', content))

        return {
            'fee_values': fee_vars,
            'has_dynamic_fees': has_dynamic_fees,
            'has_fee_limits': has_fee_limits,
            'max_fee': max([int(f) for f in fee_vars]) if fee_vars else None
        }

    def _check_collateral_ratios(self, content: str) -> Dict[str, Any]:
        """Check collateral ratio configurations"""
        collateral_factor = re.search(r'collateralFactor\s*=\s*(\d+)', content)
        liquidation_threshold = re.search(r'liquidationThreshold\s*=\s*(\d+)', content)

        cf_value = int(collateral_factor.group(1)) if collateral_factor else None
        lt_value = int(liquidation_threshold.group(1)) if liquidation_threshold else None

        safety_margin = lt_value - cf_value if cf_value and lt_value else None

        return {
            'collateral_factor': cf_value,
            'liquidation_threshold': lt_value,
            'safety_margin': safety_margin,
            'is_safe': safety_margin > 500 if safety_margin else False,
            'recommendation': 'Increase safety margin' if safety_margin and safety_margin < 500 else None
        }

    def _analyze_liquidation(self, content: str) -> Dict[str, Any]:
        """Analyze liquidation mechanism"""
        checks = {
            'has_liquidation_function': 'liquidate' in content.lower(),
            'has_incentive': 'liquidationIncentive' in content or 'liquidationBonus' in content,
            'has_partial_liquidation': 'partialLiquidation' in content or 'maxLiquidation' in content,
            'has_price_check': 'checkPrice' in content or 'updatePrice' in content,
            'has_reentrancy_guard': 'nonReentrant' in content or 'ReentrancyGuard' in content
        }

        risk_score = 5 - sum(checks.values())

        return {
            'checks': checks,
            'risk_score': risk_score,
            'risk_level': 'High' if risk_score >= 3 else 'Medium' if risk_score >= 2 else 'Low'
        }

    def _check_interest_model(self, content: str) -> Dict[str, Any]:
        """Check interest rate model implementation"""
        has_interest_calc = bool(re.search(r'calculateInterest|interestRate|getRate', content))
        has_rate_caps = bool(re.search(r'MAX_RATE|rateLimit|maxInterest', content))
        has_utilization = bool(re.search(r'utilization|utilizationRate|getUtilization', content))

        return {
            'has_interest_calculation': has_interest_calc,
            'has_rate_caps': has_rate_caps,
            'has_utilization_model': has_utilization,
            'completeness': sum([has_interest_calc, has_rate_caps, has_utilization]) / 3
        }

    def _check_oracle_deps(self, content: str) -> Dict[str, Any]:
        """Check oracle dependencies and security"""
        oracle_refs = re.findall(r'oracle|priceFeed|getPrice', content, re.I)
        has_validation = bool(re.search(r'require.price\s>', content))
        has_staleness_check = bool(re.search(r'timestamp|lastUpdate|stale', content))
        oracle_count = len(set(re.findall(r'(\w+)[Oo]racle', content)))

        return {
            'oracle_references': len(oracle_refs),
            'has_price_validation': has_validation,
            'has_staleness_check': has_staleness_check,
            'oracle_count': oracle_count,
            'uses_multiple_oracles': oracle_count > 1,
            'risk': 'Low' if oracle_count > 1 and has_validation and has_staleness_check else 'High'
        }


# Module-level instance
defi_analyzer = DeFiAnalyzer()


def analyze_amm(contract_path: str) -> Dict[str, Any]:
    return defi_analyzer.analyze_amm_contract(contract_path)


def analyze_lending(contract_path: str) -> Dict[str, Any]:
    return defi_analyzer.analyze_lending_protocol(contract_path)
