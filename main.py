from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from translator import PajAjapTranslator as pat
from cachetools import LRUCache

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
        return {"translation": cache[cleaned][0], "raw": cache[cleaned][1]}

    output = translator.translate(req.text)
    cache[cleaned] = [output[1], output[2]]

    print(output)

    return {"translation": output[1], "raw": output[2]}


@app.get("/api/cache")
async def return_():
    return cache


@app.get("/")
async def n():
    return 404


@app.get("/ping")
def ping():
    return {"ping": "pong"}
