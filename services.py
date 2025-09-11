from datetime import datetime
from sqlite3 import IntegrityError

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

    book_title= cursor.execute(
        "SELECT title FROM titles WHERE id=?",
        tit_id
    ).fetchone()[0]
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
    title_and_author = [tit_id,book_title]
    return title_and_author

def add_author(conn,*,first,last):
    cursor = conn.cursor()
    full_name = " ".join([first,last])
    pair = normalize_and_dedupe([full_name])
    display, normalized = pair[0]
    cursor.execute(
        "INSERT INTO authors(full_name,normalized_name)VALUES(?,?) ON CONFLICT (normalized_name) DO UPDATE SET full_name=excluded.full_name",
        (display, normalized)
    )
    row = cursor.execute(
        "SELECT id, full_name FROM authors WHERE normalized_name=?",
        normalized
    ).fetchone()

    return row

def add_member(conn,*,first,last,email,phone):
    cursor = conn.cursor()
    full_name = " ".join([first,last])
    try:
        cursor.execute(
            "INSERT INTO members (full_name,email_address,phone_number) VALUES(?,?,?)",
            (full_name,email,phone)
        )
        member_id=cursor.lastrowid
        return member_id,full_name
    except IntegrityError as e:
        return None

def search(conn,*,title):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id,title FROM titles WHERE LOWER(title) LIKE LOWER(?)",
        ('%'+title+'%',)
    )
    row = cursor.fetchall()
    if not row:
        return None
    results=[]
    for book_id, book_title in row:
        cursor.execute(
            'SELECT id, status FROM copies WHERE title_id=?',
            (book_id,)
        )
        current=cursor.fetchall()
        total=0
        available=0
        for copies_id, copies_status in current:
            total+=1
            if copies_status=="available":
                available+=1

        results.append({"id":book_id, "title":book_title, "available":available, "total":total})
    return results