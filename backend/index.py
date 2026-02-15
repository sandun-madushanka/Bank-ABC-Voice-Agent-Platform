# Vercel serverless function handler
from app.main import app

# Export the FastAPI app for Vercel
handler = app
