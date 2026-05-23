from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API key from environment
api_key = os.getenv("NEXUS_API_KEY")

if not api_key:
    raise ValueError("NEXUS_API_KEY environment variable is missing")

# OpenAI client
client = OpenAI(
    api_key=api_key,
    base_url="https://apidev.navigatelabsai.com"
)

# Request body model
class PromptRequest(BaseModel):
    user_prompt: str

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "NexusAI backend is running successfully"
    }

# Welcome endpoint
@app.get("/welcome")
def welcome():
    return {
        "message": "Welcome to Navi Chat"
    }

# AI endpoint
@app.post("/run_task")
async def run_task(req: PromptRequest):
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a personal AI tutor. "
                        "Explain everything in simple layman terms. "
                        "Keep responses short, precise, and factual."
                    )
                },
                {
                    "role": "user",
                    "content": req.user_prompt
                }
            ]
        )

        return {
            "response": response.choices[0].message.content
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )