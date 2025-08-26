# api_app.py
from __future__ import annotations

import json
import pathlib
import hashlib
import datetime as dt
from typing import List, Literal, Optional, Tuple
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Local modules
from moderation import validate_quote, normalize  # your bible/community rules
from q2b import QUOTES  # built-in quotes list lives in q2b.py

# ---------- Config / Paths ----------
BASE_DIR = pathlib.Path(__file__).parent.resolve()
APPROVED_PATH = BASE_DIR / "quotes_approved.json"

# ---------- Helpers ----------
def load_approved_quotes() -> List[dict]:
    if not APPROVED_PATH.exists():
        return []
    try:
        data = json.loads(APPROVED_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def save_approved_quotes(items: List[dict]) -> None:
    APPROVED_PATH.write_text(
        json.dumps(items, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

def merged_pool(feed: Literal["bible", "community", "both"]) -> List[dict]:
    built = QUOTES
    approved = load_approved_quotes()
    allq: List[dict] = []
    # mark source for transparency/debug
    allq.extend([{**q, "_src": "built-in"} for q in built])
    allq.extend([{**q, "_src": "approved"} for q in approved])

    if feed == "both":
        return allq
    return [q for q in allq if normalize(q.get("tag", "")) == feed]

def pick_for_date(day: dt.date, items: List[dict]) -> dict:
    if not items:
        raise ValueError("empty pool")
    idx = day.toordinal() % len(items)
    return items[idx]

def build_feed(start_date: dt.date, days: int, feed: Literal["bible","community","both"]) -> List[dict]:
    """Return a list of quotes for consecutive days starting at start_date."""
    pool = merged_pool(feed)
    if not pool:
        return []
    out: List[dict] = []
    for i in range(days):
        day = start_date + dt.timedelta(days=i)
        q = pick_for_date(day, pool)
        out.append({
            "date": day.isoformat(),
            "text": q["text"],
            "author": q["author"],
            "tag": q.get("tag", ""),
            "source": q.get("_src", "?"),
        })
    return out

def parse_date_in_tz(tz_name: Optional[str]) -> Tuple[dt.date, str]:
    tz = None
    if tz_name:
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = None
    if tz is None:
        tz = ZoneInfo("UTC")
        tz_name = "UTC"
    now = dt.datetime.now(tz)
    return now.date(), tz_name

def key_for(q: dict) -> str:
    # normalized (text+author) hash for dedupe
    text = normalize(q.get("text", ""))
    author = normalize(q.get("author", ""))
    return hashlib.sha256(f"{text}||{author}".encode("utf-8")).hexdigest()

# ---------- Schemas ----------
class QuoteIn(BaseModel):
    text: str
    author: str
    tag: str = Field(description="Use 'bible' for scripture; anything else will be treated as 'community'.")

class QuoteOut(BaseModel):
    date: dt.date
    tz: str
    text: str
    author: str
    tag: str
    source: Literal["built-in", "approved"]

class SubmitResult(BaseModel):
    accepted: bool
    reasons: Optional[List[str]] = None
    stored_as: Optional[str] = None  # 'bible' or 'community'

# ---------- App ----------
app = FastAPI(title="Quote of the Day API", version="1.0.0")

# CORS (loose now; tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return {
        "app": "Quote of the Day API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

@app.get("/v1/qod", response_model=QuoteOut)
def qod(feed: Literal["bible", "community", "both"] = "bible", tz: Optional[str] = None):
    """Return today's deterministic quote for the selected feed, using the local date in tz."""
    today, final_tz = parse_date_in_tz(tz)
    pool = merged_pool(feed)
    if not pool:
        raise HTTPException(404, detail=f"No quotes in feed '{feed}'.")
    q = pick_for_date(today, pool)
    return QuoteOut(
        date=today,
        tz=final_tz,
        text=q["text"],
        author=q["author"],
        tag=q.get("tag", ""),
        source=q.get("_src", "?"),
    )

@app.get("/v1/pick", response_model=QuoteOut)
def pick(date: str, feed: Literal["bible", "community", "both"] = "bible", tz: Optional[str] = None):
    """
    Pick deterministically for an arbitrary date (YYYY-MM-DD).
    `tz` is only echoed back (helps clients be consistent).
    """
    try:
        day = dt.date.fromisoformat(date)
    except Exception:
        raise HTTPException(400, detail="Invalid date; expected YYYY-MM-DD.")
    pool = merged_pool(feed)
    if not pool:
        raise HTTPException(404, detail=f"No quotes in feed '{feed}'.")
    q = pick_for_date(day, pool)
    return QuoteOut(
        date=day,
        tz=tz or "UTC",
        text=q["text"],
        author=q["author"],
        tag=q.get("tag", ""),
        source=q.get("_src", "?"),
    )

@app.get("/v1/feed")
def feed(
    days: int = Query(7, ge=1, le=31),
    feed: Literal["bible","community","both"] = "bible",
    tz: Optional[str] = None
):
    """Return N days of deterministic picks starting from 'today' in tz."""
    today, final_tz = parse_date_in_tz(tz)
    items = build_feed(today, days, feed)
    if not items:
        raise HTTPException(404, detail=f"No quotes in feed '{feed}'.")
    return {"tz": final_tz, "days": days, "feed": feed, "items": items}

@app.post("/v1/submit", response_model=SubmitResult)
def submit(q: QuoteIn, auto_store: bool = True):
    """
    Submit a quote. If tag != 'bible', it's treated as 'community' (Bible is reserved for scripture).
    We run your moderation.validate_quote. If accepted and not a duplicate, we append to quotes_approved.json.
    """
    # Map non-bible to community (respect your bible-first design)
    tag_norm = normalize(q.tag)
    effective = q.model_dump()
    if tag_norm != "bible":
        effective = {**effective, "orig_tag": q.tag, "tag": "community"}

    ok, reasons = validate_quote(effective)
    if not ok:
        return SubmitResult(accepted=False, reasons=reasons)

    # Deduplicate
    approved = load_approved_quotes()
    existing = {key_for(item) for item in approved}
    k = key_for(effective)
    if k in existing:
        # Treat as accepted but duplicate (no write)
        return SubmitResult(accepted=True, stored_as=normalize(effective["tag"]))

    if auto_store:
        approved.append(effective)
        save_approved_quotes(approved)

    return SubmitResult(accepted=True, stored_as=normalize(effective["tag"]))
