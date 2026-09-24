import hashlib
from fastapi import Depends, FastAPI, HTTPException,Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import crud, models
from app.database import Base, engine, get_db
from app.schemas import LinkCreate, LinkResponse, StatsResponse


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="A URL shortener with click analytics.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse("app/static/index.html") 

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/links", response_model=LinkResponse, status_code=201)
def create_short_link(
    link_data: LinkCreate,
    db: Session = Depends(get_db),
):
    return crud.create_link(db, link_data)

@app.get("/{short_code}")
def redirect_to_original(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db),
):
    link = crud.get_link_by_code(db, short_code)

    if link is None:
        raise HTTPException(status_code=404, detail="Short link not found")

    ip_address = request.client.host if request.client else None

    ip_hash = (
        hashlib.sha256(ip_address.encode()).hexdigest()
        if ip_address
        else None
    )

    crud.record_click(
        db,
        link,
        referrer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
        ip_hash=ip_hash,
    )

    return RedirectResponse(
        url=link.original_url,
        status_code=307,
    )
@app.get("/links/{short_code}/stats", response_model=StatsResponse)
def get_stats(
    short_code: str,
    db: Session = Depends(get_db),
):
    result = crud.get_link_stats(db, short_code)

    if result is None:
        raise HTTPException(status_code=404, detail="Short link not found")

    link, click_count = result

    return {
        "short_code": link.short_code,
        "original_url": link.original_url,
        "created_at": link.created_at,
        "click_count": click_count,
    }
