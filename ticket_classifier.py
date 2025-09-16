#!/usr/bin/env python3
"""
Atlan Ticket Classification System using Grok LLM
Classifies support tickets by topic, sentiment, and priority
"""

import json
import time
from typing import List, Dict, Any
from grok_client import GrokClient
from config import TOPIC_TAGS, SENTIMENT_OPTIONS, PRIORITY_LEVELS

class TicketClassifier:
    def __init__(self):
        self.grok_client = GrokClient()
        self.results = []
        self.stats = {
            'total_tickets': 0,
            'successful_classifications': 0,
            'failed_classifications': 0,
            'topic_distribution': {},
            'sentiment_distribution': {},
            'priority_distribution': {}
        }
    
    def load_tickets(self, tickets_data: List[Dict[str, Any]]) -> None:
        """
        Load tickets for classification
        """
        self.tickets = tickets_data
        self.stats['total_tickets'] = len(tickets_data)
        print(f"Loaded {len(tickets_data)} tickets for classification")
    
    def classify_all_tickets(self) -> List[Dict[str, Any]]:
        """
        Classify all loaded tickets
        """
        print("Starting ticket classification...")
        print("=" * 50)
        
        for i, ticket in enumerate(self.tickets, 1):
            print(f"Processing ticket {i}/{len(self.tickets)}: {ticket.get('id', 'unknown')}")
            
            # Classify the ticket
            result = self.grok_client.classify_ticket(ticket)
            self.results.append(result)
            
            # Update statistics
            self._update_stats(result)
            
            # Print progress
            classification = result.get('classification', {})
            print(f"  → Topic: {classification.get('topic_tag', 'N/A')}")
            print(f"  → Sentiment: {classification.get('sentiment', 'N/A')}")
            print(f"  → Priority: {classification.get('priority', 'N/A')}")
            print(f"  → Status: {result.get('status', 'unknown')}")
            print()
            
            # Add small delay to avoid rate limiting
            time.sleep(0.5)
        
        print("Classification completed!")
        return self.results
    
    def _update_stats(self, result: Dict[str, Any]) -> None:
        """
        Update classification statistics
        """
        if result.get('status') == 'success':
            self.stats['successful_classifications'] += 1
        else:
            self.stats['failed_classifications'] += 1
        
        classification = result.get('classification', {})
        
        # Update topic distribution
        topic = classification.get('topic_tag', 'Unknown')
        self.stats['topic_distribution'][topic] = self.stats['topic_distribution'].get(topic, 0) + 1
        
        # Update sentiment distribution
        sentiment = classification.get('sentiment', 'Unknown')
        self.stats['sentiment_distribution'][sentiment] = self.stats['sentiment_distribution'].get(sentiment, 0) + 1
        
        # Update priority distribution
        priority = classification.get('priority', 'Unknown')
        self.stats['priority_distribution'][priority] = self.stats['priority_distribution'].get(priority, 0) + 1
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive classification report
        """
        report = {
            'summary': {
                'total_tickets': self.stats['total_tickets'],
                'successful_classifications': self.stats['successful_classifications'],
                'failed_classifications': self.stats['failed_classifications'],
                'success_rate': f"{(self.stats['successful_classifications'] / self.stats['total_tickets'] * 100):.1f}%" if self.stats['total_tickets'] > 0 else "0%"
            },
            'distributions': {
                'topics': self.stats['topic_distribution'],
                'sentiments': self.stats['sentiment_distribution'],
                'priorities': self.stats['priority_distribution']
            },
            'detailed_results': self.results
        }
        
        return report
    
    def save_report(self, filename: str = None) -> None:
        """
        Save classification report to file
        """
        if filename is None:
            from config import DEFAULT_REPORT_FILENAME
            filename = DEFAULT_REPORT_FILENAME
            
        report = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Report saved to {filename}")
    
    def print_summary(self) -> None:
        """
        Print a summary of classification results
        """
        print("\n" + "=" * 60)
        print("CLASSIFICATION SUMMARY")
        print("=" * 60)
        
        print(f"Total Tickets: {self.stats['total_tickets']}")
        print(f"Successful Classifications: {self.stats['successful_classifications']}")
        print(f"Failed Classifications: {self.stats['failed_classifications']}")
        print(f"Success Rate: {(self.stats['successful_classifications'] / self.stats['total_tickets'] * 100):.1f}%")
        
        print("\nTOPIC DISTRIBUTION:")
        for topic, count in sorted(self.stats['topic_distribution'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.stats['total_tickets'] * 100) if self.stats['total_tickets'] > 0 else 0
            print(f"  {topic}: {count} ({percentage:.1f}%)")
        
        print("\nSENTIMENT DISTRIBUTION:")
        for sentiment, count in sorted(self.stats['sentiment_distribution'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.stats['total_tickets'] * 100) if self.stats['total_tickets'] > 0 else 0
            print(f"  {sentiment}: {count} ({percentage:.1f}%)")
        
        print("\nPRIORITY DISTRIBUTION:")
        for priority, count in sorted(self.stats['priority_distribution'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.stats['total_tickets'] * 100) if self.stats['total_tickets'] > 0 else 0
            print(f"  {priority}: {count} ({percentage:.1f}%)")
        
        print("=" * 60)

def main_classification_only():
    """
    Main function to run basic ticket classification only
    Note: This is a utility function for testing classification only.
    For full processing, use process_all_tickets.py or smart_ticket_processor.py
    """
    from utils import load_tickets_data
    
    print("Basic Ticket Classification (Classification Only)")
    print("=" * 50)
    print("Note: For full processing with responses, use process_all_tickets.py")
    print()
    
    # Load tickets data from file
    tickets_data = load_tickets_data()
    if not tickets_data:
        print("No tickets data loaded. Exiting.")
        return
    
    # Initialize classifier
    classifier = TicketClassifier()
    
    # Load tickets
    classifier.load_tickets(tickets_data)
    
    # Classify all tickets
    results = classifier.classify_all_tickets()
    
    # Print summary
    classifier.print_summary()
    
    # Save report
    classifier.save_report()
    
    print(f"\nClassification complete! Check '{classifier.save_report.__defaults__[0] if classifier.save_report.__defaults__ else 'atlan_tickets_classification_report.json'}' for detailed results.")

if __name__ == "__main__":
    main_classification_only()
