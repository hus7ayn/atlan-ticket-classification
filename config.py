import os
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# Try to import streamlit for cloud deployment
try:
    import streamlit as st
    # Use Streamlit secrets if available (for cloud deployment)
    try:
        if hasattr(st, 'secrets') and st.secrets:
            GROK_API_KEY = st.secrets.get('GROK_API_KEY')
            TAVILY_API_KEY = st.secrets.get('TAVILY_API_KEY')
            GROK_MODEL = st.secrets.get('GROK_MODEL', 'gemma2-9b-it')
        else:
            # Fallback to environment variables (for local development)
            GROK_API_KEY = os.getenv('GROK_API_KEY')
            TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
            GROK_MODEL = os.getenv('GROK_MODEL', 'gemma2-9b-it')
    except Exception:
        # Fallback to environment variables if secrets access fails
        GROK_API_KEY = os.getenv('GROK_API_KEY')
        TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
        GROK_MODEL = os.getenv('GROK_MODEL', 'gemma2-9b-it')
except ImportError:
    # Fallback to environment variables if streamlit is not available
    GROK_API_KEY = os.getenv('GROK_API_KEY')
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
    GROK_MODEL = os.getenv('GROK_MODEL', 'gemma2-9b-it')

# API URLs
GROK_API_URL = "https://api.groq.com/openai/v1/chat/completions"
TAVILY_API_URL = "https://api.tavily.com/search"

# Debug: Print API key status (remove in production)
def debug_api_keys():
    """Debug function to check API key status"""
    print(f"🔑 Grok API Key: {'✅ Set' if GROK_API_KEY else '❌ Missing'}")
    print(f"🔑 Tavily API Key: {'✅ Set' if TAVILY_API_KEY else '❌ Missing'}")
    if GROK_API_KEY:
        print(f"🔑 Grok Key Preview: {GROK_API_KEY[:10]}...")
    if TAVILY_API_KEY:
        print(f"🔑 Tavily Key Preview: {TAVILY_API_KEY[:10]}...")

# Import standardized values from utils
from utils import get_supported_topics, get_sentiment_options, get_priority_levels

# Classification categories
TOPIC_TAGS = get_supported_topics()
SENTIMENT_OPTIONS = get_sentiment_options()
PRIORITY_LEVELS = get_priority_levels()

# Standardized filenames
DEFAULT_REPORT_FILENAME = "atlan_tickets_classification_report.json"
DEFAULT_CSV_FILENAME = "atlan_tickets_classification.csv"
DEFAULT_TICKETS_FILENAME = "tickets_data.json"