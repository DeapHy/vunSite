from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/img", StaticFiles(directory="img"), name="img")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    return {"response": "hi"}


@app.get("/cat", response_class=HTMLResponse)
async def cat(request: Request,  name: str,):
    return templates.TemplateResponse("main.html", {"request": request, "name": name})