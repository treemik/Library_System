from datetime import datetime
from helper_functions import normalize_and_dedupe

def add_book(conn,*,title,authors,pub_year,isbn):
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d")
    pairs=normalize_and_dedupe(authors)
    cursor.execute(
        "INSERT INTO titles (title,pub_year,isbn,created_at)VALUES(?,?,?,?)",
        (title, pub_year, isbn, created_at)
    )
    tit_id = cursor.lastrowid
    for order, (display, normalized) in enumerate(pairs, start=1):
        cursor.execute(
            "INSERT INTO authors(full_name,normalized_name)VALUES(?,?) ON CONFLICT (normalized_name) DO UPDATE SET full_name=excluded.full_name",
            (display, normalized)
        )
        aut_id = cursor.execute("SELECT id FROM authors WHERE normalized_name=?", (normalized,)).fetchone()[0]

        cursor.execute(
            "INSERT OR IGNORE INTO title_authors(title_id,author_id,author_order)VALUES(?,?,?)",
            (tit_id, aut_id, order)
        )
    return tit_id