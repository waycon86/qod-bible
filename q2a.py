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
    {"text": "Agent Smith: You must be able to see it, Mr. Anderson. You must know it by now. You can't win. It's pointless to keep fighting. Why, Mr. Anderson? Why? Why do you persist? \nNeo: Because I choose to.", "author": "The Matrix", "tag": "movies"},
    {"text": "You are a god among insects. Never let anyone tell you different.", "author": "Magneto", "tag": "movies"},
    {"text": "The gods envy us. They envy us because we are mortal, because any moment might be our last. Everything is more beautiful because we’re doomed. You will never be lovelier than you are now. We will never be here again.", "author": "Achilles", "tag": "movies"},
    {"text": "Shoot for the moon. Even if you miss, you’ll land among the stars.", "author": "Les Brown", "tag": "motivation"},
    {"text": "Too many of us are not living our dreams because we are living our fears.", "author": "Les Brown", "tag": "fear"},
    {"text": "It’s not over until you win.", "author": "Les Brown", "tag": "perseverance"},
    {"text": "You don’t have to be great to get started, but you have to get started to be great.", "author": "Les Brown", "tag": "action"},
    {"text": "Other people’s opinion of you does not have to become your reality.", "author": "Les Brown", "tag": "self-belief"},
]

def pick_for_date(date,items):
    n = len(items)
    index = date.toordinal() % n
    return items[index]

def main():
    parser = argparse.ArgumentParser(description="Quote of the Day (deterministic)")
    parser.add_argument("--tag", help="filter by tag (e.g. bible, movies)")
    args = parser.parse_args()
    
    pool = QUOTES
    if args.tag:
        filtered = [q for q in QUOTES if q.get("tag", "").lower() == args.tag.lower()]
        if not filtered:
            print(f"(no matches for tag '{args.tag}', using all quotes)")
        pool = filtered or QUOTES
        
    
    today = datetime.date.today()
    q = pick_for_date(today, pool)
    print(f"{today} — {q['text']} — {q['author']} [{q.get('tag','')}]")
if __name__ == "__main__":
    main()