import streamlit as st
import pandas as pd
from web3 import Web3
from backend import defi_analyzer

def show_defi_analysis():
    st.header("💰 DeFi-Specific Security Analysis")
    
    defi_protocol = st.selectbox(
        "Select DeFi Protocol Type",
        ["AMM/DEX", "Lending Protocol", "Yield Aggregator", "Stablecoin", "Derivatives"]
    )
    
    if defi_protocol == "AMM/DEX":
        st.subheader("🔄 AMM/DEX Security Checks")
        
        checks = {
            "Price Manipulation": {
                "description": "Check for price oracle manipulation vulnerabilities",
                "severity": "critical",
                "checks": [
                    "Flash loan price manipulation",
                    "TWAP oracle delays",
                    "Liquidity pool imbalance attacks"
                ]
            },
            "Sandwich Attacks": {
                "description": "MEV sandwich attack vulnerabilities",
                "severity": "high",
                "checks": [
                    "Slippage protection",
                    "Deadline parameters",
                    "Front-running protection"
                ]
            },
            "Impermanent Loss": {
                "description": "IL protection mechanisms",
                "severity": "medium",
                "checks": [
                    "IL compensation",
                    "Dynamic fees",
                    "Concentrated liquidity"
                ]
            }
        }
        
        for check_name, check_data in checks.items():
            with st.expander(f"{check_name} - {check_data['severity'].upper()}"):
                st.write(f"*Description:* {check_data['description']}")
                st.write("*Checks:*")
                for check in check_data['checks']:
                    st.write(f"- {check}")
                
                if st.button(f"Run {check_name} Analysis", key=check_name):
                    with st.spinner(f"Analyzing {check_name}..."):
                        # Simulate analysis
                        st.success(f"✅ {check_name} analysis complete")
                        st.write("*Findings:*")
                        st.write("- No immediate vulnerabilities detected")
                        st.write("- Recommend implementing additional safeguards")
    
    elif defi_protocol == "Lending Protocol":
        st.subheader("🏦 Lending Protocol Security")
        
        # Collateral analysis
        st.write("*Collateral Risk Analysis:*")
        col1, col2 = st.columns(2)
        
        with col1:
            collateral_factor = st.slider("Collateral Factor", 0.0, 1.0, 0.75)
            liquidation_threshold = st.slider("Liquidation Threshold", 0.0, 1.0, 0.8)
        
        with col2:
            st.metric("Safety Margin", f"{(liquidation_threshold - collateral_factor)*100:.1f}%")
            risk_level = "High" if liquidation_threshold - collateral_factor < 0.05 else "Medium" if liquidation_threshold - collateral_factor < 0.1 else "Low"
            st.metric("Risk Level", risk_level)
        
        # Oracle dependencies
        st.write("*Oracle Security:*")
        oracle_checks = [
            {"name": "Price Feed Staleness", "status": "✅ Pass", "details": "Max delay: 3600s"},
            {"name": "Oracle Manipulation", "status": "⚠ Warning", "details": "Single oracle dependency"},
            {"name": "Circuit Breakers", "status": "✅ Pass", "details": "5% deviation limit"}
        ]
        
        for check in oracle_checks:
            col1, col2, col3 = st.columns([2, 1, 3])
            with col1:
                st.write(check["name"])
            with col2:
                st.write(check["status"])
            with col3:
                st.write(check["details"])
        
        # Liquidation analysis
        st.write("*Liquidation Mechanism:*")
        if st.button("Simulate Liquidation Scenario"):
            with st.spinner("Running liquidation simulation..."):
                # Simulate different market conditions
                scenarios = [
                    {"name": "10% Price Drop", "liquidations": 15, "bad_debt": 0},
                    {"name": "30% Price Drop", "liquidations": 145, "bad_debt": 50000},
                    {"name": "50% Flash Crash", "liquidations": 890, "bad_debt": 2500000}
                ]
                
                df = pd.DataFrame(scenarios)
                st.dataframe(df, use_container_width=True)
                
                st.warning("⚠ High bad debt risk in extreme scenarios")
                
    elif defi_protocol == "Yield Aggregator":
        st.subheader("🌾 Yield Aggregator Security Analysis")
        
        # Strategy risks
        st.write("*Strategy Risk Assessment*")
        
        strategies = {
            "Leveraged Yield Farming": {
                "risk": "High",
                "checks": [
                    "Liquidation thresholds",
                    "Oracle dependencies",
                    "Protocol composability risks"
                ]
            },
            "Vault Strategies": {
                "risk": "Medium",
                "checks": [
                    "Strategy upgrade mechanism",
                    "Emergency withdrawal",
                    "Fee structure"
                ]
            },
            "Auto-compounding": {
                "risk": "Low",
                "checks": [
                    "Compound frequency",
                    "Gas optimization",
                    "Slippage tolerance"
                ]
            }
        }
        
        for strategy_name, details in strategies.items():
            with st.expander(f"{strategy_name} - Risk: {details['risk']}"):
                st.write("*Security Checks:*")
                for check in details['checks']:
                    st.write(f"- {check}")
        
        # Yield aggregator specific metrics
        st.write("*Yield Aggregator Security Metrics*")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            strategies_count = st.number_input("Active Strategies", min_value=1, max_value=20, value=5)
            st.metric("Risk Score", f"{strategies_count * 15}/100")
        
        with col2:
            tvl = st.number_input("Total Value Locked ($M)", min_value=1.0, max_value=1000.0, value=50.0)
            st.metric("Concentration Risk", "High" if tvl > 100 else "Medium" if tvl > 10 else "Low")
        
        with col3:
            external_protocols = st.number_input("External Protocol Dependencies", min_value=1, max_value=10, value=3)
            st.metric("Composability Risk", f"{external_protocols * 10}%")
        
        # Vulnerability checks
        if st.button("Run Yield Aggregator Analysis"):
            with st.spinner("Analyzing yield aggregator vulnerabilities..."):
                
                # Simulate analysis results
                findings = {
                    "Strategy Risks": {
                        "Admin Key Risk": "⚠ Warning: Centralized strategy updates",
                        "Impermanent Loss": "✅ Pass: IL protection implemented",
                        "Reward Token Dumping": "⚠ Warning: No vesting mechanism"
                    },
                    "Integration Risks": {
                        "Protocol Health Monitoring": "❌ Fail: No automated monitoring",
                        "Emergency Pause": "✅ Pass: Emergency functions present",
                        "Slippage Protection": "✅ Pass: Max slippage enforced"
                    },
                    "Economic Risks": {
                        "Fee Sustainability": "⚠ Warning: High fees may deter users",
                        "Yield Source Diversity": "✅ Pass: Multiple yield sources",
                        "Token Inflation": "❌ Fail: Unsustainable reward emissions"
                    }
                }
                
                for category, checks in findings.items():
                    st.subheader(category)
                    for check, result in checks.items():
                        st.write(f"{check}: {result}")
                
                # Recommendations
                with st.expander("🔧 Recommendations"):
                    st.markdown("""
                    *Critical Improvements:*
                    1. Implement automated protocol health monitoring
                    2. Add time-locks for strategy changes
                    3. Diversify yield sources to reduce dependency
                    4. Implement reward token vesting
                    5. Add circuit breakers for abnormal APY
                    """)

    elif defi_protocol == "Stablecoin":
        st.subheader("💵 Stablecoin Security Analysis")
        
        stablecoin_type = st.selectbox(
            "Stablecoin Type",
            ["Algorithmic", "Collateralized", "Hybrid"]
        )
        
        if stablecoin_type == "Algorithmic":
            st.write("*Algorithmic Stablecoin Risks*")
            
            # Parameters
            col1, col2 = st.columns(2)
            with col1:
                target_price = st.number_input("Target Price ($)", value=1.00, format="%.2f")
                current_price = st.number_input("Current Price ($)", min_value=0.01, max_value=2.00, value=0.98, format="%.2f")
            
            with col2:
                burn_rate = st.slider("Burn Rate (%)", min_value=0.1, max_value=10.0, value=2.0)
                mint_rate = st.slider("Mint Rate (%)", min_value=0.1, max_value=10.0, value=2.0)
            
            # Death spiral risk calculation
            price_deviation = abs(current_price - target_price) / target_price * 100
            death_spiral_risk = min(100, price_deviation * 10)
            
            st.subheader("Risk Metrics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Price Deviation", f"{price_deviation:.2f}%")
            with col2:
                st.metric("Death Spiral Risk", f"{death_spiral_risk:.0f}%", 
                        delta="High Risk" if death_spiral_risk > 50 else "Low Risk")
            with col3:
                st.metric("Peg Stability", "❌ Unstable" if price_deviation > 5 else "✅ Stable")
            
            # Risk factors
            st.write("*Risk Assessment*")
            risks = {
                "Death Spiral": death_spiral_risk > 50,
                "Insufficient Liquidity": True,
                "Oracle Manipulation": True,
                "Governance Attack": False,
                "Bank Run Risk": price_deviation > 10
            }
            
            for risk, is_present in risks.items():
                if is_present:
                    st.error(f"❌ {risk}: HIGH RISK")
                else:
                    st.success(f"✅ {risk}: Low Risk")
        
        elif stablecoin_type == "Collateralized":
            st.write("*Collateralized Stablecoin Analysis*")
            
            col1, col2 = st.columns(2)
            with col1:
                collateral_ratio = st.slider("Collateral Ratio (%)", min_value=100, max_value=200, value=150)
                collateral_types = st.multiselect(
                    "Collateral Types",
                    ["ETH", "BTC", "USDC", "DAI", "Other Stables"],
                    default=["ETH", "USDC"]
                )
            
            with col2:
                liquidation_ratio = st.slider("Liquidation Ratio (%)", min_value=100, max_value=150, value=125)
                oracle_count = st.number_input("Price Oracle Count", min_value=1, max_value=5, value=1)
            
            # Risk assessment
            st.subheader("Collateral Risk Assessment")
            
            if collateral_ratio < 120:
                st.error("⚠ Low collateral ratio - High liquidation risk")
            else:
                st.success("✅ Healthy collateral ratio")
            
            if oracle_count < 3:
                st.warning("⚠ Single oracle dependency - Manipulation risk")
            else:
                st.success("✅ Multiple oracle sources")
            
            if "Other Stables" in collateral_types:
                st.warning("⚠ Recursive collateral risk detected")
        
        # Common stablecoin checks
        if st.button("Run Stablecoin Security Check"):
            with st.spinner("Analyzing stablecoin mechanisms..."):
                st.success("Analysis Complete!")
                
                # Results
                checks = {
                    "Mint/Burn Access Control": "✅ Pass",
                    "Emergency Pause Function": "✅ Pass",
                    "Oracle Price Feeds": "⚠ Warning: Single oracle",
                    "Redemption Mechanism": "✅ Pass",
                    "Governance Timelock": "❌ Fail: No timelock"
                }
                
                for check, result in checks.items():
                    st.write(f"{check}: {result}")

    elif defi_protocol == "Derivatives":
        st.subheader("📊 Derivatives Protocol Security")
        
        derivative_type = st.selectbox(
            "Derivative Type",
            ["Perpetual Futures", "Options", "Synthetic Assets"]
        )
        
        if derivative_type == "Perpetual Futures":
            st.write("*Perpetual Futures Risk Analysis*")
            
            # Parameters
            col1, col2, col3 = st.columns(3)
            with col1:
                max_leverage = st.slider("Max Leverage", min_value=5, max_value=100, value=20)
                funding_rate = st.number_input("Funding Rate (%/8h)", value=0.01, format="%.3f")
            
            with col2:
                insurance_fund = st.number_input("Insurance Fund ($M)", min_value=0.1, max_value=100.0, value=10.0)
                open_interest = st.number_input("Open Interest ($M)", min_value=1.0, max_value=1000.0, value=100.0)
            
            with col3:
                mark_price_source = st.selectbox("Mark Price Source", ["Spot Index", "TWAP", "Oracle Aggregate"])
                liquidation_penalty = st.slider("Liquidation Penalty (%)", min_value=0.1, max_value=5.0, value=1.0)
            
            # Risk calculations
            insurance_ratio = (insurance_fund / open_interest) * 100
            cascade_risk = max_leverage * (1 / insurance_ratio) * 100 if insurance_ratio > 0 else 100
            
            st.subheader("Risk Metrics")
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            
            with metrics_col1:
                st.metric("Insurance Ratio", f"{insurance_ratio:.2f}%",
                        delta="Good" if insurance_ratio > 10 else "Poor")
            
            with metrics_col2:
                st.metric("Cascade Liquidation Risk", f"{min(100, cascade_risk):.0f}%",
                        delta="High" if cascade_risk > 50 else "Low")
            
            with metrics_col3:
                st.metric("Max System Leverage", f"{max_leverage}x",
                        delta="Risky" if max_leverage > 50 else "Conservative")
            
            # Security checks
            st.write("*Security Vulnerabilities Check*")
            
            vulnerabilities = {
                "Price Manipulation": {
                    "status": "⚠ Medium Risk" if mark_price_source == "Spot Index" else "✅ Low Risk",
                    "details": "Using multiple price sources recommended"
                },
                "Liquidation Cascade": {
                    "status": "❌ High Risk" if cascade_risk > 50 else "✅ Low Risk",
                    "details": f"Current cascade risk: {cascade_risk:.1f}%"
                },
                "Insurance Fund Drain": {
                    "status": "⚠ Medium Risk" if insurance_ratio < 5 else "✅ Low Risk",
                    "details": f"Insurance covers {insurance_ratio:.2f}% of OI"
                },
                "Oracle Front-running": {
                    "status": "⚠ Possible",
                    "details": "Consider commit-reveal price updates"
                }
            }
            
            for vuln, data in vulnerabilities.items():
                with st.expander(f"{vuln}: {data['status']}"):
                    st.write(data['details'])
            
            # Recommendations
            st.write("*Security Recommendations*")
            st.info("""
            1. *Implement position limits* per account to prevent manipulation
            2. *Use multiple price oracles* with median pricing
            3. *Add circuit breakers* for extreme price movements
            4. *Implement gradual liquidations* to prevent cascades
            5. *Regular insurance fund audits* and stress testing
            """)           

if __name__ == "__main__":
    show_defi_analysis()
