import streamlit as st

try:
    from dashboard.settings import DashboardSettings
except ModuleNotFoundError:
    # When running from dashboard directory directly
    from settings import DashboardSettings

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