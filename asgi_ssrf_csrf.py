from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
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

regex = r"(https?:\/\/[A-Za-z0-9.,_-]{1,512})|(\/img\/c[a-z0-9]{1,}\.png)"

class CsrfSettings(BaseModel):
  secret_key: str = "asecrettoeverybody"

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

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
async def root(request: Request, csrf_protect: CsrfProtect = Depends()):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse("index.html", {"request": request, "csrf_token": csrf_token})
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response

@app.get("/cat", response_class=HTMLResponse)
async def cat(request: Request,  name: str, csrf_protect: CsrfProtect = Depends()):
    await csrf_protect.validate_csrf(request)
    check_result = check_img_url(name)
    if check_result["action"] == "RESTRICT":
        raise HTTPException(status_code=422, detail=check_result["reason"])
    response = templates.TemplateResponse("main.html", {"request": request, "name": name})
    csrf_protect.unset_csrf_cookie(response)
    return response

@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})