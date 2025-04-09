from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel  # ← à importer
from sqlalchemy.orm import Session
from db import SessionLocal, init_db
from models import User, Message
import httpx

app = FastAPI()

# modèle d'entrée pour le prompt
class ChatRequest(BaseModel):
    prompt: str

# init base
@app.on_event("startup")
def on_startup():
    init_db()

# dépendance DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chat")
async def chat(data: ChatRequest, db: Session = Depends(get_db)):
    prompt = data.prompt

    async with httpx.AsyncClient() as client:
        res = await client.post("http://ollama:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt
        })

    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="Erreur appel LLM")

    response = res.json().get("response", "")

    msg = Message(user_id=1, text=prompt, response=response)
    db.add(msg)
    db.commit()

    return {"response": response}
