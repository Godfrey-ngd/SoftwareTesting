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

Suggested techniques:
- ep_bva
- decision_table
- state_transition

## Example 2: Library Borrowing

System Overview:
A library system allows users to borrow and return books through a kiosk. Users authenticate with a library card.

Functional Requirements:
- Users can borrow at most 5 books at the same time.
- A loan period is 30 days; overdue books incur a daily fine of $0.50.
- Books marked as "Reference" cannot be borrowed.
- Users with unpaid fines over $10.00 cannot borrow new books.

Suggested techniques:
- ep_bva
- decision_table
- state_transition

## Example 3: Ticket Booking

System Overview:
A ticket booking site sells concert tickets. Users select a show, seat category, and payment method.

Functional Requirements:
- Seat categories: Standard ($50-$80), Premium ($100-$150), VIP ($200-$300).
- Each booking can include 1-6 tickets.
- Payment methods: credit card or mobile wallet.
- Booking is rejected if total price exceeds $1,000.
- Refunds allowed within 24 hours after purchase.

Suggested techniques:
- ep_bva
- decision_table
- combinatorial

## Example 4: Codebase Context (API Snippet)

Use this example with:
- input_type: `codebase`
- technique: `decision_table` (or `ep_bva`)

Code/Docs Context:

```text
Endpoint: POST /checkout
Fields:
- item_price: decimal, required, must be between 1.00 and 999.99
- quantity: int, required, must be between 1 and 6
- coupon_code: string, optional, if provided must match regex ^[A-Z0-9]{6}$
- payment_method: enum {card, wallet}
Rules:
- total = item_price * quantity
- If payment_method=wallet then total must be <= 500.00 (otherwise reject)
- If coupon_code is provided and valid, discount = 10% (round to cents)
Responses:
- 200 OK: {order_id, total, discount}
- 400 Bad Request: validation error
```
