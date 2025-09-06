import sqlite3
from datetime import datetime
import argparse
import re
# inits the database
def init_db():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('PRAGMA foreign_keys = ON;')
    c.execute('PRAGMA journal_mode = WAL;')
    with open('libsys.sql') as f:
        data = f.read()
        c.executescript(data)
    c.execute('PRAGMA user_version = 1;')
    conn.commit()
    conn.close()

#connects to the database
class DatabaseContextManager:

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        c = self.conn.cursor()
        c.execute('PRAGMA foreign_keys = ON;')
        c.execute('PRAGMA journal_mode = WAL;')
        c.execute('PRAGMA synchronous = NORMAL;')
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()

def normalize_and_dedupe(authors: list[str]) -> list[tuple[str, str]]:
    seen = set()
    deduped = []
    for author in authors:
        author = author.strip()
        normalized_author =" ".join(author.split()).lower()
        display_and_normalized=(author, normalized_author)
        if normalized_author not in seen:
            seen.add(normalized_author)
            deduped.append(display_and_normalized)
        else:
            continue
    return deduped

#year regex
year_re=re.compile(r"^\s*(\d{4})(?:-(\d{2})(?:-\d{2})?)?\s*$")
def published_type(s: str)->int:
    match = year_re.match(s)
    if not match:
        raise argparse.ArgumentTypeError(f"{s} is not a valid date please enter a vaild date (YYYY-MM-DD OR YYYY-MM OR YYYY)")
    year = int(match.group(1))
    now = int(datetime.now().year)
    if not 1400 <= year <= now+1:
        raise argparse.ArgumentTypeError(f"{year} is not a valid year")
    return year


