"""
Bank ABC Voice Agent - LiveKit Integration with Gemini Live Audio
"""
import asyncio
import logging
from typing import Dict, Any
from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.plugins import google
import os
from dotenv import load_dotenv

# Import our banking tools
from app.services.banking import verify_identity, get_recent_transactions, block_card, get_account_balance

load_dotenv()

logger = logging.getLogger("bank-abc-voice-agent")
logger.setLevel(logging.INFO)


class BankingAssistant:
    """Banking assistant with voice interface and tool calling"""
    
    def __init__(self):
        self.customer_id = None
        self.is_verified = False
        self.conversation_context = []
        
    async def verify_customer(self, customer_id: str, pin: str) -> Dict[str, Any]:
        """Verify customer identity"""
        result = verify_identity(customer_id, pin)
        if result:
            self.customer_id = customer_id
            self.is_verified = True
            return {"success": True, "message": f"Identity verified for customer {customer_id}"}
        return {"success": False, "message": "Invalid credentials. Please try again."}
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance - requires verification"""
        if not self.is_verified:
            return {"error": "Please verify your identity first by providing your customer ID and PIN."}
        
        balance = get_account_balance(self.customer_id)
        return balance
    
    async def get_transactions(self, count: int = 5) -> Dict[str, Any]:
        """Get recent transactions - requires verification"""
        if not self.is_verified:
            return {"error": "Please verify your identity first."}
        
        transactions = get_recent_transactions(self.customer_id, count)
        return {"transactions": transactions}
    
    async def block_customer_card(self, card_id: str, reason: str) -> Dict[str, Any]:
        """Block a card - irreversible action, requires verification and confirmation"""
        if not self.is_verified:
            return {"error": "Please verify your identity first."}
        
        result = block_card(self.customer_id, card_id, reason)
        return {"success": True, "message": result}


# Define tool schemas for Gemini function calling
BANKING_TOOLS = [
    {
        "name": "verify_customer",
        "description": "Verify customer identity using their customer ID and PIN. MUST be called before any sensitive operations like checking balance or transactions.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "Customer ID (e.g., user123)"},
                "pin": {"type": "string", "description": "4-digit PIN number"}
            },
            "required": ["customer_id", "pin"]
        }
    },
    {
        "name": "get_balance",
        "description": "Get customer's account balance. Requires prior identity verification.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_transactions",
        "description": "Get customer's recent transactions. Requires prior identity verification.",
        "parameters": {
            "type": "object",
            "properties": {
                "count": {"type": "integer", "description": "Number of transactions to retrieve (default 5)"}
            }
        }
    },
    {
        "name": "block_customer_card",
        "description": "Block a customer's card. This is IRREVERSIBLE. Requires verification and explicit customer confirmation.",
        "parameters": {
            "type": "object",
            "properties": {
                "card_id": {"type": "string", "description": "Card identifier"},
                "reason": {"type": "string", "description": "Reason for blocking (lost, stolen, compromised)"}
            },
            "required": ["card_id", "reason"]
        }
    }
]


async def entrypoint(ctx: JobContext):
    """Main entry point for the voice agent"""
    
    logger.info(f"Connecting to room {ctx.room.name}")
    
    # Initialize banking assistant
    assistant = BankingAssistant()
    
    # Create system prompt with banking context
    system_prompt = """You are a helpful banking assistant for Bank ABC.
    
CRITICAL SECURITY RULES:
1. You MUST verify the customer's identity using verify_customer(customer_id, pin) BEFORE providing any account details or performing actions.
2. If the customer hasn't provided their Customer ID and PIN, politely ask for them.
3. For irreversible actions like blocking a card, ask for explicit confirmation: "To confirm, should I proceed with blocking your card?"

AVAILABLE FLOWS:
- Card & ATM Issues: Help with lost/stolen cards, declined payments. Use block_customer_card if needed.
- Account Servicing: Provide balance, transaction history, profile updates.
- Account Opening: Provide information about new accounts (informational only).
- Digital App Support: Help with login issues, app problems (informational only).
- Transfers & Bill Payments: Assist with transfer issues (informational only).
- Account Closure: Capture reason and provide retention information (informational only).

Be conversational, empathetic, and professional. Keep responses concise for voice interaction.
"""
    
    # Connect to participant (first one that joins)
    await ctx.connect()
    logger.info("Agent connected to room")
    
    # Wait for participant
    participant = await ctx.wait_for_participant()
    logger.info(f"Participant {participant.identity} joined")
    
    # Initialize Gemini Live Audio session
    try:
        model = google.realtime.RealtimeModel(
            model="models/gemini-2.0-flash-exp",
            voice="Kore",  # Voice option
            temperature=0.8,
            system_instruction=system_prompt,
            tools=BANKING_TOOLS
        )
        
        # Create assistant session
        agent_session = model.sessions().create()
        
        logger.info("Gemini Live Audio session created")
        
        # Handle audio streaming and tool calls
        async def handle_tool_call(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
            """Execute banking tool calls"""
            logger.info(f"Tool call: {function_name} with {arguments}")
            
            if function_name == "verify_customer":
                return await assistant.verify_customer(
                    arguments.get("customer_id"),
                    arguments.get("pin")
                )
            elif function_name == "get_balance":
                return await assistant.get_balance()
            elif function_name == "get_transactions":
                return await assistant.get_transactions(arguments.get("count", 5))
            elif function_name == "block_customer_card":
                return await assistant.block_customer_card(
                    arguments.get("card_id"),
                    arguments.get("reason")
                )
            else:
                return {"error": f"Unknown function: {function_name}"}
        
        # Run the agent session
        agent_session.on("function_call", handle_tool_call)
        
        # Start audio streaming (this would be more complex in real implementation)
        # For now, this is a simplified structure
        logger.info("Voice agent running. Listening for audio...")
        
        # Keep session alive
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in voice agent: {e}")
        raise


if __name__ == "__main__":
    # Run the LiveKit agent worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.getenv("LIVEKIT_API_KEY"),
            api_secret=os.getenv("LIVEKIT_API_SECRET"),
            ws_url=os.getenv("LIVEKIT_URL"),
        )
    )
