import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from backend import gas_analyzer, formal_verifier, vulnerability_db

def show_advanced_analysis():
    st.header("🔬 Advanced Analysis Tools")
    
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Gas Optimization", "Formal Verification", "Pattern Matching", "Historical Analysis"]
    )
    
    if analysis_type == "Gas Optimization":
        st.subheader("⛽ Gas Usage Analysis")
        
        if st.session_state.uploaded_contract:
            gas_results = gas_analyzer.analyze_gas_usage(st.session_state.uploaded_contract)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Total Estimated Gas",
                    f"{gas_results['total_estimated_gas']:,}",
                    help="Rough estimate based on operation counts"
                )
            with col2:
                storage_gas = gas_results['storage_patterns']['estimated_gas']
                st.metric("Storage Operations Gas", f"{storage_gas:,}")
            with col3:
                optimizable = sum(1 for f in gas_results['gas_heavy_functions'] if f['optimizable'])
                st.metric("Optimizable Functions", optimizable)
            
            # Gas heavy functions
            st.subheader("Gas Heavy Functions")
            if gas_results['gas_heavy_functions']:
                df = pd.DataFrame(gas_results['gas_heavy_functions'])
                fig = go.Figure(data=[
                    go.Bar(
                        x=df['name'],
                        y=df['estimated_gas'],
                        marker_color=['red' if opt else 'blue' for opt in df['optimizable']]
                    )
                ])
                fig.update_layout(title="Estimated Gas by Function")
                st.plotly_chart(fig, use_container_width=True)
            
            # Optimization opportunities
            st.subheader("💡 Optimization Opportunities")
            for opt in gas_results['optimization_opportunities']:
                with st.expander(f"{opt['type']} - {opt['potential_savings']} savings"):
                    st.write(f"*Description:* {opt['description']}")
                    st.write(f"*Recommendation:* {opt['recommendation']}")
            
            # Loop analysis
            if gas_results['loop_analysis']:
                st.warning(f"⚠ Found {len(gas_results['loop_analysis'])} potentially expensive loops")
                for loop in gas_results['loop_analysis']:
                    st.write(f"- {loop['issue']}: {loop['recommendation']}")
    
    elif analysis_type == "Formal Verification":
        st.subheader("🔐 Formal Property Verification")
        
        # Property input
        st.write("Define properties to verify:")
        properties = []
        
        col1, col2 = st.columns([3, 1])
        with col1:
            prop1 = st.text_input("Property 1", "balance >= 0")
            prop2 = st.text_input("Property 2", "totalSupply == sum(balances)")
            prop3 = st.text_input("Property 3", "owner != address(0)")
        
        properties = [p for p in [prop1, prop2, prop3] if p]
        
        if st.button("Verify Properties") and st.session_state.uploaded_contract:
            with st.spinner("Running formal verification..."):
                results = formal_verifier.verify_properties(
                    st.session_state.uploaded_contract,
                    properties
                )
                
                # Display results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Verified", len(results['verified_properties']))
                with col2:
                    st.metric("❌ Failed", len(results['failed_properties']))
                with col3:
                    st.metric("❓ Undecidable", len(results['undecidable']))
                
                # Detailed results
                if results['verified_properties']:
                    st.success("Verified Properties:")
                    for prop in results['verified_properties']:
                        st.write(f"✅ {prop}")
                
                if results['failed_properties']:
                    st.error("Failed Properties:")
                    for prop in results['failed_properties']:
                        st.write(f"❌ {prop}")
                        if prop in results['counterexamples']:
                            st.code(f"Counterexample: {results['counterexamples'][prop]}")
    
    elif analysis_type == "Pattern Matching":
        st.subheader("🔍 Vulnerability Pattern Matching")
        
        # Get patterns from database
        patterns = vulnerability_db.get_patterns()
        
        # Display pattern library
        st.write("*Active Patterns:*")
        pattern_df = pd.DataFrame(patterns)
        st.dataframe(
            pattern_df[['name', 'severity', 'description', 'cwe_id']],
            use_container_width=True
        )
        
        if st.button("Scan with Patterns") and st.session_state.uploaded_contract:
            with st.spinner("Scanning for patterns..."):
                import re
                
                with open(st.session_state.uploaded_contract, 'r') as f:
                    content = f.read()
                
                matches = []
                for pattern in patterns:
                    if re.search(pattern['pattern'], content):
                        matches.append(pattern)
                
                if matches:
                    st.warning(f"Found {len(matches)} pattern matches!")
                    for match in matches:
                        severity_color = {
                            'critical': '🔴',
                            'high': '🟠',
                            'medium': '🟡',
                            'low': '🟢'
                        }.get(match['severity'], '⚪')
                        
                        with st.expander(f"{severity_color} {match['name']} - {match['severity'].upper()}"):
                            st.write(f"*Description:* {match['description']}")
                            st.write(f"*Recommendation:* {match['recommendation']}")
                            st.write(f"*CWE ID:* {match['cwe_id']}")
                else:
                    st.success("No pattern matches found!")
    
    elif analysis_type == "Historical Analysis":
        st.subheader("📊 Historical Vulnerability Analysis")
        
        stats = vulnerability_db.get_stats()
        
        # Common vulnerabilities chart
        if stats['common_vulnerabilities']:
            st.write("*Most Common Vulnerabilities:*")
            vuln_df = pd.DataFrame(stats['common_vulnerabilities'])
            fig = go.Figure(data=[
                go.Pie(
                    labels=vuln_df['type'],
                    values=vuln_df['count'],
                    hole=0.3
                )
            ])
            fig.update_layout(title="Vulnerability Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Severity distribution
        if stats['severity_distribution']:
            st.write("*Severity Distribution:*")
            severities = list(stats['severity_distribution'].keys())
            counts = list(stats['severity_distribution'].values())
            
            fig = go.Figure(data=[
                go.Bar(
                    x=severities,
                    y=counts,
                    marker_color=['red', 'orange', 'yellow', 'green', 'gray']
                )
            ])
            fig.update_layout(title="Findings by Severity")
            st.plotly_chart(fig, use_container_width=True)
        
        # Tool effectiveness
        if stats['tool_effectiveness']:
            st.write("*Tool Effectiveness:*")
            tools = list(stats['tool_effectiveness'].keys())
            findings = list(stats['tool_effectiveness'].values())
            
            col1, col2 = st.columns(2)
            with col1:
                for tool, count in zip(tools, findings):
                    st.metric(f"{tool} Findings", count)