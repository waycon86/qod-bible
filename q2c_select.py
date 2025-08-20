import argparse
import datetime

QUOTES = [
    {"text": "Programs must be written for people to read.", "author": "Harold Abelson", "tag": "tech"},
    {"text": "The fear of the LORD is the beginning of wisdom.", "author": "Proverbs 9:10 (KJV)", "tag": "bible"},
    {"text": "Talk is cheap. Show me the code.", "author": "Linus Torvalds", "tag": "tech"},
    {"text": "Jesus wept.", "author": "John 11:35 (KJV)", "tag": "bible"},
    {"text": "Do or do not. There is no try.", "author": "yoda", "tag": "Star Wars"},
    {"text": "Don't let anyone ever make you feel like you don't deserve what you want.", "author": "Heath Ledger", "tag": "inspiration"},
    {"text": "It ain't about how hard you hit, it's about how you can get hit and keep moving forward, how much you can take and keep moving forward. That's how winning is done!", "author": "Rocky Balboa", "tag": "movies"},
    {"text": "Every passing second is another chance to turn it all around", "author": "Vanilla Sky", "tag": "movies"},
    {"text": "Agent Smith: ... Why do you persist?\nNeo: Because I choose to.", "author": "The Matrix", "tag": "movies"},
    {"text": "You are a god among insects. Never let anyone tell you different.", "author": "Magneto", "tag": "movies"},
    {"text": "The gods envy us ... We will never be here again.", "author": "Achilles", "tag": "movies"},
    {"text": "Shoot for the moon. Even if you miss, you’ll land among the stars.", "author": "Les Brown", "tag": "motivation"},
    {"text": "Too many of us are not living our dreams because we are living our fears.", "author": "Les Brown", "tag": "fear"},
    {"text": "It’s not over until you win.", "author": "Les Brown", "tag": "perseverance"},
    {"text": "You don’t have to be great to get started, but you have to get started to be great.", "author": "Les Brown", "tag": "action"},
    {"text": "Other people’s opinion of you does not have to become your reality.", "author": "Les Brown", "tag": "self-belief"},
]

def normalize(s: str) -> str:
    return " ".join(s.lower().split())

def pick_for_date(date, items):
    n = len(items)
    index = date.toordinal() % n
    return items[index]

def available_tags():
    return sorted({normalize(q.get("tag", "")) for q in QUOTES if q.get("tag")})

def filter_by_tags(pool, tags_norm: set[str]):
    return [q for q in pool if normalize(q.get("tag", "")) in tags_norm]

def filter_by_author(pool, author_text: str):
    a = normalize(author_text)
    return [q for q in pool if a in normalize(q.get("author", ""))]

def interactive_choose_tags():
    tags = available_tags()
    print("\nChoose a category (or multiple, comma-separated):")
    for i, t in enumerate(tags, 1):
        print(f"  {i}. {t}")
    choice = input("> ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(tags):
            return {tags[idx]}
    # allow comma-separated names
    picked = {normalize(x) for x in choice.split(",") if x.strip()}
    return picked or set()

def main():
    parser = argparse.ArgumentParser(description="Quote of the Day (with category selection)")
    parser.add_argument("--categories", "--tags", help="comma-separated categories, e.g. 'bible,movies'")
    parser.add_argument("--author", help='filter by author, e.g. "Les Brown"')
    parser.add_argument("--list-categories", action="store_true", help="list available categories and exit")
    parser.add_argument("--debug", action='store_true', help="print diagnostics")
    args = parser.parse_args()

    if args.list_categories:
        print("Available categories:", ", ".join(available_tags()))
        return

    pool = QUOTES
    if args.debug:
        print(f"[debug] start pool size: {len(pool)}")

    # Category selection (one or many)
    if args.categories:
        selected = {normalize(x) for x in args.categories.split(",") if x.strip()}
    else:
        selected = interactive_choose_tags()

    if selected:
        valid = set(available_tags())
        unknown = selected - valid
        if unknown and args.debug:
            print(f"[debug] unknown categories ignored: {sorted(unknown)}")
        wanted = selected & valid
        if wanted:
            filtered = filter_by_tags(pool, wanted)
            if args.debug:
                print(f"[debug] categories={sorted(wanted)} matches: {len(filtered)}")
            if filtered:
                pool = filtered
        if args.debug:
            print(f"[debug] pool size now: {len(pool)}")

    # Optional author filter
    if args.author:
        filtered = filter_by_author(pool, args.author)
        if args.debug:
            print(f"[debug] author contains '{args.author}' matches: {len(filtered)}")
        if filtered:
            pool = filtered
        if args.debug:
            print(f"[debug] pool size now: {len(pool)}")

    if not pool:
        raise SystemExit("No quotes available after filtering.")

    today = datetime.date.today()
    q = pick_for_date(today, pool)
    print(f"{today} — {q['text']} — {q['author']} [{q.get('tag','')}]")

if __name__ == "__main__":
    main()
