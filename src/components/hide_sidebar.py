# src/components/hide_sidebar.py - Utility to completely hide sidebar
import streamlit as st

def hide_sidebar_completely():
    """
    Completely hides the Streamlit sidebar using multiple approaches
    to prevent any visual flash during loading.
    """
    
    # Method 1: Immediate CSS injection with highest priority
    st.markdown("""
    <style>
        /* Force hide sidebar with maximum specificity */
        html body div.stApp div.main-container div[data-testid="stSidebar"],
        html body div.stApp section[data-testid="stSidebar"],
        html body div[data-testid="stSidebar"],
        section[data-testid="stSidebar"],
        .css-1d391kg,
        .css-1l02zno, 
        .css-17eq0hr,
        .css-164nlkn,
        .css-1cypcdb,
        .css-1y4p8pa,
        .stSidebar,
        .css-9s5bis,
        .css-1544g2n {
            display: none !important;
            visibility: hidden !important;
            width: 0px !important;
            min-width: 0px !important;
            max-width: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
            opacity: 0 !important;
            z-index: -9999 !important;
            position: absolute !important;
            left: -9999px !important;
        }
        
        /* Hide sidebar toggle buttons with multiple selectors */
        button[aria-label="Open sidebar"],
        button[aria-label="Close sidebar"],
        button[title="Open sidebar"],
        button[title="Close sidebar"],
        .css-1rs6os,
        .css-17ziqus,
        .css-k1ih3n {
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Optimize main content area */
        .main .block-container {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: none !important;
            width: 100% !important;
            margin-left: 0 !important;
        }
        
        /* Remove any sidebar-related spacing */
        .css-18e3th9,
        .css-1d391kg {
            padding-left: 0rem !important;
            margin-left: 0rem !important;
        }
        
        /* Hide Streamlit branding */
        #MainMenu { visibility: hidden !important; }
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        
        /* Additional hiding for various Streamlit versions */
        [class*="sidebar"],
        [id*="sidebar"],
        [data-testid*="sidebar"] {
            display: none !important;
            visibility: hidden !important;
        }
    </style>
    
    <script>
        // JavaScript fallback to hide sidebar immediately
        (function() {
            function hideSidebar() {
                const selectors = [
                    '[data-testid="stSidebar"]',
                    'section[data-testid="stSidebar"]',
                    '.stSidebar',
                    '.css-1d391kg',
                    '.css-1l02zno',
                    '.css-17eq0hr',
                    '.css-164nlkn',
                    '.css-1cypcdb',
                    '.css-1y4p8pa',
                    '.css-9s5bis',
                    '.css-1544g2n'
                ];
                
                selectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        el.style.display = 'none';
                        el.style.visibility = 'hidden';
                        el.style.width = '0px';
                        el.style.opacity = '0';
                    });
                });
            }
            
            // Hide immediately
            hideSidebar();
            
            // Hide on DOM ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', hideSidebar);
            }
            
            // Hide on window load
            window.addEventListener('load', hideSidebar);
            
            // Monitor for dynamic sidebar creation
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes.length) {
                        hideSidebar();
                    }
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        })();
    </script>
    """, unsafe_allow_html=True)