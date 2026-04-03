# Example Inputs

Use these sample requirement texts to quickly test the UI and API.

## Example 1: Smart Vending Machine

System Overview:
A smart vending machine deployed in public areas. Internal software and hardware logic are not visible to the tester. Testing is based only on observable behavior and requirements.

Functional Requirements:
- Item categories: Drinks ($1.50-$3.00), Snacks ($2.00-$4.50), Hot food ($5.00-$10.00).
- Payment methods: coins ($0.10, $0.25, $0.50, $1.00) and banknotes ($5.00, $10.00).
- Payment constraints: total inserted must be >= item price; change returned up to $5.00; reject if change > $5.00.
- Inventory constraints: an item may become out of stock during payment.

## Example 2: Library Borrowing

System Overview:
A library system allows users to borrow and return books through a kiosk. Users authenticate with a library card.

Functional Requirements:
- Users can borrow at most 5 books at the same time.
- A loan period is 30 days; overdue books incur a daily fine of $0.50.
- Books marked as "Reference" cannot be borrowed.
- Users with unpaid fines over $10.00 cannot borrow new books.

## Example 3: Ticket Booking

System Overview:
A ticket booking site sells concert tickets. Users select a show, seat category, and payment method.

Functional Requirements:
- Seat categories: Standard ($50-$80), Premium ($100-$150), VIP ($200-$300).
- Each booking can include 1-6 tickets.
- Payment methods: credit card or mobile wallet.
- Booking is rejected if total price exceeds $1,000.
- Refunds allowed within 24 hours after purchase.
