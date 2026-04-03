from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    context = {"request": request}

    try:
        return templates.TemplateResponse("index.html", context)
    except Exception as exc:
        if "unhashable type" in str(exc):
            return templates.TemplateResponse(request, "index.html", context)
        raise
