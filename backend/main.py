import os
import re
import glob
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from backend.agent import run_query

app = FastAPI(title="Titanic Chatbot API")

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    text: str
    images: List[str]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    existing_plots = set(glob.glob("static/plot_*.png"))

    try:
        result = run_query(request.query)

        new_plots = set(glob.glob("static/plot_*.png")) - existing_plots
        images = [f"/{p.replace(chr(92), '/')}" for p in new_plots]

        return ChatResponse(text=result["text"], images=images)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
