#!/usr/bin/env python3
"""
Tavily API client for generating answers to product-related questions
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from config import TAVILY_API_KEY, TAVILY_API_URL

class TavilyClient:
    def __init__(self):
        self.api_key = TAVILY_API_KEY
        self.api_url = TAVILY_API_URL
        self.knowledge_base = {
            "product": "https://docs.atlan.com/",
            "api_sdk": "https://developer.atlan.com/"
        }
    
    def search_and_answer(self, query: str, topic: str) -> Dict[str, any]:
        """
        Search for information and generate an answer based on the topic
        """
        try:
            # Determine the appropriate knowledge base
            if topic.lower() in ["api/sdk"]:
                knowledge_base = self.knowledge_base["api_sdk"]
                search_query = f"site:developer.atlan.com {query}"
            elif topic.lower() in ["how-to", "product", "best practices", "sso"]:
                knowledge_base = self.knowledge_base["product"]
                search_query = f"site:docs.atlan.com {query}"
            else:
                return {
                    "success": False,
                    "error": f"Tavily search not supported for topic: {topic}"
                }
            
            # Perform Tavily search
            search_results = self._perform_search(search_query)
            
            if not search_results["success"]:
                return search_results
            
            # Generate answer from search results
            answer = self._generate_answer(query, search_results["results"], topic)
            
            return {
                "success": True,
                "answer": answer,
                "sources": search_results["sources"],
                "knowledge_base": knowledge_base,
                "search_query": search_query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating answer: {str(e)}"
            }
    
    def _perform_search(self, query: str) -> Dict[str, any]:
        """
        Perform Tavily search
        """
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "advanced",
                "include_answer": True,
                "include_raw_content": False,
                "max_results": 5,
                "include_domains": [],
                "exclude_domains": []
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "results": data.get("results", []),
                    "sources": [result.get("url", "") for result in data.get("results", [])],
                    "answer": data.get("answer", "")
                }
            else:
                return {
                    "success": False,
                    "error": f"Tavily API error: {response.status_code} - {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Search error: {str(e)}"
            }
    
    def _generate_answer(self, query: str, results: List[Dict], topic: str) -> str:
        """
        Generate a comprehensive answer from search results
        """
        if not results:
            return f"I couldn't find specific information about '{query}' in the Atlan documentation. Please check the official documentation or contact support for more specific assistance."
        
        # Use the answer from Tavily if available
        if results and len(results) > 0:
            # Combine the most relevant results
            answer_parts = []
            
            # Add the main answer if available
            for result in results[:3]:  # Use top 3 results
                content = result.get("content", "")
                if content:
                    answer_parts.append(content)
            
            if answer_parts:
                answer = "\n\n".join(answer_parts)
                
                # Add context based on topic
                if topic.lower() == "api/sdk":
                    answer += "\n\nFor more detailed API documentation and examples, please refer to the Atlan Developer Hub."
                elif topic.lower() in ["how-to", "product", "best practices", "sso"]:
                    answer += "\n\nFor more detailed information, please refer to the Atlan Documentation."
                
                return answer
        
        return f"I found some information about '{query}' but couldn't generate a specific answer. Please refer to the sources below for more details."
    
    def get_supported_topics(self) -> List[str]:
        """
        Get list of topics that support Tavily search
        """
        return ["How-to", "Product", "Best practices", "API/SDK", "SSO"]
    
    def is_topic_supported(self, topic: str) -> bool:
        """
        Check if a topic supports Tavily search
        """
        return topic in self.get_supported_topics()

class TicketResponseGenerator:
    """
    Generates appropriate responses based on ticket classification
    """
    
    def __init__(self):
        self.tavily_client = TavilyClient()
    
    def generate_response(self, ticket_data: Dict, classification: Dict) -> Dict[str, any]:
        """
        Generate the complete response for a ticket
        """
        topic = classification.get("topic_tag", "")
        sentiment = classification.get("sentiment", "")
        priority = classification.get("priority", "")
        
        # Internal analysis view
        internal_analysis = {
            "topic": topic,
            "sentiment": sentiment,
            "priority": priority,
            "reasoning": classification.get("reasoning", {})
        }
        
        # Generate final response based on topic
        if self.tavily_client.is_topic_supported(topic):
            # Use Tavily to generate answer
            tavily_result = self.tavily_client.search_and_answer(
                f"{ticket_data.get('subject', '')} {ticket_data.get('body', '')}",
                topic
            )
            
            if tavily_result["success"]:
                final_response = {
                    "type": "tavily_answer",
                    "answer": tavily_result["answer"],
                    "sources": tavily_result["sources"],
                    "knowledge_base": tavily_result["knowledge_base"]
                }
            else:
                final_response = {
                    "type": "error",
                    "message": f"Unable to generate answer: {tavily_result.get('error', 'Unknown error')}",
                    "fallback": f"This ticket has been classified as a '{topic}' issue. Please contact support for assistance."
                }
        else:
            # Simple routing message
            final_response = {
                "type": "routing",
                "message": f"This ticket has been classified as a '{topic}' issue and routed to the appropriate team.",
                "routing_info": self._get_routing_info(topic)
            }
        
        return {
            "ticket_id": ticket_data.get("id", ""),
            "subject": ticket_data.get("subject", ""),
            "internal_analysis": internal_analysis,
            "final_response": final_response,
            "generated_at": self._get_timestamp()
        }
    
    def _get_routing_info(self, topic: str) -> Dict[str, str]:
        """
        Get routing information for different topics
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
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    """
    Test the Tavily integration
    """
    print("Testing Tavily Integration")
    print("=" * 40)
    
    # Test Tavily client
    tavily = TavilyClient()
    
    # Test supported topics
    print("Supported topics:", tavily.get_supported_topics())
    
    # Test search
    test_query = "How to connect Snowflake to Atlan"
    result = tavily.search_and_answer(test_query, "How-to")
    
    if result["success"]:
        print(f"\nQuery: {test_query}")
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Sources: {result['sources']}")
    else:
        print(f"Error: {result['error']}")
    
    # Test response generator
    print("\n" + "=" * 40)
    print("Testing Response Generator")
    
    generator = TicketResponseGenerator()
    
    test_ticket = {
        "id": "TEST-001",
        "subject": "How to set up SSO with Okta",
        "body": "I need help configuring SAML SSO with our Okta instance."
    }
    
    test_classification = {
        "topic_tag": "SSO",
        "sentiment": "Curious",
        "priority": "P1",
        "reasoning": {
            "topic_reasoning": "User asking about SSO configuration",
            "sentiment_reasoning": "User is seeking information",
            "priority_reasoning": "Standard support request"
        }
    }
    
    response = generator.generate_response(test_ticket, test_classification)
    print(f"Generated response for ticket {response['ticket_id']}")
    print(f"Internal Analysis: {response['internal_analysis']}")
    print(f"Final Response Type: {response['final_response']['type']}")

if __name__ == "__main__":
    main()
