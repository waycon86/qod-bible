import re
from typing import Tuple, List, Dict

URL_RE = re.compile(r"https?://|www\.", re.I)
EMAIL_RE = re.compile(r"[AZ0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)

ALLOWED_TAGS = {
    "bible", "movies", "tech", "inspiration", "motivation",
    "fear", "perseverance", "action", "self-belief", "star wars"
}

#Keep this small and SFW in the repo. Expand privately if needed.
BANNED_WORDS = {
    # examples / plaxeholders - replace with whatever you consider disallowed
    "kill yourself", "suicide",
    # add profanity/explicit words you want to block, one per string
}

def normalize(s: str) -> str:
    return " ".join(s.lower().split())

def _find_banned(text: str) -> Lost[str]:
    t = normalize(text)
    return [w for w in BANNED_WORDS if w in t]

def validate_quote(q: Dict) -> Tuple[bool, List[str]]:
    """Require keys: text, author, tag. Return (ok, reasons)."""
    reasons = List[str]=[]
    
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
    
    # Length gates (tune as you like)
    if len(text) < 4:
        reasons.append("text too short")
    if len(text) > 500:
        reasons.append("text too long")
    if len(author) > 120:
        reasons.append("author too long")
        

    # No links / emails
    if URL_RE.search(text):
        reasons.append("text URL")
        if URL_RE.search(author):
            reasons.append("author URL")
    if EMAIL_RE.search(text):
        reasons.append("contains email address")
        
    # All-caps shouting (letters only)
    letters = [c for c in text if c.isalpha()]
    if letters and all(c.isupper() for c in letters) and len(letters) >= 6:
        reasons.append("text looks like all-caps")
    
    # Very low word variety (spammy)
    words  = text.lower().split()
    if len(words) >= 6 and len(set(words)) <= 3:
        reasons.append("too repetitive/low variety")
    
    # Banned words/phrases
    hits = _find_banned(text)
    if hits:
        reasons.append("banned content: {', '.join(sorted(set)hits)))}")
        
    #hits = _find_banned(author)
    if hits:
        reasons.append(f"banned content: {', '.join(sorted(set(hits)))}")
        
    # Tag Whitelist
    if normalize(tag) not in ALLOWED_TAGS:
        reasons.append(f"tag not allowed: '{tag}' (allowed: {', '.join(sorted(ALLOWED_TAGS))})")
        
    return (len(reasons) == 0), reasons