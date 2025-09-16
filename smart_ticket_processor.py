#!/usr/bin/env python3
"""
Smart Ticket Processor that combines classification and Tavily response generation
"""

from typing import Dict, List, Optional
from ticket_classifier import TicketClassifier
from tavily_client import TicketResponseGenerator
from utils import load_tickets_data, save_processed_results, print_processing_summary
from config import DEFAULT_REPORT_FILENAME, DEFAULT_CSV_FILENAME

class SmartTicketProcessor:
    """
    Processes tickets with both classification and intelligent response generation
    """
    
    def __init__(self):
        self.classifier = TicketClassifier()
        self.response_generator = TicketResponseGenerator()
    
    def process_single_ticket(self, ticket_data: Dict) -> Dict[str, any]:
        """
        Process a single ticket with full classification and response generation
        """
        try:
            # Step 1: Classify the ticket
            print(f"Classifying ticket: {ticket_data.get('id', 'Unknown')}")
            classification_result = self.classifier.grok_client.classify_ticket(ticket_data)
            
            if classification_result.get('status') != 'success':
                return {
                    "success": False,
                    "error": "Classification failed",
                    "ticket_id": ticket_data.get('id', 'Unknown'),
                    "classification_result": classification_result
                }
            
            # Step 2: Generate intelligent response
            print(f"Generating response for ticket: {ticket_data.get('id', 'Unknown')}")
            response = self.response_generator.generate_response(
                ticket_data, 
                classification_result.get('classification', {})
            )
            
            return {
                "success": True,
                "ticket_id": ticket_data.get('id', 'Unknown'),
                "classification": classification_result,
                "response": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing error: {str(e)}",
                "ticket_id": ticket_data.get('id', 'Unknown')
            }
    
    def process_multiple_tickets(self, tickets_data: List[Dict]) -> Dict[str, any]:
        """
        Process multiple tickets
        """
        results = []
        successful = 0
        failed = 0
        
        print(f"Processing {len(tickets_data)} tickets...")
        print("=" * 50)
        
        for i, ticket in enumerate(tickets_data, 1):
            print(f"Processing ticket {i}/{len(tickets_data)}: {ticket.get('id', 'Unknown')}")
            
            result = self.process_single_ticket(ticket)
            results.append(result)
            
            if result["success"]:
                successful += 1
                print(f"  ✅ Success")
            else:
                failed += 1
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
            
            print()
        
        return {
            "total_tickets": len(tickets_data),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful / len(tickets_data) * 100):.1f}%" if tickets_data else "0%",
            "results": results
        }
    
    def process_ticket_with_query(self, query: str, ticket_id: str = None) -> Dict[str, any]:
        """
        Process a query as if it were a ticket
        """
        if not ticket_id:
            ticket_id = f"QUERY-{hash(query) % 10000}"
        
        # Create ticket data from query
        ticket_data = {
            "id": ticket_id,
            "subject": query,
            "body": query
        }
        
        return self.process_single_ticket(ticket_data)
    
    def get_supported_topics(self) -> List[str]:
        """
        Get list of topics that support Tavily search
        """
        return self.response_generator.tavily_client.get_supported_topics()
    
    def is_topic_supported(self, topic: str) -> bool:
        """
        Check if a topic supports Tavily search
        """
        return self.response_generator.tavily_client.is_topic_supported(topic)

# Removed duplicate functions - now using shared utilities

def print_response_summary(results: Dict):
    """
    Print a summary of the processed results
    """
    print("\n" + "=" * 60)
    print("SMART TICKET PROCESSING SUMMARY")
    print("=" * 60)
    
    print(f"Total Tickets: {results['total_tickets']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {results['success_rate']}")
    
    # Count by response type
    response_types = {}
    tavily_answers = 0
    routing_messages = 0
    
    for result in results['results']:
        if result['success']:
            response_type = result['response']['final_response']['type']
            response_types[response_type] = response_types.get(response_type, 0) + 1
            
            if response_type == 'tavily_answer':
                tavily_answers += 1
            elif response_type == 'routing':
                routing_messages += 1
    
    print(f"\nResponse Types:")
    print(f"  Tavily Answers: {tavily_answers}")
    print(f"  Routing Messages: {routing_messages}")
    
    # Show sample responses
    print(f"\nSample Responses:")
    sample_count = 0
    for result in results['results']:
        if result['success'] and sample_count < 3:
            ticket_id = result['ticket_id']
            topic = result['response']['internal_analysis']['topic']
            response_type = result['response']['final_response']['type']
            
            print(f"\n  {ticket_id} ({topic}):")
            if response_type == 'tavily_answer':
                answer = result['response']['final_response']['answer'][:100]
                print(f"    Answer: {answer}...")
                print(f"    Sources: {len(result['response']['final_response']['sources'])} sources")
            else:
                print(f"    Message: {result['response']['final_response']['message']}")
            
            sample_count += 1

def main():
    """
    Main function to demonstrate the smart ticket processor
    """
    print("Smart Ticket Processor with Tavily Integration")
    print("=" * 60)
    
    # Initialize processor
    processor = SmartTicketProcessor()
    
    # Load tickets data
    tickets_data = load_tickets_data()
    if not tickets_data:
        print("No tickets data loaded. Exiting.")
        return
    
    # Process all tickets
    results = processor.process_multiple_tickets(tickets_data)
    
    # Print summary
    print_response_summary(results)
    
    # Save results
    save_processed_results(results)
    
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE!")
    print("=" * 60)
    print("Files generated:")
    print("- smart_ticket_results.json (complete results with responses)")
    print(f"- {DEFAULT_REPORT_FILENAME} (classification only)")
    print(f"- {DEFAULT_CSV_FILENAME} (CSV format)")

def test_single_query():
    """
    Test function for single query processing
    """
    print("Testing Single Query Processing")
    print("=" * 40)
    
    processor = SmartTicketProcessor()
    
    # Test queries
    test_queries = [
        "How to connect Snowflake to Atlan?",
        "What are the API authentication methods?",
        "How to set up SSO with Okta?",
        "My connector is failing to crawl data"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = processor.process_ticket_with_query(query)
        
        if result['success']:
            topic = result['response']['internal_analysis']['topic']
            response_type = result['response']['final_response']['type']
            print(f"  Topic: {topic}")
            print(f"  Response Type: {response_type}")
            
            if response_type == 'tavily_answer':
                answer = result['response']['final_response']['answer'][:150]
                print(f"  Answer: {answer}...")
            else:
                print(f"  Message: {result['response']['final_response']['message']}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_single_query()
    else:
        main()
