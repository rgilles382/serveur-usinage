import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class FilePayload(BaseModel):
    fileName: str
    mimeType: str
    fileBase64: str

@app.post("/api/analyse")
async def analyse(payload: FilePayload):
    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY not set"}

    prompt_text = (
        "Tu es un expert en usinage CN. Analyse l'image/PDF et fournis : "
        "1) liste des opérations, 2) outils probables, 3) estimation du temps en minutes."
    )

    body = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "system", "content": "Tu es un technicien d'atelier expert en usinage."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": f"data:{payload.mimeType};base64,{payload.fileBase64}"}
                ]
            }
        ],
        "temperature": 0.0
    }

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    r = requests.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers, timeout=120)
          if r.status_code != 200:
        print("❌ OpenAI error:", r.text)
        return {"error": "OpenAI error", "detail": r.text}

    result = r.json()
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"estimation": content}



