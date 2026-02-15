import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from app.agents.graph import app as agent_app

app = FastAPI(title="Bank ABC Voice Agent API", version="0.1.0")

# CORS Setup
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://*.vercel.app",
    "*" # For POC allow all
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    customer_id: Optional[str] = None
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str

@app.get("/")
async def root():
    return {"message": "Bank ABC Voice Agent API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Prepare inputs
        inputs = {"messages": [("user", request.message)]}
        if request.customer_id:
            inputs["customer_id"] = request.customer_id
            
        # Run the agent
        # For POC we are not persistently storing thread state in a DB, 
        # but LangGraph checkpointing can be used.
        # Here we just run the graph for the single turn or session if we had thread_id.
        
        # Config for thread-level persistence if we had a checkpointer setup
        config = {"configurable": {"thread_id": request.thread_id or "default_thread"}}
        
        final_state = agent_app.invoke(inputs, config=config)
        
        # Extract response
        messages = final_state["messages"]
        last_message = messages[-1]
        
        return ChatResponse(
            response=last_message.content,
            thread_id=request.thread_id or "default_thread"
        )
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/token")
async def get_voice_token(room_name: str = "bank-abc-voice", participant_name: str = "customer"):
    """Generate LiveKit access token for voice call"""
    try:
        from app.services.livekit_auth import generate_token
        token = generate_token(room_name, participant_name)
        return {
            "token": token,
            "url": os.getenv("LIVEKIT_URL"),
            "room_name": room_name
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/local", response_model=ChatResponse)
async def chat_local(request: ChatRequest):
    """Chat endpoint using local Ollama LLM (free, no API key needed)"""
    try:
        from app.agents.graph_local import app as local_agent_app
        
        inputs = {"messages": [("user", request.message)]}
        if request.customer_id:
            inputs["customer_id"] = request.customer_id
            
        config = {"configurable": {"thread_id": request.thread_id or "default_thread"}}
        
        final_state = local_agent_app.invoke(inputs, config=config)
        
        messages = final_state["messages"]
        last_message = messages[-1]
        
        return ChatResponse(
            response=last_message.content,
            thread_id=request.thread_id or "default_thread"
        )
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
