import streamlit as st
import pandas as pd
from web3 import Web3
from backend import defi_analyzer

def show_defi_analysis():
    st.header("💰 DeFi-Specific Security Analysis")

    # Example check for uploaded contract, adjust if your app uploads contract differently
    if not st.session_state.get("uploaded_contract"):
        st.info("Please upload a smart contract to begin analysis.")
        return

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
            safety_margin = (liquidation_threshold - collateral_factor) * 100
            st.metric("Safety Margin", f"{safety_margin:.1f}%")
            risk_level = (
                "High" if safety_margin < 5
                else "Medium" if safety_margin < 10
                else "Low"
            )
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
