# src/components/navigation.py - Reusable Navigation Component
import streamlit as st

def render_navigation_bar(current_page="Home"):
    """
    Renders a top navigation bar for the application
    
    Args:
        current_page: The current page name for highlighting
    """
    
    # Navigation styling
    st.markdown("""
    <style>
    .nav-container {
        background: linear-gradient(90deg, #0f1419 0%, #1c2833 50%, #0f1419 100%);
        padding: 5px 20px;
        border-radius: 0px;
        margin: -1rem -1rem 10px -1rem;
        border: none;
        border-bottom: 1px solid rgba(0, 212, 255, 0.3);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .nav-button {
        background: transparent;
        color: #b0b0b0;
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 8px;
        padding: 8px 16px;
        margin: 0 5px;
        text-decoration: none;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .nav-button:hover {
        background: rgba(0, 212, 255, 0.1);
        border-color: rgba(0, 212, 255, 0.5);
        color: #00d4ff;
        transform: translateY(-1px);
    }
    .nav-button.active {
        background: rgba(0, 212, 255, 0.2);
        border-color: #00d4ff;
        color: #00d4ff;
        font-weight: bold;
    }
    .nav-title {
        color: #00d4ff;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    .nav-divider {
        color: rgba(0, 212, 255, 0.3);
        margin: 0 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Navigation bar content
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 6, 2])
    
    with col1:
        # Logo/Title
        st.markdown('<h3 class="nav-title">🔆 RE Analyst</h3>', unsafe_allow_html=True)
    
    with col2:
        # Navigation buttons
        nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)
        
        with nav_col1:
            home_class = "nav-button active" if current_page == "Home" else "nav-button"
            if st.button("🏠 Home", key="nav_home", help="Return to main dashboard"):
                st.switch_page("app.py")
        
        with nav_col2:
            deep_dive_class = "nav-button active" if current_page == "Deep Dive" else "nav-button"
            if st.button("🔍 Deep Dive", key="nav_deep_dive", help="Stock analysis tools"):
                st.switch_page("pages/Deep_Dive_Analysis.py")
        
        with nav_col3:
            executive_class = "nav-button active" if current_page == "Executive Summary" else "nav-button"
            if st.button("📊 Executive", key="nav_executive", help="Executive summaries & charts"):
                st.switch_page("pages/Executive_Summary_ProPlus.py")
        
        with nav_col4:
            ai_class = "nav-button active" if current_page == "AI Assistant" else "nav-button"
            if st.button("🤖 AI Assistant", key="nav_ai", help="Natural language queries"):
                try:
                    from src.agent.nl_orchestrator import NLOrchestrator
                    st.switch_page("pages/AI_Assistant.py")
                except ImportError:
                    st.error("⚠️ AI Assistant unavailable")
        
        with nav_col5:
            if st.button("🔄 Refresh", key="nav_refresh", help="Refresh current page"):
                st.rerun()
    
    with col3:
        # Status indicators (optional)
        st.markdown('<p style="color: #00d4ff; text-align: right; margin: 0; font-size: 0.8rem;">✅ Live Data</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)