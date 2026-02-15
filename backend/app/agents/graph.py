from typing import Annotated, Literal, TypedDict, Union
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from app.agents.tools import verify_identity, get_recent_transactions, block_card, get_account_balance

# Define the state
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    customer_id: Union[str, None]
    is_verified: bool

# Initialize LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Define Tools
tools = [verify_identity, get_recent_transactions, block_card, get_account_balance]
llm_with_tools = llm.bind_tools(tools)

# Define Nodes
def routing_node(state: AgentState):
    """
    Analyzes the user's intent and routes to the appropriate flow.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # Prompt for routing
    system_prompt = """You are an intelligent routing agent for Bank ABC. 
    Analyze the user's latest message and route them to one of the following intents:
    1. CARD_ISSUES: Lost/stolen card, declined payments.
    2. ACCOUNT_SERVICING: Statement requests, address change.
    3. ACCOUNT_OPENING: New account, eligibility.
    4. DIGITAL_SUPPORT: Login issues, app crash.
    5. TRANSFERS_BILLS: Failed transfers, bill pay.
    6. ACCOUNT_CLOSURE: Close account, retention.
    7. GENERAL: Greetings, or unclear intent.
    
    If you need more info to clarify intent, ask the user.
    """
    
    # This is a simplification. In a real app, we might use a structured output or specific classification chain.
    # For this POC, we'll let the main LLM handle the conversation and tool calling directly for "Deep Logic" flows,
    # and identifying the intent.
    
    return {"messages": [AIMessage(content="I am routing your request...")]} # Placeholder update

def call_model(state: AgentState):
    messages = state["messages"]
    
    # Enforce guardrails via system message
    system_message = SystemMessage(content="""You are a helpful banking assistant for Bank ABC.
    You have access to tools to help customers.
    
    CRITICAL SECURITY RULES:
    1. You MUST verify the user's identity using verify_identity(customer_id, pin) BEFORE providing any account details (balance, transactions) or performing actions (block card).
    2. If the user hasn't provided their Customer ID and PIN, ask for it politely.
    3. Once verified, you can proceed with their request.
    
    Flow Handling:
    - Card & ATM Issues: Use block_card tool if needed.
    - Account Servicing: Use get_account_balance or check profile.
    
    For other flows (Account Opening, Digital Support, Transfers, Account Closure),
    provide a helpful stub response simulating that flow, e.g., "I can help you with account opening. Please visit our nearest branch..."
    
    Current User Verification Status: """ + str(state.get("is_verified", False)))
    
    # Prepend system message if not present or needs update
    # Note: efficient way is to just pass it to invoke
    response = llm_with_tools.invoke([system_message] + messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return "tools"
    return "__end__"

# This is a simplified single-node graph with tools for the POC to handle all flows dynamically
# In a more complex setup, we would have separate subgraphs for each flow.

workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app = workflow.compile()
