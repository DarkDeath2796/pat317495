from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from translator import PajAjapTranslator as pat
from cachetools import LRUCache

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

translator = pat()
cache = LRUCache(maxsize=200)

# Pydantic model for translation requests
class TranslationRequest(BaseModel):
    text: str

@app.post("/api/translate")
async def translate(req: TranslationRequest):
    cleaned = req.text.strip().lower()

    if cleaned in cache:
        print("Using cache")
        return {"translation": cache[cleaned][0], "raw": cache[cleaned][1]}

    output = translator.translate(req.text)
    if not "error" in output[1]
        cache[cleaned] = [output[1], output[2]]
    else:
        return {"translation": "Error translating your text, Please try again later.", "raw": ""}

    print(output)
    return {"translation": output[1], "raw": output[2]}

# 🛠 FIXED this route
@app.get("/api/cache")
async def get_cache():
    cachestr = "\n".join([f"{k} => {v[0]}" for k, v in cache.items()])
    return {"cache": cachestr}

# 👻 404 route that returns a real 404
@app.get("/")
async def root():
    return {"detail": "Not found"}, 404

# 🏓 Ping-pong test
@app.get("/ping")
def ping():
    return {"ping": "pong"}
