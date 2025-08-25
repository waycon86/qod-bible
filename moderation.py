# moderation.py
import re
from typing import Tuple, List, Dict, Optional

# Regex: "Book Chapter:Verse" with optional translation in parentheses.
REF_RE = re.compile(
    r"""^\s*
        (?P<book>(?:[1-3]\s*)?[A-Za-z][A-Za-z\s]+?)   # Book, e.g., 'John', '1 John'
        \s+
        (?P<chap>\d+)
        :
        (?P<verse>\d+)
        \s*
        (?:\((?P<trans>[A-Za-z0-9\-]+)\))?            # optional (KJV), (ESV), etc.
        \s*$
    """,
    re.X,
)

# Basic list – expand any time
KNOWN_BOOKS = {
    "genesis", "exodus", "leviticus", "numbers", "deuteronomy",
    "joshua", "judges", "ruth", "1 samuel", "2 samuel",
    "1 kings", "2 kings", "1 chronicles", "2 chronicles",
    "ezra", "nehemiah", "esther", "job", "psalms", "proverbs",
    "ecclesiastes", "song of solomon", "isaiah", "jeremiah",
    "lamentations", "ezekiel", "daniel", "hosea", "joel",
    "amos", "obadiah", "jonah", "micah", "nahum", "habakkuk",
    "zephaniah", "haggai", "zechariah", "malachi",
    "matthew", "mark", "luke", "john", "acts",
    "romans", "1 corinthians", "2 corinthians",
    "galatians", "ephesians", "philippians",
    "colossians", "1 thessalonians", "2 thessalonians",
    "1 timothy", "2 timothy", "titus", "philemon",
    "hebrews", "james",
    "1 peter", "2 peter",
    "1 john", "2 john", "3 john",
    "jude", "revelation",
}

URL_RE = re.compile(r"https?://|www\.", re.I)
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)

# Bible is default; community is for non‑Bible user submissions
ALLOWED_TAGS = {"bible", "community"}

# Keep repo-safe; expand privately if you like
BANNED_WORDS = {
    "kill yourself", "suicide",
    # add profanity/explicit terms you disallow
}

def normalize(s: str) -> str:
    return " ".join(s.lower().split())

def _norm_ref_book(name: str) -> str:
    return " ".join(name.lower().split())

def parse_scripture_reference(author_field: str) -> Optional[Tuple[str, int, int, Optional[str]]]:
    """Parse 'Book C:V (TRANS)' from the author field; return (book, chap, verse, trans) or None."""
    m = REF_RE.match(author_field or "")
    if not m:
        return None
    book = _norm_ref_book(m.group("book"))
    chap = int(m.group("chap"))
    verse = int(m.group("verse"))
    trans = m.group("trans")
    return (book, chap, verse, trans)

def _find_banned(text: str) -> List[str]:
    t = normalize(text)
    return [w for w in BANNED_WORDS if w in t]

def validate_quote(q: Dict) -> Tuple[bool, List[str]]:
    """Require keys: text, author, tag. Return (ok, reasons)."""
    reasons: List[str] = []

    if not isinstance(q, dict):
        return False, ["not an object"]

    text = q.get("text", "")
    author = q.get("author", "")
    tag = q.get("tag", "")

    # Basic presence
    if not isinstance(text, str) or not text.strip():
        reasons.append("missing/empty text")
    if not isinstance(author, str) or not author.strip():
        reasons.append("missing/empty author")
    if not isinstance(tag, str) or not tag.strip():
        reasons.append("missing/empty tag")
    if reasons:
        return False, reasons

    # Length gates
    if len(text) < 4:
        reasons.append("text too short")
    if len(text) > 500:
        reasons.append("text too long")
    if len(author) > 120:
        reasons.append("author too long")

    # No links/emails in text
    if URL_RE.search(text):
        reasons.append("contains URL")
    if EMAIL_RE.search(text):
        reasons.append("contains email address")

    # All-caps shouting
    letters = [c for c in text if c.isalpha()]
    if letters and all(c.isupper() for c in letters) and len(letters) >= 6:
        reasons.append("text looks like all-caps shouting")

    # Low variety / spammy
    words = text.lower().split()
    if len(words) > 6 and len(set(words)) <= 3:
        reasons.append("too repetitive/low variety")

    # Banned words/phrases (in text or author)
    hits_text = _find_banned(text)
    hits_author = _find_banned(author)
    hits = sorted(set(hits_text + hits_author))
    if hits:
        reasons.append(f"banned content: {', '.join(hits)}")

    # Tag whitelist
    tag_norm = normalize(tag)
    if tag_norm not in ALLOWED_TAGS:
        reasons.append(f"tag not allowed: '{tag}' (allowed: {', '.join(sorted(ALLOWED_TAGS))})")

    # Bible-specific: author must look like a scripture reference
    if tag_norm == "bible":
        parsed = parse_scripture_reference(author)
        if not parsed:
            reasons.append("invalid scripture reference in author (expected 'Book C:V', e.g. 'John 3:16 (KJV)')")
        else:
            book, chap, verse, trans = parsed
            if book not in KNOWN_BOOKS:
                sample = ", ".join(sorted(list(KNOWN_BOOKS)[:6])) + " …"
                reasons.append(f"unknown scripture book: '{book}' (sample known: {sample})")
            if chap <= 0 or verse <= 0:
                reasons.append("chapter and verse must be positive integers")

    return (len(reasons) == 0), reasons
