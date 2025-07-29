import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from translator import PajAjapTranslator as pat
from cachetools import LRUCache
from python-dotenv import load_dotenv

load_dotenv()

password = os.getenv("PWD")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

translator = pat()
cache = LRUCache(maxsize=200)

class TranslationRequest(BaseModel):
    text: str

@app.post("/api/translate")
async def translate(req: TranslationRequest):
    cleaned = req.text.strip().lower()

    if cleaned in cache:
        print("Using cache")
        return {"translation": cache[cleaned][0], "raw": cache[cleaned][1]}

    output = translator.translate(req.text)
    if not "error" in output[1]:
        cache[cleaned] = [output[1], output[2]]
    else:
        return {"translation": "Error translating your text, Please try again later.", "raw": ""}

    print(output)
    return {"translation": output[1], "raw": output[2]}

@app.get("/api/cache")
async def get_cache(passsword: str = Query(...)):
    if passsword != password:
        raise HTTPException(status_code=403, detail="Access denied. Wrong password.")
    return cache

@app.get("/ping")
def ping():
    return {"ping": "pong"}
