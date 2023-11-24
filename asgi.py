from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from requests import get
from pydantic import BaseModel
import re

app = FastAPI()
app.mount("/img", StaticFiles(directory="img"), name="img")
templates = Jinja2Templates(directory="templates")


trusted_sources = (
    "https://random.imagecdn.app",
    "/img/cat.png"
)


regex = r"(https?:\/\/[A-Za-z0-9.,_-]{1,512})|(\/img\/[a-z0-9]{1,}\.png)"


def check_img_url(url: str) -> dict:
    try:
        base_url = re.search(regex, url).group()
    except AttributeError:
        return {
            "action": "RESTRICT",
            "reason": "Incorrect URL format"
        }
    if base_url in trusted_sources:
        return {
            "action": "PROCEED",
            "reason": ""
        }
    else:
        return {
            "action": "RESTRICT",
            "reason": "Source isn't allowed (SSRF fail)"
        }

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/cat", response_class=HTMLResponse)
async def cat(request: Request,  name: str):
    check_result = check_img_url(name)
    if check_result["action"] == "RESTRICT":
        raise HTTPException(status_code=422, detail=check_result["reason"])
    return templates.TemplateResponse("main.html", {"request": request, "name": name})