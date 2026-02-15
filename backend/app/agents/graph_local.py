"""
Local LLM Agent using Ollama (Open Source Alternative)
Replaces OpenAI/Gemini for testing without API costs
"""
from typing import Annotated, Literal, TypedDict, Union
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.agents.tools import verify_identity, get_recent_transactions, block_card, get_account_balance

# Define the state
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    customer_id: Union[str, None]
    is_verified: bool

# Initialize Ollama LLM (free, runs locally)
llm = ChatOllama(
    model="llama3.2:3b",  # Lightweight model, faster for testing
    temperature=0,
    base_url="http://localhost:11434"
)

# Define Tools
tools = [verify_identity, get_recent_transactions, block_card, get_account_balance]
llm_with_tools = llm.bind_tools(tools)

def call_model(state: AgentState):
    messages = state["messages"]
    
    system_message = SystemMessage(content="""You are a helpful banking assistant for Bank ABC.
    
CRITICAL SECURITY RULES:
1. You MUST verify the user's identity using verify_identity(customer_id, pin) BEFORE providing any account details (balance, transactions) or performing actions (block card).
2. If the user hasn't provided their Customer ID and PIN, ask for it politely.
3. Once verified, you can proceed with their request.

Current User Verification Status: """ + str(state.get("is_verified", False)))
    
    response = llm_with_tools.invoke([system_message] + messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return "tools"
    return "__end__"

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app = workflow.compile()
