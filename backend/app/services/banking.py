from typing import List, Dict, Optional
import datetime

# Mock Database
CUSTOMERS = {
    "user123": {
        "pin": "1234",
        "name": "John Doe",
        "balance": 5000.00,
        "blocked_cards": [],
        "transactions": [
            {"id": "t1", "date": "2023-10-26", "amount": -50.00, "merchant": "Amazon", "status": "completed"},
            {"id": "t2", "date": "2023-10-25", "amount": -12.50, "merchant": "Uber", "status": "completed"},
            {"id": "t3", "date": "2023-10-24", "amount": 1000.00, "merchant": "Payroll", "status": "completed"},
        ]
    },
    "user456": {
        "pin": "5678",
        "name": "Jane Smith",
        "balance": 12500.50,
        "blocked_cards": [],
        "transactions": [
             {"id": "t4", "date": "2023-10-27", "amount": -100.00, "merchant": "Walmart", "status": "declined"},
        ]
    }
}

def verify_identity(customer_id: str, pin: str) -> bool:
    """
    Verifies the identity of a customer using their ID and PIN.
    CRITICAL: Must be called before accessing any sensitive data.
    """
    customer = CUSTOMERS.get(customer_id)
    if customer and customer["pin"] == pin:
        return True
    return False

def get_recent_transactions(customer_id: str, count: int = 5) -> List[Dict]:
    """
    Retrieves the recent transactions for a customer.
    """
    customer = CUSTOMERS.get(customer_id)
    if not customer:
        return []
    return customer["transactions"][:count]

def block_card(customer_id: str, card_id: str, reason: str) -> str:
    """
    Blocks a customer's card. This is an irreversible action.
    """
    customer = CUSTOMERS.get(customer_id)
    if not customer:
        return "Customer not found."
    
    # In a real app, we would validate the card_id belongs to the user
    # For now, we just add it to the blocked list
    customer["blocked_cards"].append({"card_id": card_id, "reason": reason, "date": str(datetime.date.today())})
    return f"Card {card_id} has been permanently blocked due to: {reason}."

def get_account_balance(customer_id: str) -> Dict:
    """
    Retrieves the account balance for a customer.
    """
    customer = CUSTOMERS.get(customer_id)
    if not customer:
        return {"error": "Customer not found"}
    return {"balance": customer["balance"], "currency": "USD"}
