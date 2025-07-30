import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from backend import gas_analyzer, formal_verifier, vulnerability_db
import plotly.express as px
from datetime import datetime, timedelta

if 'uploaded_contract' not in st.session_state:
    st.session_state.uploaded_contract = None


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
    
    # Generate sample historical data
    import pandas as pd
    import plotly.express as px
    from datetime import datetime, timedelta
    
    # Create sample historical data
    vulnerabilities_over_time = []
    base_date = datetime.now() - timedelta(days=180)
    
    vuln_types = ["Reentrancy", "Integer Overflow", "Access Control", "Front-Running", "Flash Loan"]
    
    for i in range(180):
        date = base_date + timedelta(days=i)
        for vuln in vuln_types:
            if random.random() > 0.7:  # 30% chance of vulnerability each day
                vulnerabilities_over_time.append({
                    'date': date,
                    'type': vuln,
                    'severity': random.choice(['Critical', 'High', 'Medium', 'Low']),
                    'count': random.randint(1, 5)
                })
    
    df = pd.DataFrame(vulnerabilities_over_time)
    
    if not df.empty:
        # Vulnerability trends over time
        st.write("*Vulnerability Trends (Last 6 Months)*")
        
        # Group by week and type
        df['week'] = pd.to_datetime(df['date']).dt.to_period('W')
        weekly_counts = df.groupby(['week', 'type'])['count'].sum().reset_index()
        weekly_counts['week'] = weekly_counts['week'].astype(str)
        
        fig = px.line(weekly_counts, x='week', y='count', color='type',
                     title='Weekly Vulnerability Detections by Type')
        st.plotly_chart(fig, use_container_width=True)
        
        # Most common vulnerabilities
        st.write("*Most Common Vulnerabilities*")
        vuln_counts = df.groupby('type')['count'].sum().sort_values(ascending=False)
        
        fig2 = px.pie(values=vuln_counts.values, names=vuln_counts.index,
                      title='Vulnerability Distribution')
        st.plotly_chart(fig2, use_container_width=True)
        
        # Severity distribution
        st.write("*Severity Distribution*")
        severity_counts = df.groupby('severity')['count'].sum()
        
        colors = {'Critical': '#FF4B4B', 'High': '#FFA500', 'Medium': '#FFD700', 'Low': '#90EE90'}
        fig3 = px.bar(x=severity_counts.index, y=severity_counts.values,
                      color=severity_counts.index,
                      color_discrete_map=colors,
                      title='Vulnerabilities by Severity')
        st.plotly_chart(fig3, use_container_width=True)
        
        # Recent high-profile exploits
        st.write("*Recent DeFi Exploits Database*")
        
        exploits = [
            {"Date": "2023-10", "Protocol": "Curve Finance", "Loss": "$73M", "Type": "Reentrancy", "Chain": "Ethereum"},
            {"Date": "2023-07", "Protocol": "Multichain", "Loss": "$126M", "Type": "Private Key", "Chain": "Multiple"},
            {"Date": "2023-04", "Protocol": "Euler Finance", "Loss": "$197M", "Type": "Flash Loan", "Chain": "Ethereum"},
            {"Date": "2023-03", "Protocol": "Sentiment", "Loss": "$1M", "Type": "Price Oracle", "Chain": "Arbitrum"},
            {"Date": "2022-10", "Protocol": "Mango Markets", "Loss": "$116M", "Type": "Price Manipulation", "Chain": "Solana"},
        ]
        
        exploit_df = pd.DataFrame(exploits)
        st.dataframe(exploit_df, use_container_width=True)
        
        # Statistics summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Exploits", len(exploits))
        with col2:
            total_loss = sum(float(e['Loss'].replace('$', '').replace('M', '')) for e in exploits)
            st.metric("Total Loss", f"${total_loss:.0f}M")
        with col3:
            st.metric("Avg Loss", f"${total_loss/len(exploits):.1f}M")
        with col4:
            most_common = max(set(e['Type'] for e in exploits), key=lambda x: sum(1 for e in exploits if e['Type'] == x))
            st.metric("Most Common", most_common)
    else:
        st.info("No historical data available. Run some analyses to build history!")
if __name__ == "__main__":
    show_advanced_analysis()

