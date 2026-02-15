from langchain_core.tools import tool
from app.services import banking

@tool
def verify_identity(customer_id: str, pin: str) -> bool:
    """
    Verifies the identity of a customer using their ID and PIN.
    This must be called and return True before accessing any sensitive account data.
    """
    return banking.verify_identity(customer_id, pin)

@tool
def get_recent_transactions(customer_id: str, count: int = 5) -> str:
    """
    Retrieves the recent transactions for a customer.
    Requires successful identity verification first.
    """
    transactions = banking.get_recent_transactions(customer_id, count)
    return str(transactions)

@tool
def block_card(customer_id: str, card_id: str, reason: str) -> str:
    """
    Blocks a customer's card. This is an irreversible action.
    Requires successful identity verification first.
    """
    return banking.block_card(customer_id, card_id, reason)

@tool
def get_account_balance(customer_id: str) -> str:
    """
    Retrieves the account balance for a customer.
    Requires successful identity verification first.
    """
    balance_info = banking.get_account_balance(customer_id)
    return str(balance_info)
