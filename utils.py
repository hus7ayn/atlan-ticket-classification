#!/usr/bin/env python3
"""
Shared utilities for the Atlan Ticket Classification System
"""

import json
import csv
from typing import List, Dict, Any

# Standardized filenames
DEFAULT_REPORT_FILENAME = "atlan_tickets_classification_report.json"
DEFAULT_CSV_FILENAME = "atlan_tickets_classification.csv"
DEFAULT_TICKETS_FILENAME = "tickets_data.json"

def load_tickets_data(filename: str = DEFAULT_TICKETS_FILENAME) -> List[Dict[str, Any]]:
    """
    Load tickets data from JSON file
    
    Args:
        filename: Path to the JSON file containing ticket data
        
    Returns:
        List of ticket dictionaries
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found. Please ensure the tickets data file exists.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filename}: {e}")
        return []
    except Exception as e:
        print(f"Error loading tickets data: {e}")
        return []

def save_tickets_data(tickets: List[Dict[str, Any]], filename: str = DEFAULT_TICKETS_FILENAME) -> bool:
    """
    Save tickets data to JSON file
    
    Args:
        tickets: List of ticket dictionaries
        filename: Path to save the JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tickets, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving tickets data: {e}")
        return False

def save_csv_report(results: List[Dict[str, Any]], filename: str = DEFAULT_CSV_FILENAME) -> bool:
    """
    Save classification results in CSV format for easy analysis
    
    Args:
        results: List of classification results
        filename: Path to save the CSV file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ticket_id', 'subject', 'topic_tag', 'sentiment', 'priority', 'status', 'topic_reasoning', 'sentiment_reasoning', 'priority_reasoning']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                classification = result.get('classification', {})
                reasoning = classification.get('reasoning', {})
                
                row = {
                    'ticket_id': result.get('ticket_id', 'N/A'),
                    'subject': result.get('subject', 'N/A'),
                    'topic_tag': classification.get('topic_tag', 'N/A'),
                    'sentiment': classification.get('sentiment', 'N/A'),
                    'priority': classification.get('priority', 'N/A'),
                    'status': result.get('status', 'N/A'),
                    'topic_reasoning': reasoning.get('topic_reasoning', 'N/A'),
                    'sentiment_reasoning': reasoning.get('sentiment_reasoning', 'N/A'),
                    'priority_reasoning': reasoning.get('priority_reasoning', 'N/A')
                }
                writer.writerow(row)
        
        print(f"CSV report saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving CSV report: {e}")
        return False

def print_processing_summary(total: int, successful: int, failed: int) -> None:
    """
    Print a standardized processing summary
    
    Args:
        total: Total number of items processed
        successful: Number of successful operations
        failed: Number of failed operations
    """
    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total Items: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(successful / total * 100):.1f}%" if total > 0 else "0%")
    print("=" * 60)

def validate_ticket_data(ticket: Dict[str, Any]) -> bool:
    """
    Validate that a ticket has required fields
    
    Args:
        ticket: Ticket dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['id', 'subject', 'body']
    return all(field in ticket and ticket[field] for field in required_fields)

def get_supported_topics() -> List[str]:
    """
    Get list of supported topic tags
    
    Returns:
        List of supported topic names
    """
    return [
        "How-to", "Product", "Connector", "Lineage", "API/SDK", 
        "SSO", "Glossary", "Best practices", "Sensitive data"
    ]

def get_sentiment_options() -> List[str]:
    """
    Get list of supported sentiment options
    
    Returns:
        List of supported sentiment names
    """
    return [
        "Frustrated", "Curious", "Angry", "Neutral", "Positive", "Concerned"
    ]

def get_priority_levels() -> List[str]:
    """
    Get list of supported priority levels
    
    Returns:
        List of supported priority names
    """
    return ["P0", "P1", "P2"]

def save_processed_results(results: Dict, filename: str = "smart_ticket_results.json") -> bool:
    """
    Save processed results to file
    
    Args:
        results: Dictionary containing processed results
        filename: Path to save the results file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving results: {e}")
        return False
