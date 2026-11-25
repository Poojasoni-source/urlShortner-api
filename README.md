# URL Shortener API

A lightweight, high-performance URL shortener REST API built with **FastAPI**, **SQLite**, and **Redis**. Supports custom aliases, click analytics, Redis-backed redirect caching, and per-IP rate limiting.

## Features
- **Short URL Generation:** Cryptographically secure 6-character Base62 short codes ($62^6 \approx 56.8\text{B}$ combinations) with collision checks.
- **Custom Aliases:** Optional user-defined short codes (e.g., `/gh`).
- **Redis Caching:** Caches `short_code -> original_url` lookups with a 1-hour TTL to reduce database reads on redirects.
- **Rate Limiting:** Fixed-window per-IP rate limiting using Redis atomic `INCR` and `EXPIRE` (defaults to 10 requests/minute on `/shorten`).
- **Click Analytics:** Tracks total redirects per link using HTTP `302` temporary redirects so browser caching does not skew counts.

## Tech Stack
- **Framework:** FastAPI, Uvicorn, Pydantic
- **Database:** SQLite (indexed on `short_code`)
- **Cache & Rate Limiting:** Redis

## Project Structure
```text
├── main.py            # FastAPI routes and Redis caching logic
├── database.py        # SQLite connection, schema, and queries
├── utils.py           # Base62 short code generator
├── rateLimiter.py     # Redis-based per-IP rate limiter
├── requirements.txt   # Python dependencies
└── .gitignore
