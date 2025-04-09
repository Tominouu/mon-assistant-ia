from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import SessionLocal, init_db
from .models import User, Message
import httpx

app = FastAPI()

# Init DB at startup
@app.on_event("startup")
def on_startup():
    init_db()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chat")
async def chat(prompt: str, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        res = await client.post("http://ollama:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt
        })
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="Erreur appel LLM")
    
    data = res.json()
    answer = data.get("response", "")

    # On enregistre (ici, user_id=1 par défaut)
    msg = Message(user_id=1, text=prompt, response=answer)
    db.add(msg)
    db.commit()

    return {"response": answer}
