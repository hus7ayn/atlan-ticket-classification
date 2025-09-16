#!/usr/bin/env python3
"""
API endpoints for ticket processing (for future frontend integration)
"""

import json
from typing import Dict, List, Optional
from smart_ticket_processor import SmartTicketProcessor

class TicketAPI:
    """
    API class for ticket processing operations
    """
    
    def __init__(self):
        self.processor = SmartTicketProcessor()
    
    def classify_and_respond(self, ticket_data: Dict) -> Dict[str, any]:
        """
        Classify a ticket and generate appropriate response
        
        Args:
            ticket_data: Dictionary with 'id', 'subject', 'body'
        
        Returns:
            Dictionary with classification and response
        """
        try:
            result = self.processor.process_single_ticket(ticket_data)
            
            if result['success']:
                return {
                    "success": True,
                    "ticket_id": result['ticket_id'],
                    "internal_analysis": result['response']['internal_analysis'],
                    "final_response": result['response']['final_response'],
                    "generated_at": result['response']['generated_at']
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Unknown error'),
                    "ticket_id": result.get('ticket_id', 'Unknown')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"API error: {str(e)}",
                "ticket_id": ticket_data.get('id', 'Unknown')
            }
    
    def process_query(self, query: str, ticket_id: str = None) -> Dict[str, any]:
        """
        Process a query as if it were a ticket
        
        Args:
            query: The user's question or query
            ticket_id: Optional ticket ID (will be generated if not provided)
        
        Returns:
            Dictionary with classification and response
        """
        try:
            result = self.processor.process_ticket_with_query(query, ticket_id)
            
            if result['success']:
                return {
                    "success": True,
                    "ticket_id": result['ticket_id'],
                    "query": query,
                    "internal_analysis": result['response']['internal_analysis'],
                    "final_response": result['response']['final_response'],
                    "generated_at": result['response']['generated_at']
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Unknown error'),
                    "query": query
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"API error: {str(e)}",
                "query": query
            }
    
    def get_supported_topics(self) -> List[str]:
        """
        Get list of topics that support Tavily search
        
        Returns:
            List of supported topic names
        """
        return self.processor.get_supported_topics()
    
    def is_topic_supported(self, topic: str) -> bool:
        """
        Check if a topic supports Tavily search
        
        Args:
            topic: Topic name to check
        
        Returns:
            True if topic is supported, False otherwise
        """
        return self.processor.is_topic_supported(topic)
    
    def get_topic_routing_info(self, topic: str) -> Dict[str, str]:
        """
        Get routing information for a topic
        
        Args:
            topic: Topic name
        
        Returns:
            Dictionary with routing information
        """
        routing_map = {
            "Connector": "Technical Support Team - Database Connections",
            "Lineage": "Data Engineering Team - Data Lineage", 
            "Glossary": "Data Governance Team - Metadata Management",
            "Sensitive data": "Security Team - Data Privacy & Compliance",
            "Product": "Product Team - Feature Requests"
        }
        
        return {
            "team": routing_map.get(topic, "General Support Team"),
            "category": topic,
            "priority": "High" if topic in ["Sensitive data", "Connector"] else "Medium"
        }

def create_frontend_response(api_result: Dict) -> Dict[str, any]:
    """
    Format API result for frontend consumption
    
    Args:
        api_result: Result from TicketAPI methods
    
    Returns:
        Formatted response for frontend
    """
    if not api_result['success']:
        return {
            "status": "error",
            "message": api_result.get('error', 'Unknown error'),
            "ticket_id": api_result.get('ticket_id', 'Unknown')
        }
    
    internal_analysis = api_result['internal_analysis']
    final_response = api_result['final_response']
    
    # Format internal analysis for frontend
    frontend_internal = {
        "classification": {
            "topic": internal_analysis['topic'],
            "sentiment": internal_analysis['sentiment'],
            "priority": internal_analysis['priority']
        },
        "reasoning": internal_analysis['reasoning']
    }
    
    # Format final response for frontend
    if final_response['type'] == 'tavily_answer':
        frontend_final = {
            "type": "ai_answer",
            "answer": final_response['answer'],
            "sources": final_response['sources'],
            "knowledge_base": final_response['knowledge_base'],
            "has_sources": len(final_response['sources']) > 0
        }
    elif final_response['type'] == 'routing':
        frontend_final = {
            "type": "routing",
            "message": final_response['message'],
            "routing_info": final_response['routing_info']
        }
    else:
        frontend_final = {
            "type": "error",
            "message": final_response.get('message', 'Unable to process request')
        }
    
    return {
        "status": "success",
        "ticket_id": api_result['ticket_id'],
        "internal_analysis": frontend_internal,
        "final_response": frontend_final,
        "generated_at": api_result['generated_at']
    }

def main():
    """
    Test the API functionality
    """
    print("Testing Ticket API")
    print("=" * 40)
    
    api = TicketAPI()
    
    # Test supported topics
    print("Supported topics for Tavily search:")
    for topic in api.get_supported_topics():
        print(f"  - {topic}")
    
    print("\n" + "=" * 40)
    
    # Test query processing
    test_queries = [
        "How to connect Snowflake to Atlan?",
        "What are the API authentication methods?",
        "My connector is failing to crawl data"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: {query}")
        result = api.process_query(query)
        frontend_response = create_frontend_response(result)
        
        print(f"  Status: {frontend_response['status']}")
        if frontend_response['status'] == 'success':
            classification = frontend_response['internal_analysis']['classification']
            print(f"  Topic: {classification['topic']}")
            print(f"  Sentiment: {classification['sentiment']}")
            print(f"  Priority: {classification['priority']}")
            print(f"  Response Type: {frontend_response['final_response']['type']}")
        else:
            print(f"  Error: {frontend_response['message']}")

if __name__ == "__main__":
    main()
