# add_quotes.py
import json
import pathlib
from typing import Dict, Tuple
from moderation import validate_quote, normalize

BASE_DIR = pathlib.Path(__file__).parent.resolve()
APPROVED_PATH = BASE_DIR / "quotes_approved.json"
REJECTS_PATH = BASE_DIR / "quotes_rejected.json"

def _load_json_list(path: pathlib.Path, *, required: bool = False):
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Input file not found: {path}")
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must be a JSON list")
    return data

def _save_json_list(path: pathlib.Path, items):
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def _key(q: Dict) -> Tuple[str, str]:
    # normalized (text, author) for duplicate detection
    return (normalize(q.get("text", "")), normalize(q.get("author", "")))

def import_quotes(input_path: str, dry_run: bool = False, debug: bool = False):
    incoming = _load_json_list(pathlib.Path(input_path), required=True)
    approved = _load_json_list(APPROVED_PATH)
    rejects  = _load_json_list(REJECTS_PATH)

    if debug:
        print(f"[debug] incoming items: {len(incoming)}")
        if incoming:
            print(f"[debug] first item: {incoming[0]}")

    approved_keys = {_key(q) for q in approved}

    added = rejected = skipped_dupe = 0
    for q in incoming:
        ok, reasons = validate_quote(q)
        if not ok:
            rejects.append({"quote": q, "reasons": reasons})
            rejected += 1
            continue

        k = _key(q)
        if k in approved_keys:
            skipped_dupe += 1
            continue

        if not dry_run:
            approved.append(q)
            approved_keys.add(k)
        added += 1

    if not dry_run:
        _save_json_list(APPROVED_PATH, approved)
        _save_json_list(REJECTS_PATH, rejects)

    print(f"Approved added: {added}")
    print(f"Rejected: {rejected}")
    print(f"Duplicates skipped: {skipped_dupe}")
    print(f"Approved store: {APPROVED_PATH.name}")
    print(f"Rejected log:  {REJECTS_PATH.name}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Import user quotes with moderation")
    p.add_argument("file", help="Path to JSON file of quotes (list of {text, author, tag})")
    p.add_argument("--dry-run", action="store_true", help="Validate only; do not write files")
    p.add_argument("--debug", action="store_true", help="Print diagnostics")
    args = p.parse_args()
    import_quotes(args.file, dry_run=args.dry_run, debug=args.debug)
