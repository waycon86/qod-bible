import hashlib, datetime, json, pathlib, sys
QUOTES_PATH = pathlib.Path("quotes.json")

def load_quotes():
    data = json.loads(QUOTES_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list) and data, "quotes.json must be a non-empty list"
    return data

def pick_by_date(date, items):
    h = hashlib.sha256(date.isoformat().encode()).hexdigest()
    return items[int(h, 16) % len(items)]

def main():
    today = datetime.date.today()
    quotes = load_quotes()
    tag = sys.argv[1].lower() if len(sys.argv) > 1 else None
    if tag:
        quotes = [q for q in quotes if q.get("tag","").lower()==tag] or quotes
    q = pick_by_date(today, quotes)
    print(f"{today} — {q['text']} — {q['author']}")

if __name__ == "__main__":
    main()
