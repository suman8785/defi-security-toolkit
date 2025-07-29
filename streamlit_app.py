import streamlit as st
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
