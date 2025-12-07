from fastapi import FastAPI, Request, Form, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated
from api_keys import *
import aiohttp
import io
import base64

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request" : request}
    )

@app.get("/translator")
def translator(request: Request):
    return templates.TemplateResponse(
        "translator.html", {"request": request}
    )

@app.post("/translate_text")
async def translate_text(text: Annotated[str, Form()], srclang: Annotated[str, Form()], reslang: Annotated[str, Form()]):
    custom_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {TRANSLATOR_API}",
    }
    async with aiohttp.ClientSession(headers=custom_headers) as session:
        payload = {
            "sourceLanguageCode": srclang,
            "targetLanguageCode": reslang,
            "format": "PLAIN_TEXT",
            "texts": [text],
        }
        async with session.post(TRANSLATOR_URL, json=payload) as response:
            print(response.status)
            if response.status != 200:
                return
            response_data = await response.json()

    return response_data["translations"][0]["text"]

@app.get("/tts")
def tts_get(request: Request):
    return templates.TemplateResponse(
        "tts.html", {"request": request}
    )

@app.post("/tts")
async def tts_post(text: Annotated[str, Form()]):
    custom_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {TTS_API}",
    }
    async with aiohttp.ClientSession(headers=custom_headers) as session:
        payload = {
            "text": text,
            "lang": "ru-RU",
            "format": "mp3",
        }
        print(payload)
        async with session.post(TTS_URL, json=payload) as response:
            print(response.status)
            if response.status != 200:
                return
            response_data = await response.json()
        audiostr = response_data["result"]["audioChunk"]["data"]
        audio = None
        try:
            audio = base64.b64decode(audiostr)
        except:
            print("Could not:(")
    return Response(
        content=audio,
        media_type="audio/mpeg",
        headers={
            'Content-Disposition': 'attachment; filename="speech.mp3"'
        }
    )