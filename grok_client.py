import requests
import json
import time
from typing import Dict, Any, Optional
from config import GROK_API_KEY, GROK_MODEL, GROK_API_URL

class GrokClient:
    def __init__(self):
        self.api_key = GROK_API_KEY
        self.model = GROK_MODEL
        self.api_url = GROK_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def classify_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a single ticket for topic, sentiment, and priority
        """
        try:
            # Create the classification prompt
            prompt = self._create_classification_prompt(ticket_data)
            
            # Make API call to Grok
            response = self._make_api_call(prompt)
            
            if response:
                return self._parse_classification_response(response, ticket_data)
            else:
                return self._create_fallback_classification(ticket_data)
                
        except Exception as e:
            print(f"Error classifying ticket {ticket_data.get('id', 'unknown')}: {str(e)}")
            return self._create_fallback_classification(ticket_data)
    
    def _create_classification_prompt(self, ticket_data: Dict[str, Any]) -> str:
        """
        Create a comprehensive prompt for ticket classification
        """
        subject = ticket_data.get('subject', '')
        body = ticket_data.get('body', '')
        
        prompt = f"""
You are an expert ticket classification system for Atlan support tickets. Analyze the following ticket and classify it into three categories:

TICKET DATA:
Subject: {subject}
Body: {body}

CLASSIFICATION REQUIREMENTS:

1. TOPIC TAGS (choose the most relevant ONE):
   - How-to: Questions about how to use features
   - Product: General product questions or feature requests
   - Connector: Issues with data source connections
   - Lineage: Questions about data lineage features
   - API/SDK: Technical questions about APIs or SDKs
   - SSO: Single Sign-On authentication issues
   - Glossary: Business glossary and metadata questions
   - Best practices: Questions about recommended approaches
   - Sensitive data: PII, security, or compliance questions

2. SENTIMENT (choose the most appropriate ONE):
   - Frustrated: User is clearly frustrated or blocked
   - Curious: User is asking exploratory questions
   - Angry: User is expressing anger or strong dissatisfaction
   - Neutral: User is matter-of-fact or professional
   - Positive: User is expressing satisfaction or enthusiasm
   - Concerned: User is worried about something but not angry

3. PRIORITY (choose the most appropriate ONE):
   - P0 (High): Critical issues, blocking work, urgent deadlines
   - P1 (Medium): Important but not blocking, standard support needs
   - P2 (Low): General questions, feature requests, non-urgent

RESPONSE FORMAT (return ONLY valid JSON):
{{
    "topic_tag": "selected_topic_tag",
    "sentiment": "selected_sentiment",
    "priority": "selected_priority",
    "reasoning": {{
        "topic_reasoning": "Brief explanation for topic selection",
        "sentiment_reasoning": "Brief explanation for sentiment selection", 
        "priority_reasoning": "Brief explanation for priority selection"
    }}
}}
"""
        return prompt
    
    def _make_api_call(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Make API call to Grok with retry logic
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"API error: {response.status_code} - {response.text}")
                    if attempt == max_retries - 1:
                        return None
                    time.sleep(1)
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error: {str(e)}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(1)
        
        return None
    
    def _parse_classification_response(self, response: Dict[str, Any], ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the Grok API response and extract classification
        """
        try:
            content = response['choices'][0]['message']['content']
            
            # Try to extract JSON from the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                classification = json.loads(json_str)
                
                # Validate the classification
                if self._validate_classification(classification):
                    return {
                        'ticket_id': ticket_data.get('id', 'unknown'),
                        'subject': ticket_data.get('subject', ''),
                        'classification': classification,
                        'status': 'success'
                    }
            
            # If JSON parsing fails, try to extract information manually
            return self._extract_classification_manually(content, ticket_data)
            
        except Exception as e:
            print(f"Error parsing response: {str(e)}")
            return self._create_fallback_classification(ticket_data)
    
    def _extract_classification_manually(self, content: str, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manually extract classification from text response
        """
        from config import TOPIC_TAGS, SENTIMENT_OPTIONS, PRIORITY_LEVELS
        
        # Simple keyword-based extraction as fallback
        content_lower = content.lower()
        
        # Topic extraction
        topic = "Product"  # default
        for tag in TOPIC_TAGS:
            if tag.lower() in content_lower:
                topic = tag
                break
        
        # Sentiment extraction
        sentiment = "Neutral"  # default
        if any(word in content_lower for word in ['frustrated', 'frustrating', 'blocked', 'urgent']):
            sentiment = "Frustrated"
        elif any(word in content_lower for word in ['angry', 'infuriating', 'huge problem']):
            sentiment = "Angry"
        elif any(word in content_lower for word in ['curious', 'explore', 'understand']):
            sentiment = "Curious"
        elif any(word in content_lower for word in ['concerned', 'worried', 'security']):
            sentiment = "Concerned"
        
        # Priority extraction
        priority = "P1 (Medium)"  # default
        if any(word in content_lower for word in ['urgent', 'critical', 'blocking', 'asap', 'p0']):
            priority = "P0 (High)"
        elif any(word in content_lower for word in ['low', 'p2', 'general']):
            priority = "P2 (Low)"
        
        return {
            'ticket_id': ticket_data.get('id', 'unknown'),
            'subject': ticket_data.get('subject', ''),
            'classification': {
                'topic_tag': topic,
                'sentiment': sentiment,
                'priority': priority,
                'reasoning': {
                    'topic_reasoning': 'Extracted from content keywords',
                    'sentiment_reasoning': 'Extracted from content keywords',
                    'priority_reasoning': 'Extracted from content keywords'
                }
            },
            'status': 'fallback'
        }
    
    def _validate_classification(self, classification: Dict[str, Any]) -> bool:
        """
        Validate that the classification contains required fields
        """
        required_fields = ['topic_tag', 'sentiment', 'priority']
        return all(field in classification for field in required_fields)
    
    def _create_fallback_classification(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a fallback classification when API fails
        """
        return {
            'ticket_id': ticket_data.get('id', 'unknown'),
            'subject': ticket_data.get('subject', ''),
            'classification': {
                'topic_tag': 'Product',
                'sentiment': 'Neutral',
                'priority': 'P1 (Medium)',
                'reasoning': {
                    'topic_reasoning': 'Default classification due to API error',
                    'sentiment_reasoning': 'Default classification due to API error',
                    'priority_reasoning': 'Default classification due to API error'
                }
            },
            'status': 'error'
        }
