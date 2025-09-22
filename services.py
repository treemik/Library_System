from datetime import datetime, timedelta
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
        (tit_id,)
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
    except IntegrityError:
        return None

def search_book(conn,*,title):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id,title FROM titles WHERE title LIKE ? COLLATE NOCASE",
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

def search_member(conn,*,email,phone,name):
    cursor = conn.cursor()
    results=[]
    seen =set()
    if email:
        cursor.execute(
            "SELECT id, full_name, phone_number, email_address, is_active FROM members WHERE email_address=? COLLATE NOCASE AND is_active=1 LIMIT 1",
            (email,)
        )
        row_email = cursor.fetchall()
        if row_email:
            for member_id, member_name, member_phone, member_email, active in row_email:
                results.append({'id':member_id,'name':member_name,'phone':member_phone,'email':member_email,'active':active})
            return results


    if phone:
        cursor.execute(
            "SELECT id, full_name, phone_number, email_address, is_active FROM members WHERE phone_number=? AND is_active=1 ORDER BY full_name ASC LIMIT 25",
            (phone,)
        )
        row_phone_number = cursor.fetchall()
        for member_id, member_name, member_phone, member_email, active in row_phone_number:
            if member_id not in seen:
                seen.add(member_id)
                results.append({'id': member_id, 'name': member_name, 'phone': member_phone, 'email': member_email, 'active': active})

    if name:
        cursor.execute(
            "SELECT id, full_name, phone_number, email_address, is_active FROM members WHERE full_name LIKE ? COLLATE NOCASE AND is_active=1 ORDER BY full_name ASC LIMIT 25",
            ("%"+name+"%",)
        )
        row_name = cursor.fetchall()
        for member_id, member_name, member_phone, member_email, active in row_name:
            if member_id not in seen:
                seen.add(member_id)
                results.append({'id': member_id, 'name': member_name, 'phone': member_phone, 'email': member_email, 'active': active})

    return results


def add_copy(conn,*,book_id,quantity):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM titles WHERE id = ?",
        (book_id,)
    )
    row = cursor.fetchone()
    if row is None:
        return book_id,0

    else:
        title_id = row[0]
        cursor.executemany(
            "INSERT INTO copies (title_id) values(?)",
            [(title_id,)] * quantity,
        )
        return title_id,quantity
def loan_book(conn,*,title_id,member_id,days):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM titles WHERE id = ?",
        (title_id,)
    )
    book_row = cursor.fetchone()
    if book_row is None:
        return {'ok':False,'error':'NO_SUCH_TITLE'}

    cursor.execute(
        "SELECT id FROM members WHERE id = ? AND is_active=1 LIMIT 1",
        (member_id,)
    )
    member_row=cursor.fetchone()
    if member_row is None:
        return {'ok':False,'error':'NO_SUCH_MEMBER'}

    cursor.execute(
        "SELECT id FROM copies WHERE title_id = ? AND status='available' ORDER BY id LIMIT 1",
        (book_row[0],)
    )
    copy_row = cursor.fetchone()
    if copy_row is None:
        return {'ok':False,'error':'NO_COPIES_AVAILABLE'}

    cursor.execute(
        "UPDATE copies SET status ='on_loan' WHERE id=? AND status='available'",
        (copy_row[0],)
    )
    if cursor.rowcount==0:
        return {'ok':False,'error':'RACE_LOST'}

    loan_date=datetime.now()
    due=(loan_date+timedelta(days=days)).strftime("%Y-%m-%d")
    loaned_at=loan_date.strftime("%Y-%m-%d")
    try:
        cursor.execute(
            "INSERT INTO loans (copy_id, member_id, loaned_at, due_at) VALUES(?,?,?,?)",
            (copy_row[0],member_id,loaned_at,due)
        )
    except IntegrityError:
        cursor.execute(
            "UPDATE copies SET status = 'available' WHERE id = ?",
            (copy_row[0],)
        )
        return {'ok':False,'error':'DB_ERROR'}
    loan_id=cursor.lastrowid
    results={'ok':True,'data':{'loan_id':loan_id,'title_id': book_row[0],'member_id': member_row[0],'copy_id':copy_row[0],'loaned_at':loaned_at,'due':due}}
    return results


def return_book(conn,*,loan_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT copy_id,returned_at FROM loans WHERE id=?",
        (loan_id,)
    )
    row=cursor.fetchone()
    if row is None:
        return {'ok':False,'error':'NO_SUCH_LOAN'}
    copy_id=row[0]
    returned_at=row[1]
    if returned_at:
        return {'ok':False,'error':'ALREADY_RETURNED','returned_at':returned_at}
    return_date=datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "UPDATE loans SET returned_at = ? WHERE id=? ",
        (return_date,loan_id)
    )

    cursor.execute(
        "UPDATE copies SET status = 'available' WHERE id=? AND status='on_loan'",
        (copy_id,)
    )
    return {'ok':True,'data':{'copy_id':copy_id,'return_date':return_date}}

def search_loan(conn,*,member_id,title_id):
    cursor = conn.cursor()
    results=[]
    if member_id is not None:
        cursor.execute(
            "SELECT id FROM loans WHERE member_id=? AND returned_at IS NULL",
            (member_id,)
        )
        row=cursor.fetchall()
        if not row:
            return {'ok':False,'error':'MEMBER_HAS_NO_LOANS'}
        for loan, in row:
            results.append(loan)
        return {'ok':True,'data':results}


    elif title_id is not None:
        cursor.execute(
            "SELECT id FROM copies WHERE title_id=? AND status='on_loan'",
            (title_id,)
        )
        copy_row=cursor.fetchall()
        if not copy_row:
            return {'ok':False,'error':'TITLE_NOT_ON_LOAN'}
        for copy_id, in copy_row:
             cursor.execute(
                 "SELECT id FROM loans WHERE copy_id=? AND returned_at IS NULL",
                 (copy_id,)
             )
             loan_row=cursor.fetchall()

             for loan, in loan_row:
                 results.append(loan)
        if not results:
            return {'ok': False, 'error': 'NO_COPIES_ON_LOAN'}
        return {'ok':True,'data':results}

def check_overdue_loans(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id,copy_id,member_id,loaned_at, due_at FROM loans WHERE returned_at IS NULL",
    )
    row=cursor.fetchall()
    if not row:
        return {'ok':False,'error':'NO_ACTIVE_LOANS'}
    results=[]
    for loan_id,copy_id,member_id,loaned_at,due_at in row:
        today=datetime.now()
        due=datetime.strptime(due_at,"%Y-%m-%d")
        if today > due:
            results.append({'loan_id':loan_id,'copy_id':copy_id,'member_id':member_id,'loaned_at':loaned_at,'due_at':due_at})
    return {'ok':True,'data':results}










