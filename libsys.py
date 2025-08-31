import sqlite3

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


