from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional

from database import init_db, save_url, get_url, increment_clicks
from utils import generate_short_code
from rateLimiter import check_rate_limit, redis_client

app = FastAPI(title="URL Shortener API")

init_db()


class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_alias: Optional[str] = None


@app.post("/shorten", dependencies=[Depends(check_rate_limit)])
def shorten_url(payload: ShortenRequest, request: Request):
    original_url = str(payload.url)

    if payload.custom_alias:
        short_code = payload.custom_alias.strip()
        if get_url(short_code):
            raise HTTPException(status_code=400, detail="Custom alias already taken.")
    else:
        short_code = generate_short_code()
        while get_url(short_code):
            short_code = generate_short_code()

    save_url(short_code, original_url)

    base_url = str(request.base_url).rstrip("/")
    return {
        "short_code": short_code,
        "short_url": f"{base_url}/{short_code}",
        "original_url": original_url,
    }


@app.get("/{short_code}")
def redirect_to_url(short_code: str):
    cache_key = f"url:{short_code}"

    # 1. Check Redis cache first
    if redis_client:
        cached_url = redis_client.get(cache_key)
        if cached_url:
            increment_clicks(short_code)
            return RedirectResponse(url=cached_url, status_code=302)

    # 2. Fallback to SQLite
    record = get_url(short_code)
    if not record:
        raise HTTPException(status_code=404, detail="Short URL not found.")

    # 3. Store in Redis for 1 hour (3600 seconds)
    if redis_client:
        redis_client.setex(cache_key, 3600, record["original_url"])

    increment_clicks(short_code)
    return RedirectResponse(url=record["original_url"], status_code=302)


@app.get("/stats/{short_code}")
def get_stats(short_code: str):
    record = get_url(short_code)
    if not record:
        raise HTTPException(status_code=404, detail="Short URL not found.")
    return record