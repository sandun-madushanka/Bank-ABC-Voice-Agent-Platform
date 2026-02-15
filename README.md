# Bank ABC Voice Agent Platform (POC)

This is a **Full-Stack Real-Time Voice Agent** for Bank ABC. It handles customer calls via WebRTC, verifies identity, and routes through banking flows with strict security guardrails.

## Features

- **Text Chat Mode**: Simulate conversations with the agent via text interface
- **Real-Time Voice Mode**: Live voice calls powered by Gemini 2.5 Flash Native Audio
- **Deep Logic Flows**:
    - Card & ATM Issues (Block card, check status)
    - Account Servicing (Balance, transaction history)
- **Routing**: Dynamically routes based on user intent
- **Guardrails**: Enforces Identity Verification before accessing sensitive data
- **Observability**: LangSmith tracing for agent execution

## Architecture

```
Text Mode:
User (Browser) → Next.js Frontend → FastAPI → LangGraph Agent → Banking Services

Voice Mode:
User (Browser) → LiveKit WebRTC → Voice Agent → Gemini Live Audio API → Banking Tools
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API Key (for text mode)
- Google AI API Key (for voice mode)
- LiveKit Account (for voice mode - [sign up](https://livekit.io/))
- LangChain API Key (optional, for tracing)

## Setup Instructions

### 1. Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Create and activate virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-voice.txt
    ```

4.  Configure Environment Variables:
    -   Edit `.env` file and add your keys:
    ```env
    OPENAI_API_KEY=your_openai_key
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY=your_langchain_key
    LANGCHAIN_PROJECT=bank-abc-voice-agent
    
    # Voice Integration
    GOOGLE_AI_API_KEY=your_google_ai_key
    LIVEKIT_URL=wss://your-project.livekit.cloud
    LIVEKIT_API_KEY=your_livekit_key
    LIVEKIT_API_SECRET=your_livekit_secret
    ```

5.  Run the FastAPI server:
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

6.  **For Voice Mode**: Run the voice agent worker in a separate terminal:
    ```bash
    python voice_agent.py
    ```

### 2. Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  (Optional) Create `.env.local` for voice mode:
    ```env
    NEXT_PUBLIC_LIVEKIT_URL=wss://your-project.livekit.cloud
    ```

4.  Run the development server:
    ```bash
    npm run dev
    ```

5.  Open browser:
    - Text mode: `http://localhost:3000`
    - Voice mode: `http://localhost:3000/voice`

## Usage

### Text Mode
1. Select a simulated customer (user123 or user456)
2. Type messages like:
   - "I lost my card"
   - "Check my balance"
   - "Show my last 3 transactions"
3. The agent will ask for verification before sensitive operations

### Voice Mode
1. Click "Start Voice Call"
2. Allow microphone access
3. Speak naturally:
   - "Hello, I lost my card"
   - "I want to check my balance"
4. The agent will respond with voice and handle tool calls in real-time

## Test Credentials

- **Customer ID**: `user123`, **PIN**: `1234`, **Balance**: $5,000
- **Customer ID**: `user456`, **PIN**: `5678`, **Balance**: $12,500

## Deployment

### Frontend (Vercel)
1. Push code to GitHub
2. Import project into Vercel
3. Set environment variables:
   - `NEXT_PUBLIC_API_URL` (if backend is on different domain)
   - `NEXT_PUBLIC_LIVEKIT_URL`

### Backend (Render/Railway/Fly.io)
- Deploy FastAPI app using `requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Voice Agent Worker
- Deploy as separate worker process
- Use same environment variables as backend
- Start command: `python voice_agent.py`

## Trade-offs & Technical Decisions

1. **Voice Technology**: Using Gemini Live Audio API for native end-to-end voice processing (STT + LLM + TTS in one model) for lowest latency (<500ms)
2. **WebRTC**: LiveKit provides production-ready WebRTC infrastructure without managing TURN/STUN servers
3. **State Management**: In-memory for POC; production would use persistent checkpointer (Postgres/Redis)
4. **Authentication**: Hardcoded test users; production would use OAuth/JWT
5. **Model Selection**: 
   - Text mode uses GPT-3.5-turbo (accessible with most API keys)
   - Voice mode uses Gemini 2.5 Flash (native audio, function calling support)

## Project Structure

```
assignment/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── agents/
│   │   │   ├── graph.py           # LangGraph agent logic
│   │   │   └── tools.py           # Banking tool wrappers
│   │   └── services/
│   │       ├── banking.py         # Mock banking API
│   │       └── livekit_auth.py    # Token generation
│   ├── voice_agent.py             # LiveKit voice worker
│   ├── requirements.txt           # Python dependencies
│   └── requirements-voice.txt     # Voice-specific dependencies
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Text chat UI
│   │   └── voice/
│   │       └── page.tsx          # Voice call UI
│   └── lib/
│       └── agent.ts              # API client
└── README.md
```

## Observability

- **LangSmith**: Traces LangGraph tool calls and agent decisions
- **Gemini API Logs**: Audio/transcript inspection in Google Cloud Console
- **LiveKit Dashboard**: WebRTC metrics (latency, packet loss)

## Known Limitations (POC)

- Voice mode requires LiveKit account setup
- No persistent conversation history
- Simulated banking data (not real accounts)
- Limited error handling for voice interruptions

## Support

For issues or questions, check the implementation plan in the artifacts directory.
