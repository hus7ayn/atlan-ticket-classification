import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Grok API configuration
GROK_API_KEY = os.getenv('GROK_API_KEY')
GROK_MODEL = os.getenv('GROK_MODEL', 'gemma2-9b-it')
GROK_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Tavily API configuration
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
TAVILY_API_URL = "https://api.tavily.com/search"

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