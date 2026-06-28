from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from generate_static_index import generate_indexes  # noqa: E402
from wislib import (  # noqa: E402
    COMPLETE,
    INBOX,
    OUTBOX,
    ROOT as WIS_ROOT,
    active_inbox_items,
    completed_items,
    organize_outbox,
    reports_by_date,
    run_notes,
    write_inbox_item,
)

app = FastAPI(title="While I Sleep", version="1.1.0")
templates = Jinja2Templates(directory=str(ROOT / "app" / "templates"))


def dashboard_context(request: Request, message: str | None = None) -> dict:
    grouped = reports_by_date()
    return {
        "request": request,
        "message": message,
        "queued": active_inbox_items(),
        "completed": list(reversed(completed_items()))[:40],
        "reports_by_date": grouped,
        "report_total": sum(len(items) for items in grouped.values()),
        "runs": run_notes()[:20],
    }


def wants_partial(request: Request) -> bool:
    return request.headers.get("HX-Request", "").lower() == "true"


def safe_child(base: Path, relative: str) -> Path:
    candidate = (base / relative).resolve()
    base_resolved = base.resolve()
    if candidate != base_resolved and base_resolved not in candidate.parents:
        raise HTTPException(status_code=404, detail="Not found")
    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return candidate


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", dashboard_context(request))


@app.get("/partials/dashboard", response_class=HTMLResponse)
async def dashboard_partial(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("_dashboard_status.html", dashboard_context(request))


@app.post("/items", response_class=HTMLResponse, response_model=None)
async def add_item(request: Request, title: str = Form(...), body: str = Form(...)):
    title = title.strip()
    body = body.strip()
    if not title or not body:
        raise HTTPException(status_code=400, detail="Title and body are required")
    path = write_inbox_item(title, body)
    message = f"Added {path.relative_to(WIS_ROOT)}"
    if wants_partial(request):
        return templates.TemplateResponse("_dashboard_status.html", dashboard_context(request, message=message))
    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/organize-outbox", response_class=HTMLResponse, response_model=None)
async def organize(request: Request):
    moved = organize_outbox()
    written = generate_indexes()
    message = f"Organized {len(moved)} report(s); regenerated {len(written)} index page(s)."
    if wants_partial(request):
        return templates.TemplateResponse("_dashboard_status.html", dashboard_context(request, message=message))
    return RedirectResponse(url="/", status_code=303)


@app.post("/admin/regenerate-index", response_class=HTMLResponse, response_model=None)
async def regenerate_index(request: Request):
    written = generate_indexes()
    message = f"Regenerated {len(written)} static index page(s)."
    if wants_partial(request):
        return templates.TemplateResponse("_dashboard_status.html", dashboard_context(request, message=message))
    return RedirectResponse(url="/", status_code=303)


@app.get("/outbox/{day}/", response_class=HTMLResponse)
async def day_view(request: Request, day: str) -> HTMLResponse:
    grouped = reports_by_date()
    if day not in grouped:
        raise HTTPException(status_code=404, detail="Day not found")
    return templates.TemplateResponse("day.html", {"request": request, "day": day, "reports": grouped[day]})


@app.get("/static-outbox/")
async def static_outbox_index() -> FileResponse:
    path = OUTBOX / "index.html"
    if not path.exists():
        generate_indexes()
    return FileResponse(path, media_type="text/html; charset=utf-8")


@app.get("/static-outbox/{filename:path}")
async def static_outbox_file(filename: str) -> FileResponse:
    path = safe_child(OUTBOX, filename)
    if path.suffix.lower() != ".html":
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path, media_type="text/html; charset=utf-8")


@app.get("/reports/{day}/{filename:path}")
async def report(day: str, filename: str) -> FileResponse:
    path = safe_child(OUTBOX / day, filename)
    if path.suffix.lower() != ".html":
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path, media_type="text/html; charset=utf-8")


@app.get("/source/{bucket}/{filename:path}", response_class=PlainTextResponse)
async def source(bucket: Literal["inbox", "complete", "runs"], filename: str) -> PlainTextResponse:
    base = {"inbox": INBOX, "complete": COMPLETE, "runs": WIS_ROOT / "runs"}[bucket]
    path = safe_child(base, filename)
    if bucket in {"inbox", "complete"} and path.suffix.lower() not in {".md", ".txt"}:
        raise HTTPException(status_code=404, detail="Not found")
    if bucket == "runs" and path.suffix.lower() != ".md":
        raise HTTPException(status_code=404, detail="Not found")
    return PlainTextResponse(path.read_text(encoding="utf-8", errors="replace"))


@app.get("/health", response_class=PlainTextResponse)
async def health() -> str:
    return "ok"
