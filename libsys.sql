CREATE TABLE IF NOT EXISTS titles(
id INTEGER PRIMARY KEY,
title TEXT NOT NULL,
author TEXT NOT NULL,
pub_year INTEGER,
isbn TEXT UNIQUE,
created_at TEXT,
updated_at TEXT
);

CREATE TABLE IF NOT EXISTS members (
id INTEGER PRIMARY KEY,
full_name TEXT NOT NULL,
email_address TEXT NOT NULL UNIQUE,
phone_number TEXT,
is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active in(0,1))
);

CREATE TABLE IF NOT EXISTS copies (
id INTEGER PRIMARY KEY,
title_id INTEGER NOT NULL,
FOREIGN KEY (title_id) REFERENCES titles(id),
status TEXT NOT NULL CHECK (status in ('available','on_loan','lost','withdrawn')) DEFAULT 'available'
);

CREATE TABLE IF NOT EXISTS loans (
id INTEGER PRIMARY KEY,
copy_id INTEGER NOT NULL,
FOREIGN KEY (copy_id) REFERENCES copies(id),
member_id INTEGER NOT NULL,
FOREIGN KEY (member_id) REFERENCES members(id),
loaned_at TEXT NOT NULL,
due_at TEXT NOT NULL,
returned_at TEXT,
renewals_count INTEGER NOT NULL DEFAULT 0
);

Then loans (fk to copies + members; loaned_at, due_at, returned_at, renewals_count).

Add two indexes on titles: (title) and (author).