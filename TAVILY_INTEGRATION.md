# Tavily Integration for Smart Ticket Processing

## Overview

This system integrates Tavily search API to provide intelligent responses to ticket queries. When a ticket is classified as a supported topic, the system uses Tavily to search Atlan's documentation and generate direct answers with proper source citations.

## Features

### Supported Topics for Tavily Search
- **How-to**: Step-by-step instructions and guides
- **Product**: Product features and capabilities
- **Best practices**: Recommended approaches and methodologies
- **API/SDK**: Technical API documentation and examples
- **SSO**: Single Sign-On configuration and setup

### Knowledge Base Sources
- **Product Documentation**: https://docs.atlan.com/
- **Developer Hub**: https://developer.atlan.com/

## Architecture

### Core Components

1. **`tavily_client.py`**: Direct Tavily API integration
2. **`smart_ticket_processor.py`**: Combines classification and response generation
3. **`ticket_api.py`**: API layer for frontend integration

### Data Flow

```
Ticket Query → Classification → Topic Check → Tavily Search → Response Generation
```

## API Configuration

### Environment Variables
```bash
TAVILY_API_KEY=your_tavily_api_key_here
```

### API Key Storage
- Stored in `config.py` with environment variable fallback
- Never hardcoded in the application code
- Can be overridden via `.env` file

## Usage Examples

### 1. Process Single Query

```python
from ticket_api import TicketAPI

api = TicketAPI()
result = api.process_query("How to connect Snowflake to Atlan?")

if result['success']:
    print(f"Topic: {result['internal_analysis']['topic']}")
    print(f"Response Type: {result['final_response']['type']}")
    if result['final_response']['type'] == 'ai_answer':
        print(f"Answer: {result['final_response']['answer']}")
        print(f"Sources: {result['final_response']['sources']}")
```

### 2. Process Ticket Data

```python
ticket_data = {
    "id": "TICKET-001",
    "subject": "API authentication methods",
    "body": "What authentication methods are supported for the Atlan API?"
}

result = api.classify_and_respond(ticket_data)
```

### 3. Check Topic Support

```python
# Check if topic supports Tavily search
if api.is_topic_supported("API/SDK"):
    print("This topic will generate Tavily answers")
else:
    print("This topic will be routed to appropriate team")
```

## Response Types

### 1. Tavily Answer (AI-Generated)
```json
{
  "type": "ai_answer",
  "answer": "Detailed answer from documentation...",
  "sources": [
    "https://docs.atlan.com/api/authentication",
    "https://developer.atlan.com/guides/auth"
  ],
  "knowledge_base": "https://developer.atlan.com/",
  "has_sources": true
}
```

### 2. Routing Message
```json
{
  "type": "routing",
  "message": "This ticket has been classified as a 'Connector' issue and routed to the appropriate team.",
  "routing_info": {
    "team": "Technical Support Team - Database Connections",
    "category": "Connector",
    "priority": "High"
  }
}
```

## Frontend Integration

### Internal Analysis View
Display the AI's classification analysis:
- **Topic**: Classified topic (e.g., "API/SDK", "Connector")
- **Sentiment**: User sentiment (e.g., "Curious", "Frustrated")
- **Priority**: Ticket priority (e.g., "P1", "P0")
- **Reasoning**: AI's reasoning for each classification

### Final Response View
Display the appropriate response based on topic:

#### For Supported Topics (Tavily Search)
- Show the AI-generated answer
- Display source URLs with proper citations
- Indicate which knowledge base was used
- Provide links to relevant documentation

#### For Other Topics (Routing)
- Show routing message
- Display team assignment
- Show priority level
- Provide contact information

## Error Handling

### Common Error Scenarios
1. **Tavily API Failure**: Falls back to routing message
2. **Classification Failure**: Returns error with fallback
3. **Invalid Query**: Returns appropriate error message
4. **Network Issues**: Implements retry logic

### Error Response Format
```json
{
  "status": "error",
  "message": "Unable to process request: API timeout",
  "ticket_id": "TICKET-001"
}
```

## Testing

### Run Tests
```bash
# Test Tavily integration
python tavily_client.py

# Test smart processor
python smart_ticket_processor.py test

# Test API
python ticket_api.py
```

### Test Queries
- "How to connect Snowflake to Atlan?" → Connector (Routing)
- "What are the API authentication methods?" → API/SDK (Tavily)
- "How to set up SSO with Okta?" → SSO (Tavily)
- "My connector is failing" → Connector (Routing)

## Performance Considerations

### Response Times
- **Tavily Search**: 2-5 seconds average
- **Classification**: 1-2 seconds average
- **Total Processing**: 3-7 seconds per ticket

### Rate Limiting
- Tavily API has rate limits
- Implemented retry logic with exponential backoff
- Consider caching for frequently asked questions

### Caching Strategy
- Cache common queries and responses
- Implement TTL-based cache invalidation
- Store responses with source URLs for consistency

## Security Considerations

### API Key Protection
- Never log API keys
- Use environment variables
- Implement key rotation strategy
- Monitor API usage

### Data Privacy
- Don't store sensitive ticket content
- Implement data retention policies
- Log only necessary information
- Ensure GDPR compliance

## Future Enhancements

### Planned Features
1. **Response Caching**: Cache common answers for faster responses
2. **Multi-language Support**: Support for different languages
3. **Custom Knowledge Bases**: Add more documentation sources
4. **Response Quality Scoring**: Rate answer quality and improve
5. **User Feedback Integration**: Learn from user feedback

### Integration Opportunities
1. **Slack Integration**: Direct ticket processing in Slack
2. **Email Integration**: Process email tickets automatically
3. **Webhook Support**: Real-time ticket processing
4. **Analytics Dashboard**: Track response quality and usage

## Troubleshooting

### Common Issues

#### Tavily API Errors
```bash
# Check API key
echo $TAVILY_API_KEY

# Test API connection
python -c "from tavily_client import TavilyClient; TavilyClient().search_and_answer('test', 'How-to')"
```

#### Classification Errors
```bash
# Test classification
python -c "from ticket_classifier import TicketClassifier; TicketClassifier().grok_client.classify_ticket({'id': 'test', 'subject': 'test', 'body': 'test'})"
```

#### Response Generation Issues
```bash
# Test full pipeline
python smart_ticket_processor.py test
```

## Support

For issues with the Tavily integration:
1. Check API key configuration
2. Verify network connectivity
3. Review error logs
4. Test with simple queries first
5. Contact support if issues persist

---

**Note**: This integration is designed for future frontend implementation. The current system provides a solid foundation for building a comprehensive ticket processing and response system.
