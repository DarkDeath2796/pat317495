# main.py
import os
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from translator import PajAjapTranslator
from dotenv import load_dotenv
from hybrid_cache import HybridCache

load_dotenv()

password = os.getenv("PWD")

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve css/ and js/ folders as static files
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")

translator = PajAjapTranslator()
cache = HybridCache(maxsize=500)


class TranslationRequest(BaseModel):
    text: str


def normalize_cache_key(text: str) -> str:
    return text.strip().lower()


@app.post("/api/translate")
async def translate(req: TranslationRequest):
    cleaned = normalize_cache_key(req.text)
    if not cleaned:
        return {"translation": "", "raw": ""}

    # Check cache
    cached = cache.get(cleaned)
    if cached:
        logging.info("Cache hit: '%s'", cleaned)
        return {"translation": cached[0], "raw": cached[1]}

    # Hybrid translate
    try:
        output = translator.translate(req.text)
        if isinstance(output, str) and output.startswith("Error"):
            raise Exception(output)
        if isinstance(output, tuple) and len(output) >= 3:
            translated = output[1]
            raw = output[2]
            cache.set(cleaned, [translated, raw])

            # Bidirectional cache: translated text can map back to original text.
            reverse_key = normalize_cache_key(translated)
            if reverse_key and reverse_key != cleaned and reverse_key not in cache:
                cache.set(reverse_key, [cleaned, f"Reverse cached from: {cleaned}"])

            logging.info("Translated '%s'", cleaned)
            return {"translation": translated, "raw": raw}
        else:
            return {"translation": "Error translating text, Please try again later.", "raw": ""}
    except Exception as e:
        logging.error("Translation error: %s", e)
        return {"translation": "Error translating text, Please try again later.", "raw": str(e)}


@app.get("/api/cache")
async def get_cache(passsword: str = Query(...)):
    if passsword != password:
        raise HTTPException(status_code=403, detail="Access denied. Wrong password.")
    return dict(cache.items())


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r", encoding="utf-8") as h:
        html = h.read()
    return HTMLResponse(content=html)


@app.get("/ping")
def ping():
    return {"ping": "pong"}
