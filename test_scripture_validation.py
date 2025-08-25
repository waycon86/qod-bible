# qod-bible/test_scripture_validation.py

from moderation import validate_quote

def ok(q):
    good, reasons = validate_quote(q)
    assert good, reasons

def bad(q, contains: str):
    good, reasons = validate_quote(q)
    assert not good and any(contains in r for r in reasons), reasons

def test_bible_reference_ok():
    ok({"text": "For God so loved the world...", "author": "John 3:16", "tag": "bible"})

def test_bible_reference_bad_format():
    bad({"text": "Verse text", "author": "John3:16", "tag": "bible"}, "invalid scripture reference")

def test_bible_unknown_book():
    bad({"text": "Verse text", "author": "Jon 3:16", "tag": "bible"}, "unknown scripture book")

def test_non_bible_skips_ref_rule():
    ok({"text": "Talk is cheap.", "author": "Linus Torvalds", "tag": "community"})
