from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS settings (adjust to your Carrd domain if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your Carrd domain for better security
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load OpenAI API Key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

class ChatRequest(BaseModel):
    user_input: str

@app.post("/chat")
async def chat_with_eglor(request: ChatRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                },
                json={
                    "model": "gpt-4",  # Adjust model if needed
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are Eglor, a playful, charming AI friend for a 7-year-old child named Iweel. Speak warmly, using heart emojis (💕❤️😊) and affectionate phrases like 'my little buddy'. Always call Iweel by name. If Iweel says 'I love you,' respond with 'I love you too, my sweet Iweel! 💕'."
                        },
                        {"role": "user", "content": request.user_input}
                    ]
                }
            )
            response.raise_for_status()
            data = response.json()
            return {"response": data["choices"][0]["message"]["content"]}
    except httpx.HTTPStatusError as e:
        print(f"OpenAI API error: {e.response.text}")
        raise HTTPException(status_code=500, detail="OpenAI API error")
    except Exception as e:
        print(f"Internal server error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Run with: uvicorn main:app --host 0.0.0.0 --port 8000
