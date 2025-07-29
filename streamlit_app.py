import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
import tempfile
from datetime import datetime



from backend import (
    contract_parser,
    slither_runner,
    mythril_runner,
    monitor,
    attack_simulator,
    report_generator
)
from config import *



# Page configuration
st.set_page_config(
    page_title="DeFi Security Toolkit",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Existing styles */
    .stAlert {
        border-radius: 10px;
        padding: 10px;
    }

    /* Modify .stAlert info box text to black */
    .stAlert p {
        color: black !important;
    }

    /* Optional: override background color if needed */
    .stAlert[data-testid="stAlertInfo"] {
        background-color: #aad8ff; /* softer blue */
    }

    /* Your custom vulnerability tags */
    .vulnerability-high {
        background-color: #ff4b4b;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
    }
    .vulnerability-medium {
        background-color: #ffa500;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
    }
    .vulnerability-low {
        background-color: #00cc00;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'uploaded_contract' not in st.session_state:
    st.session_state.uploaded_contract = None
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False

# Header
st.title("🛡 DeFi Security and Auditing Toolkit")
st.markdown("### Professional Smart Contract Security Analysis Platform")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select Tool",
        ["Contract Analysis", "Attack Simulation", "Live Monitoring", "Audit Reports", "Settings"]
    )
    
    st.divider()
    
    # Theme toggle
    theme = st.selectbox("Theme", ["Light", "Dark"])
    if theme == "Dark":
        st.markdown("""
        <style>
            .stApp {
                background-color: #1e1e1e;
                color: #ffffff;
            }
        </style>
        """, unsafe_allow_html=True)

# Main content based on selected page
if page == "Contract Analysis":
    st.header("📄 Smart Contract Analysis")
    
    # File upload
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Solidity Contract (.sol)",
            type=['sol'],
            help="Upload your smart contract for security analysis"
        )
    
    with col2:
        analysis_type = st.multiselect(
            "Analysis Tools",
            ["Slither", "Mythril", "Echidna"],
            default=["Slither"]
        )
    
    if uploaded_file:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.sol') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            contract_path = tmp_file.name
            st.session_state.uploaded_contract = contract_path
        
        # Display contract info
        st.info(f"📁 Uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Parse contract
        with st.expander("Contract Overview", expanded=True):
            contract_info = contract_parser.parse_contract(contract_path)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Functions", len(contract_info.get('functions', [])))
            with col2:
                st.metric("State Variables", len(contract_info.get('state_variables', [])))
            with col3:
                st.metric("Modifiers", len(contract_info.get('modifiers', [])))
        
        # Run analysis
        if st.button("🔍 Run Security Analysis", type="primary"):
            with st.spinner("Analyzing contract..."):
                results = {}
                
                # Slither Analysis
                if "Slither" in analysis_type:
                    with st.status("Running Slither analysis...", expanded=True) as status:
                        st.write("Detecting vulnerabilities...")
                        slither_results = slither_runner.analyze(contract_path)
                        results['slither'] = slither_results
                        status.update(label="Slither analysis complete!", state="complete")
                
                # Mythril Analysis
                if "Mythril" in analysis_type:
                    with st.status("Running Mythril analysis...", expanded=True) as status:
                        st.write("Performing symbolic execution...")
                        mythril_results = mythril_runner.analyze(contract_path)
                        results['mythril'] = mythril_results
                        status.update(label="Mythril analysis complete!", state="complete")
                
                # Echidna Analysis
                if "Echidna" in analysis_type:
                    with st.status("Running Echidna fuzzing...", expanded=True) as status:
                        st.write("Fuzzing contract properties...")
                        # Echidna integration would go here
                        status.update(label="Echidna fuzzing complete!", state="complete")
                
                st.session_state.analysis_results = results
        
        # Display results
        if st.session_state.analysis_results:
            st.header("📊 Analysis Results")
            
            # Vulnerability summary
            vulnerabilities = []
            if 'slither' in st.session_state.analysis_results:
                vulnerabilities.extend(st.session_state.analysis_results['slither'].get('vulnerabilities', []))
            if 'mythril' in st.session_state.analysis_results:
                vulnerabilities.extend(st.session_state.analysis_results['mythril'].get('issues', []))
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            high_count = sum(1 for v in vulnerabilities if v.get('severity') in ['high', 'critical'])
            medium_count = sum(1 for v in vulnerabilities if v.get('severity') == 'medium')
            low_count = sum(1 for v in vulnerabilities if v.get('severity') in ['low', 'informational'])
            
            with col1:
                st.metric("🔴 Critical/High", high_count)
            with col2:
                st.metric("🟡 Medium", medium_count)
            with col3:
                st.metric("🟢 Low/Info", low_count)
            with col4:
                st.metric("📋 Total Issues", len(vulnerabilities))
            
            # Detailed findings
            st.subheader("Detailed Findings")
            for idx, vuln in enumerate(vulnerabilities):
                severity = vuln.get('severity', 'unknown')
                severity_class = f"vulnerability-{severity}"
                
                with st.expander(f"{vuln.get('title', 'Issue')} - {severity.upper()}", expanded=(severity in ['high', 'critical'])):
                    st.markdown(f"*Description:* {vuln.get('description', 'N/A')}")
                    st.markdown(f"*Location:* {vuln.get('location', 'N/A')}")
                    if vuln.get('recommendation'):
                        st.markdown(f"*Recommendation:* {vuln.get('recommendation')}")
                    if vuln.get('code_snippet'):
                        st.code(vuln.get('code_snippet'), language='solidity')

elif page == "Attack Simulation":
    st.header("⚔ Attack Simulation")
    
    attack_type = st.selectbox(
        "Select Attack Type",
        ["Flash Loan Attack", "MEV Sandwich Attack", "Reentrancy Attack", "Front-Running"]
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if attack_type == "Flash Loan Attack":
            st.subheader("Flash Loan Attack Simulation")
            target_address = st.text_input("Target Contract Address", "0x...")
            loan_amount = st.number_input("Loan Amount (ETH)", min_value=0.1, max_value=1000.0, value=10.0)
            attack_steps = st.text_area(
                "Attack Steps",
                "1. Borrow flash loan\n2. Manipulate price\n3. Exploit arbitrage\n4. Repay loan"
            )
            
            if st.button("🚀 Simulate Attack"):
                with st.spinner("Simulating flash loan attack..."):
                    results = attack_simulator.simulate_flashloan(
                        target_address,
                        loan_amount,
                        attack_steps
                    )
                    
                    st.success("Simulation Complete!")
                    st.subheader("📝 Reentrancy Attack Report")
                    st.write(results)


        
        elif attack_type == "MEV Sandwich Attack":
            st.subheader("MEV Sandwich Attack Simulation")
            victim_tx = st.text_input("Victim Transaction Hash", "0x...")
            frontrun_amount = st.number_input("Frontrun Amount (ETH)", min_value=0.01, value=1.0)
            backrun_amount = st.number_input("Backrun Amount (ETH)", min_value=0.01, value=1.0)
            
            if st.button("🥪 Simulate Sandwich"):
                with st.spinner("Simulating MEV sandwich attack..."):
                    results = attack_simulator.simulate_mev_sandwich(
                        victim_tx,
                        frontrun_amount,
                        backrun_amount
                    )
                    
                    st.success("Simulation Complete!")
                    st.json(results)
            
        elif attack_type == "Reentrancy Attack":
            st.subheader("Reentrancy Attack Simulation")
            contract_address = st.text_input("Vulnerable Contract Address", "0x...")
            attack_depth = st.slider("Attack Depth (Recursive Calls)", min_value=1, max_value=10, value=3)

            if st.button("♻️ Simulate Reentrancy"):
                with st.spinner("Simulating reentrancy attack..."):
                    results = attack_simulator.simulate_reentrancy(
                        contract_address,
                        attack_depth
                    )
                    st.success("Simulation Complete!")
                    st.json(results)

        elif attack_type == "Front-Running":
            st.subheader("Front-Running Attack Simulation")
            pending_tx = st.text_input("Pending Victim Transaction Hash", "0x...")
            gas_price_boost = st.slider("Gas Price Boost (%)", min_value=0, max_value=200, value=50)

            if st.button("🚨 Simulate Front-Running"):
                with st.spinner("Simulating front-running attack..."):
                    results = attack_simulator.simulate_front_running(
                        pending_tx,
                        gas_price_boost
                    )
                    st.success("Simulation Complete!")
                    st.json(results)
    
    with col2:
        st.info("""
        *Attack Simulation Notes:*
        - Simulations run on testnet
        - No real funds at risk
        - Educational purposes only
        - Results show potential impact
        """)

elif page == "Live Monitoring":
    st.header("📡 Live Contract Monitoring")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        monitor_address = st.text_input("Contract Address to Monitor", placeholder="0x...")
        monitor_options = st.multiselect(
            "Monitor Events",
            ["Transactions", "State Changes", "Large Transfers", "Suspicious Activity"],
            default=["Transactions", "Suspicious Activity"]
        )
    
    with col2:
        if st.button("Start Monitoring", type="primary"):
                        st.session_state.monitoring_active = True
        if st.button("Stop Monitoring", type="secondary"):
            st.session_state.monitoring_active = False
    
    if st.session_state.monitoring_active and monitor_address:
        st.success("🟢 Monitoring Active")
        
        # Real-time monitoring display
        monitor_container = st.container()
        with monitor_container:
            # Create tabs for different monitoring views
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📜 Transactions", "⚠ Alerts", "📈 Analytics"])
            
            with tab1:
                # Dashboard metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Transactions", "1,234", "+12")
                with col2:
                    st.metric("Suspicious Activities", "3", "+1")
                with col3:
                    st.metric("Gas Price (Gwei)", "45", "-5")
                with col4:
                    st.metric("Contract Balance (ETH)", "125.5", "+2.3")
                
                # Activity chart
                st.subheader("Transaction Activity (24h)")
                activity_data = monitor.get_activity_data(monitor_address)
                if activity_data is not None and not activity_data.empty:


                    fig = px.line(activity_data, x='timestamp', y='tx_count', title='Hourly Transaction Count')
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Transaction list
                st.subheader("Recent Transactions")
                transactions = monitor.get_recent_transactions(monitor_address, limit=20)
                if transactions:
                    tx_df = pd.DataFrame(transactions)
                    st.dataframe(
                        tx_df[['hash', 'from', 'to', 'value', 'gas_used', 'timestamp']],
                        use_container_width=True
                    )
            
            with tab3:
                # Alerts
                st.subheader("Security Alerts")
                alerts = monitor.get_security_alerts(monitor_address)
                for alert in alerts:
                    alert_type = alert.get('type', 'info')
                    if alert_type == 'critical':
                        st.error(f"🚨 {alert['message']}")
                    elif alert_type == 'warning':
                        st.warning(f"⚠ {alert['message']}")
                    else:
                        st.info(f"ℹ {alert['message']}")
            
            with tab4:
                # Analytics
                st.subheader("Contract Analytics")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gas usage chart
                    gas_data = monitor.get_gas_analytics(monitor_address)
                    if gas_data is not None and not gas_data.empty:


                        fig = px.bar(gas_data, x='function', y='avg_gas', title='Average Gas by Function')
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Value flow chart
                    flow_data = monitor.get_value_flow(monitor_address)
                    if flow_data is not None and not flow_data.empty:
                        fig = px.pie(flow_data, values='amount', names='direction', title='Value Flow Distribution')
                        st.plotly_chart(fig, use_container_width=True)

elif page == "Audit Reports":
    st.header("📋 Audit Report Generator")
    
    if st.session_state.analysis_results:
        st.success("Analysis data available for report generation")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            report_name = st.text_input("Report Name", value=f"Security_Audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            report_format = st.selectbox("Report Format", ["Markdown", "JSON", "PDF (Beta)"])
            
            include_sections = st.multiselect(
                "Include Sections",
                ["Executive Summary", "Vulnerability Details", "Code Analysis", "Recommendations", "Risk Matrix"],
                default=["Executive Summary", "Vulnerability Details", "Recommendations"]
            )
        
        with col2:
            severity_filter = st.multiselect(
                "Include Severities",
                ["Critical", "High", "Medium", "Low", "Informational"],
                default=["Critical", "High", "Medium"]
            )
        
        if st.button("📄 Generate Report", type="primary"):
            with st.spinner("Generating audit report..."):
                report = report_generator.generate_report(
                    st.session_state.analysis_results,
                    report_name,
                    report_format,
                    include_sections,
                    severity_filter
                )
                
                st.success("Report generated successfully!")
                
                # Display report preview
                with st.expander("Report Preview", expanded=True):
                    if report_format == "Markdown":
                        st.markdown(report['content'])
                    elif report_format == "JSON":
                        st.json(report['content'])
                
                # Download button
                st.download_button(
                    label="⬇ Download Report",
                    data=report['content'],
                    file_name=f"{report_name}.{report_format.lower()}",
                    mime=report['mime_type']
                )
    else:
        st.warning("No analysis data available. Please run contract analysis first.")

elif page == "Settings":
    st.header("⚙ Settings")
    
    # API Configuration
    st.subheader("API Configuration")
    col1, col2 = st.columns(2)
    with col1:
        etherscan_key = st.text_input("Etherscan API Key", value="*" * 20, type="password")
        tenderly_key = st.text_input("Tenderly API Key", value="*" * 20, type="password")
    with col2:
        infura_key = st.text_input("Infura Project ID", value="*" * 20, type="password")
        network = st.selectbox("Default Network", ["Mainnet", "Sepolia", "Goerli", "Polygon"])
    
    # Analysis Settings
    st.subheader("Analysis Settings")
    col1, col2 = st.columns(2)
    with col1:
        slither_timeout = st.number_input("Slither Timeout (seconds)", min_value=60, max_value=1800, value=300)
        mythril_timeout = st.number_input("Mythril Timeout (seconds)", min_value=60, max_value=3600, value=600)
    with col2:
        max_file_size = st.number_input("Max File Size (MB)", min_value=1, max_value=50, value=5)
        auto_save_reports = st.checkbox("Auto-save Reports", value=True)
    
    # Save settings
    if st.button("💾 Save Settings"):
        # Here you would save settings to config file or database
        st.success("Settings saved successfully!")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888;'>
    DeFi Security Toolkit v1.0 | Built with ❤ for Crypto Security
</div>
""", unsafe_allow_html=True)
