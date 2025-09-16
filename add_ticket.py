#!/usr/bin/env python3
"""
Add new tickets to the tickets_data.json file
"""

from utils import load_tickets_data, save_tickets_data, validate_ticket_data
from config import DEFAULT_TICKETS_FILENAME

DATA_FILE = DEFAULT_TICKETS_FILENAME

def add_ticket(ticket_id, subject, body):
    """Add a new ticket to the data file"""
    tickets = load_tickets_data(DATA_FILE)
    
    # Validate ticket data
    new_ticket = {
        "id": ticket_id,
        "subject": subject,
        "body": body
    }
    
    if not validate_ticket_data(new_ticket):
        print("Error: Invalid ticket data. All fields (id, subject, body) are required.")
        return False
    
    # Check if ticket ID already exists
    for ticket in tickets:
        if ticket['id'] == ticket_id:
            print(f"Error: Ticket {ticket_id} already exists!")
            return False
    
    # Add to list
    tickets.append(new_ticket)
    
    # Save to file
    if save_tickets_data(tickets, DATA_FILE):
        print(f"Successfully added ticket {ticket_id}")
        print(f"Total tickets: {len(tickets)}")
        return True
    else:
        print("Error: Failed to save ticket data")
        return False

def add_multiple_tickets(tickets_list):
    """Add multiple tickets at once"""
    existing_tickets = load_tickets_data(DATA_FILE)
    new_tickets = []
    
    for ticket in tickets_list:
        # Validate ticket data
        if not validate_ticket_data(ticket):
            print(f"Warning: Invalid ticket data for {ticket.get('id', 'unknown')}, skipping...")
            continue
            
        # Check if ticket ID already exists
        ticket_exists = any(t['id'] == ticket['id'] for t in existing_tickets)
        if not ticket_exists:
            new_tickets.append(ticket)
        else:
            print(f"Warning: Ticket {ticket['id']} already exists, skipping...")
    
    if new_tickets:
        all_tickets = existing_tickets + new_tickets
        if save_tickets_data(all_tickets, DATA_FILE):
            print(f"Successfully added {len(new_tickets)} new tickets")
            print(f"Total tickets: {len(all_tickets)}")
        else:
            print("Error: Failed to save ticket data")
    else:
        print("No new tickets to add")

def interactive_add_ticket():
    """Interactive mode to add a single ticket"""
    print("Add New Ticket")
    print("=" * 30)
    
    ticket_id = input("Enter ticket ID (e.g., TICKET-275): ").strip()
    if not ticket_id:
        print("Error: Ticket ID is required")
        return
    
    subject = input("Enter ticket subject: ").strip()
    if not subject:
        print("Error: Subject is required")
        return
    
    print("Enter ticket body (press Enter twice when done):")
    body_lines = []
    while True:
        line = input()
        if line == "" and len(body_lines) > 0 and body_lines[-1] == "":
            break
        body_lines.append(line)
    
    body = "\n".join(body_lines).strip()
    if not body:
        print("Error: Body is required")
        return
    
    add_ticket(ticket_id, subject, body)

def main():
    """Main function"""
    print("Atlan Ticket Data Manager")
    print("=" * 30)
    print("1. Add single ticket (interactive)")
    print("2. Add multiple tickets (from code)")
    print("3. View all tickets")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        interactive_add_ticket()
    elif choice == "2":
        print("\nTo add multiple tickets, modify the add_multiple_tickets() function")
        print("or use the add_ticket() function in your code.")
    elif choice == "3":
        tickets = load_tickets_data(DATA_FILE)
        print(f"\nTotal tickets: {len(tickets)}")
        for ticket in tickets:
            print(f"- {ticket['id']}: {ticket['subject']}")
    elif choice == "4":
        print("Goodbye!")
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
