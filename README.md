# Atlan Ticket Classification System

A comprehensive ticket classification system that uses the Grok LLM to automatically classify Atlan support tickets by topic, sentiment, and priority.

## Features

### Core Classification
- **Topic Classification**: Categorizes tickets into relevant topics like How-to, Product, Connector, Lineage, API/SDK, SSO, Glossary, Best practices, and Sensitive data
- **Sentiment Analysis**: Identifies user sentiment (Frustrated, Curious, Angry, Neutral, Positive, Concerned)
- **Priority Assessment**: Determines ticket priority (P0 High, P1 Medium, P2 Low)
- **Comprehensive Reporting**: Generates detailed JSON and CSV reports with statistics and reasoning

### Smart Response Generation (NEW)
- **Tavily Integration**: Uses Tavily API to generate intelligent answers for supported topics
- **Knowledge Base Search**: Searches Atlan documentation and developer hub for accurate answers
- **Source Citations**: All answers include proper source URLs and citations
- **Smart Routing**: Automatically routes unsupported topics to appropriate teams
- **API-Ready**: Built for easy frontend integration


## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   The system uses the Grok API key and model from the config.py file. The API key is already configured, but you can modify it if needed.

## Usage

### 🌐 Web UI (Recommended)

Launch the interactive Streamlit web interface:

```bash
python run_streamlit.py
```

This will open a web browser with two main pages:

#### 📊 Classification Report Page
- **Load Button**: Process all 30 tickets with one click
- **Statistics Dashboard**: Interactive charts and metrics
- **Ticket Details**: View actual ticket content (subject & body)
- **Filtering**: Filter by topic, sentiment, or priority
- **Classification Details**: See AI reasoning for each decision

#### 💬 Interactive Query Page
- **Query Input**: Ask any question about Atlan
- **Smart Classification**: Automatic topic, sentiment, priority detection
- **Tavily Integration**: Get answers from Atlan documentation
- **Grok Summarization**: AI-summarized responses
- **Source Citations**: Clickable links to documentation

### 📋 Command Line Usage

#### Process All Provided Tickets

To classify all 30 tickets provided in the original request:

```bash
python process_all_tickets.py
```

This will:
- Process all 30 tickets using the Grok LLM
- Display real-time progress and results
- Generate comprehensive statistics
- Save detailed reports in JSON and CSV formats

### Process Custom Tickets

To classify your own tickets, you have several options:

#### Option 1: Add tickets to the data file
```bash
python add_ticket.py
```
This interactive script allows you to add new tickets to `tickets_data.json`.

#### Option 2: Modify the JSON data file directly
Edit `tickets_data.json` to add your tickets in the same format:
```json
[
  {
    "id": "TICKET-001",
    "subject": "Your ticket subject",
    "body": "Your ticket body content"
  }
]
```

#### Option 3: Use the smart processor (NEW)
```python
from smart_ticket_processor import SmartTicketProcessor

# Process single query with intelligent response
processor = SmartTicketProcessor()
result = processor.process_ticket_with_query("How to connect Snowflake to Atlan?")

if result['success']:
    print(f"Topic: {result['response']['internal_analysis']['topic']}")
    print(f"Response: {result['response']['final_response']}")
```

#### Option 4: Use the API (NEW)
```python
from ticket_api import TicketAPI

# API-ready processing
api = TicketAPI()
result = api.process_query("What are the API authentication methods?")

if result['success']:
    print(f"Answer: {result['final_response']['answer']}")
    print(f"Sources: {result['final_response']['sources']}")
```

#### Option 5: Use the classifier programmatically
```python
from ticket_classifier import TicketClassifier

# Your ticket data
tickets = [
    {
        "id": "TICKET-001",
        "subject": "Your ticket subject",
        "body": "Your ticket body content"
    }
]

# Classify tickets
classifier = TicketClassifier()
classifier.load_tickets(tickets)
results = classifier.classify_all_tickets()
classifier.print_summary()
classifier.save_report("my_classification_report.json")
```

## Data Files

### Input Data
- **`tickets_data.json`**: Contains all ticket data in JSON format
  - Each ticket has: `id`, `subject`, `body`
  - Easy to edit and maintain
  - Can be updated using `add_ticket.py` script

### Output Files

The system generates two output files:

1. **JSON Report** (`atlan_tickets_classification_report.json`):
   - Complete classification results
   - Detailed statistics and distributions
   - Reasoning for each classification

2. **CSV Report** (`atlan_tickets_classification.csv`):
   - Tabular format for easy analysis
   - Suitable for importing into Excel or other tools

## Classification Categories

### Topic Tags
- **How-to**: Questions about how to use features
- **Product**: General product questions or feature requests
- **Connector**: Issues with data source connections
- **Lineage**: Questions about data lineage features
- **API/SDK**: Technical questions about APIs or SDKs
- **SSO**: Single Sign-On authentication issues
- **Glossary**: Business glossary and metadata questions
- **Best practices**: Questions about recommended approaches
- **Sensitive data**: PII, security, or compliance questions

### Sentiment Options
- **Frustrated**: User is clearly frustrated or blocked
- **Curious**: User is asking exploratory questions
- **Angry**: User is expressing anger or strong dissatisfaction
- **Neutral**: User is matter-of-fact or professional
- **Positive**: User is expressing satisfaction or enthusiasm
- **Concerned**: User is worried about something but not angry

### Priority Levels
- **P0 (High)**: Critical issues, blocking work, urgent deadlines
- **P1 (Medium)**: Important but not blocking, standard support needs
- **P2 (Low)**: General questions, feature requests, non-urgent

## System Architecture

### Core Files
- **`config.py`**: Configuration and constants (Grok + Tavily API keys)
- **`grok_client.py`**: Grok API integration with error handling and retry logic
- **`ticket_classifier.py`**: Main classification logic and reporting
- **`process_all_tickets.py`**: Script to process all provided tickets

### Smart Response System (NEW)
- **`tavily_client.py`**: Tavily API integration for intelligent answers
- **`smart_ticket_processor.py`**: Combines classification and response generation
- **`ticket_api.py`**: API layer ready for frontend integration
- **`add_ticket.py`**: Interactive script to add new tickets

### Data Files
- **`tickets_data.json`**: Input ticket data
- **`atlan_tickets_classification_report.json`**: Classification results
- **`atlan_tickets_classification.csv`**: CSV export format

## Error Handling

The system includes robust error handling:
- API rate limiting with exponential backoff
- Fallback classification when API calls fail
- Detailed error logging and status tracking
- Graceful degradation for failed classifications

## API Configuration

The system uses the Grok API with the following configuration:
- **Model**: gemma2-9b-it
- **API Key**: Configured in config.py
- **Rate Limiting**: Built-in delays to prevent rate limiting
- **Retry Logic**: Automatic retries for failed requests

## Example Output

```
CLASSIFICATION SUMMARY
============================================================
Total Tickets: 30
Successful Classifications: 28
Failed Classifications: 2
Success Rate: 93.3%

TOPIC DISTRIBUTION:
  Connector: 8 (26.7%)
  API/SDK: 6 (20.0%)
  Lineage: 5 (16.7%)
  How-to: 4 (13.3%)
  ...

SENTIMENT DISTRIBUTION:
  Neutral: 12 (40.0%)
  Frustrated: 8 (26.7%)
  Curious: 6 (20.0%)
  ...

PRIORITY DISTRIBUTION:
  P1 (Medium): 15 (50.0%)
  P0 (High): 10 (33.3%)
  P2 (Low): 5 (16.7%)
============================================================
```
