import datetime #gives us the current date and time

#A python list of dicts. Start with just 3 so it's easy to see what's happening.
QUOTES = [
    {"text": "Programs must be written for people to read.", "author": "Harold Abelson"},
    {"text": "The fear of the LORD is the beginning of wisdom.", "author": "Proverbs 9:10 (KJV)"},
    {"text": "Talk is cheap. Show me the code.", "author": "Linus Torvalds"},
]

today = datetime.date.today() #get today's date e.g., 2025-01-01
n = len(QUOTES) #get the number of quotes in the list
#date.toordinal() turns a date into an integer(days since a fixed point).
index = today.toordinal() % n #always 0..n-1 repeat every n days
quote = QUOTES[index] #get the quote for today

#print the quote
print(f"{today} - {quote['text']} - {quote['author']}")