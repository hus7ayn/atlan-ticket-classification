#!/usr/bin/env python3
"""
Process all provided Atlan tickets for classification
"""

from ticket_classifier import TicketClassifier
from utils import load_tickets_data, save_csv_report, print_processing_summary
from config import DEFAULT_REPORT_FILENAME, DEFAULT_CSV_FILENAME

def main():
    """
    Main function to process all tickets
    """
    print("Atlan Ticket Classification System")
    print("=" * 50)
    
    # Load tickets data from file
    tickets_data = load_tickets_data()
    if not tickets_data:
        print("No tickets data loaded. Exiting.")
        return
    
    print(f"Processing {len(tickets_data)} tickets...")
    print()
    
    # Initialize classifier
    classifier = TicketClassifier()
    
    # Load all tickets
    classifier.load_tickets(tickets_data)
    
    # Classify all tickets
    results = classifier.classify_all_tickets()
    
    # Print summary
    classifier.print_summary()
    
    # Save detailed report
    classifier.save_report(DEFAULT_REPORT_FILENAME)
    
    # Also save a CSV-friendly format
    save_csv_report(results, DEFAULT_CSV_FILENAME)
    
    # Print processing summary
    print_processing_summary(
        total=len(tickets_data),
        successful=classifier.stats['successful_classifications'],
        failed=classifier.stats['failed_classifications']
    )
    
    print("\n" + "=" * 60)
    print("CLASSIFICATION COMPLETE!")
    print("=" * 60)
    print("Files generated:")
    print(f"- {DEFAULT_REPORT_FILENAME} (detailed JSON report)")
    print(f"- {DEFAULT_CSV_FILENAME} (CSV format for analysis)")
    print("=" * 60)

# Removed duplicate save_csv_report function - now using shared utility

if __name__ == "__main__":
    main()
