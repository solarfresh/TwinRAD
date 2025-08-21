import streamlit as st

# Smart import: Use relative import when running directly, absolute when installed
if __package__ is None:
    # Direct execution (python app.py or streamlit run app.py)
    from settings import DashboardSettings
else:
    # Package execution (python -m dashboard.app or installed package)
    from dashboard.settings import DashboardSettings

# Initialize dashboard-specific settings
settings = DashboardSettings()

def main():
    """Main entry point for TwinRAD dashboard."""
    st.title(settings.title)
    st.write("Multi-agent red teaming framework monitoring dashboard")
    st.write("Coming soon...")
    
    # Show configuration in sidebar
    with st.sidebar:
        st.header("Configuration")
        st.write(f"Host: {settings.dashboard_host}")
        st.write(f"Port: {settings.dashboard_port}")
        st.write(f"Theme: {settings.theme}")
        st.write(f"Log Level: {settings.log_level}")


if __name__ == "__main__":
    main()