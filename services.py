from datetime import datetime


def add_book(conn,*,title,author,pub_year,isbn):
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d")
    normalized_name = " ".join(author.strip().split()).lower()
    cursor.execute(
        "INSERT INTO titles (title,pub_year,isbn,created_at)VALUES(?,?,?,?)",
        (title, pub_year, isbn, created_at)
    )
    tit_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO authors(full_name,normalized_name)VALUES(?,?) ON CONFLICT (normalized_name) DO UPDATE SET full_name=excluded.full_name",
        (author, normalized_name)
    )
    aut_id = cursor.execute("SELECT id FROM authors WHERE normalized_name=?", (normalized_name,)).fetchone()[0]

    cursor.execute(
        "INSERT OR IGNORE INTO title_authors(title_id,author_id,author_order)VALUES(?,?,?)",
        (tit_id, aut_id, 1)
    )