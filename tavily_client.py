#!/usr/bin/env python3
"""
Tavily API client for generating answers to product-related questions
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from config import TAVILY_API_KEY, TAVILY_API_URL
from grok_client import GrokClient

class TavilyClient:
    def __init__(self):
        self.api_key = TAVILY_API_KEY
        self.api_url = TAVILY_API_URL
        self.grok_client = GrokClient()
        self.knowledge_base = {
            "product": "https://docs.atlan.com/",
            "api_sdk": "https://developer.atlan.com/"
        }
    
    def optimize_query_for_tavily(self, query: str, topic: str) -> str:
        """
        Use Grok to extract key search terms from a long query for Tavily search
        """
        try:
            # Create a prompt to extract key search terms and context
            optimization_prompt = f"""
            Extract the most important search terms and context from this user query for searching Atlan documentation.
            
            User Query: "{query}"
            Topic: {topic}
            
            Please provide a comprehensive search query that includes:
            - Key technical terms specific to Atlan
            - Atlan feature names and capabilities
            - Action words and verbs
            - Context and requirements
            - Specific use cases mentioned
            - Atlan-specific terminology (data catalog, lineage, governance, etc.)
            
            Focus on Atlan-specific terms and avoid generic programming concepts.
            Make the search query detailed and specific to help find the most relevant Atlan documentation.
            Return only the search terms and context, no explanations.
            Keep it under 300 characters total.
            """
            
            # Use Grok to optimize the query
            result = self.grok_client.classify_ticket({
                'id': 'QUERY_OPT',
                'subject': 'Optimize Search Query',
                'body': optimization_prompt
            })
            
            if result.get('status') == 'success':
                # Extract the optimized query from the response
                optimized_query = result.get('classification', {}).get('reasoning', {}).get('topic_reasoning', '')
                if optimized_query and len(optimized_query) < 400:
                    return optimized_query.strip()
            
            # Fallback: truncate original query if optimization fails
            if len(query) > 400:
                return query[:397] + "..."
            return query
            
        except Exception as e:
            print(f"Error optimizing query: {e}")
            # Fallback: truncate original query
            if len(query) > 400:
                return query[:397] + "..."
            return query
    
    def search_and_answer(self, query: str, topic: str) -> Dict[str, any]:
        """
        Search for information and generate an answer based on the topic
        """
        try:
            # Optimize the query for Tavily (handle long queries)
            optimized_query = self.optimize_query_for_tavily(query, topic)
            
            # Determine the appropriate knowledge base and construct Atlan-specific search query
            if topic.lower() in ["api/sdk"]:
                knowledge_base = self.knowledge_base["api_sdk"]
                search_query = f"Atlan API SDK {optimized_query} developer documentation"
            elif topic.lower() in ["how-to", "product", "best practices", "sso"]:
                knowledge_base = self.knowledge_base["product"]
                search_query = f"Atlan {optimized_query} documentation guide tutorial"
            elif topic.lower() in ["connector", "lineage", "glossary", "sensitive data"]:
                knowledge_base = self.knowledge_base["product"]
                search_query = f"Atlan {topic} {optimized_query} data catalog governance"
            else:
                # For other topics, use a general Atlan-focused search
                knowledge_base = self.knowledge_base["product"]
                search_query = f"Atlan {optimized_query} data catalog platform"
            
            # Perform Tavily search
            search_results = self._perform_search(search_query)
            
            if not search_results["success"]:
                return search_results
            
            # Enhance the response to be more detailed and tailored
            enhanced_answer = self._enhance_response(search_results["answer"], query, topic, search_results.get("results", []))
            
            return {
                "success": True,
                "answer": enhanced_answer,
                "sources": search_results["sources"],
                "knowledge_base": knowledge_base,
                "search_query": search_query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating answer: {str(e)}"
            }
    
    def _enhance_response(self, answer: str, original_query: str, topic: str, search_results: List[Dict]) -> str:
        """
        Use Grok to enhance and tailor Tavily's response to be more specific and helpful
        """
        try:
            # Prepare context from search results
            context_info = ""
            if search_results and len(search_results) > 0:
                context_parts = []
                for i, result in enumerate(search_results[:5], 1):  # Use top 5 results
                    title = result.get('title', '')
                    content = result.get('content', '')
                    url = result.get('url', '')
                    if title and content:
                        # Extract relevant snippets (longer for better context)
                        snippet = content[:500] + "..." if len(content) > 500 else content
                        context_parts.append(f"Source {i} - {title}:\n{snippet}\nURL: {url}")
                
                if context_parts:
                    context_info = "\n\n".join(context_parts)
            
            # Create a comprehensive prompt for Grok to tailor the response
            enhancement_prompt = f"""
            You are an expert Atlan documentation assistant. A user asked: "{original_query}"
            
            Topic Category: {topic}
            
            Tavily search provided this initial answer: "{answer}"
            
            Additional context from Atlan documentation:
            {context_info}
            
            Please provide a comprehensive, well-structured response that:
            1. Directly answers the user's specific question
            2. Uses the provided context to give accurate, detailed information
            3. Includes step-by-step instructions where applicable
            4. Mentions specific Atlan features, settings, or configurations
            5. Provides practical examples or use cases
            6. Includes important considerations, prerequisites, or troubleshooting tips
            7. References specific documentation sections when relevant
            8. Is written in a helpful, professional tone
            
            Structure your response with clear headings and bullet points for easy reading.
            Focus on being actionable and specific to Atlan's platform.
            """
            
            # Use Grok to generate a tailored response
            result = self.grok_client.classify_ticket({
                'id': 'ENHANCE_RESPONSE',
                'subject': f'Enhance Response for: {original_query[:50]}...',
                'body': enhancement_prompt
            })
            
            if result.get('status') == 'success':
                # Extract the enhanced response from Grok's reasoning
                enhanced = result.get('classification', {}).get('reasoning', {}).get('topic_reasoning', '')
                if enhanced and len(enhanced) > len(answer):
                    return enhanced
                else:
                    # Fallback to summary if reasoning is not available
                    summary = result.get('summary', '')
                    if summary and len(summary) > len(answer):
                        return summary
            
            # If Grok enhancement fails, return the original answer with basic context
            if context_info:
                return f"{answer}\n\n**Additional Context:**\n{context_info[:1000]}..."
            
            return answer
            
        except Exception as e:
            print(f"Error enhancing response with Grok: {e}")
            # Fallback to original answer
            return answer
    
    def _perform_search(self, query: str) -> Dict[str, any]:
        """
        Perform Tavily search with Atlan-specific domain restrictions
        """
        try:
            # Define Atlan-specific domains to focus the search
            atlan_domains = [
                "developer.atlan.com",
                "docs.atlan.com", 
                "atlan.com",
                "help.atlan.com",
                "support.atlan.com"
            ]
            
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "advanced",
                "include_answer": True,
                "include_raw_content": True,  # Include raw content for more detailed responses
                "max_results": 8,  # Get more results for comprehensive answers
                "include_domains": atlan_domains,  # Focus on Atlan domains only
                "exclude_domains": [
                    "stackoverflow.com",
                    "quora.com", 
                    "reddit.com",
                    "medium.com",
                    "dev.to",
                    "github.com"
                ],  # Exclude generic programming sites
                "answer_style": "detailed",  # Request detailed answers
                "answer_length": "long"  # Request longer, more comprehensive answers
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                sources = [result.get("url", "") for result in results]
                answer = data.get("answer", "")
                
                # Check if we got Atlan-specific results
                atlan_sources = [s for s in sources if any(domain in s for domain in atlan_domains)]
                
                # If we don't have enough Atlan-specific results, try a broader search
                if len(atlan_sources) < 2 and len(results) > 0:
                    print(f"⚠️ Limited Atlan-specific results found. Got {len(atlan_sources)} Atlan sources out of {len(sources)} total.")
                    # Try a more specific Atlan search
                    return self._fallback_atlan_search(query)
                
                return {
                    "success": True,
                    "results": results,
                    "sources": sources,
                    "answer": answer,
                    "atlan_sources_count": len(atlan_sources)
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
    
    def _fallback_atlan_search(self, query: str) -> Dict[str, any]:
        """
        Fallback search with more specific Atlan terms when initial search doesn't return enough Atlan results
        """
        try:
            # Try a more specific Atlan search
            atlan_specific_query = f"Atlan data catalog platform {query} documentation"
            
            payload = {
                "api_key": self.api_key,
                "query": atlan_specific_query,
                "search_depth": "basic",
                "include_answer": True,
                "include_raw_content": True,
                "max_results": 5,
                "include_domains": ["developer.atlan.com", "docs.atlan.com"],
                "exclude_domains": [
                    "stackoverflow.com",
                    "quora.com", 
                    "reddit.com",
                    "medium.com",
                    "dev.to"
                ],
                "answer_style": "detailed",
                "answer_length": "medium"
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                sources = [result.get("url", "") for result in results]
                answer = data.get("answer", "")
                
                # If still no good results, provide a helpful message
                if len(sources) == 0 or not any("atlan.com" in s for s in sources):
                    answer = f"I couldn't find specific Atlan documentation for your query: '{query}'. This might be because:\n\n1. The feature you're asking about might be newer or not yet documented\n2. The terminology might be different in Atlan's documentation\n3. The feature might be available through a different name\n\nI recommend checking the official Atlan documentation at https://docs.atlan.com/ or the developer portal at https://developer.atlan.com/ for the most up-to-date information."
                    sources = ["https://docs.atlan.com/", "https://developer.atlan.com/"]
                
                return {
                    "success": True,
                    "results": results,
                    "sources": sources,
                    "answer": answer,
                    "atlan_sources_count": len([s for s in sources if "atlan.com" in s])
                }
            else:
                return {
                    "success": False,
                    "error": f"Fallback search failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error in fallback search: {str(e)}"
            }

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
