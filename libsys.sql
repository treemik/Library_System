CREATE TABLE IF NOT EXISTS titles(
id INTEGER PRIMARY KEY,
title TEXT NOT NULL,
pub_year INTEGER,
isbn TEXT UNIQUE,
created_at TEXT,
updated_at TEXT
);

CREATE TABLE IF NOT EXISTS authors(
id INTEGER PRIMARY KEY,
full_name TEXT NOT NULL,
normalized_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS title_authors(
title_id INTEGER NOT NULL,
author_id INTEGER NOT NULL,
author_order INTEGER NOT NULL,
FOREIGN KEY (title_id) REFERENCES titles(id) ON DELETE CASCADE,
FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE RESTRICT,
PRIMARY KEY (title_id,author_id)
);

CREATE TABLE IF NOT EXISTS members (
id INTEGER PRIMARY KEY,I
full_name TEXT NOT NULL,
email_address TEXT NOT NULL UNIQUE,
phone_number TEXT,
is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active in(0,1))
);

CREATE TABLE IF NOT EXISTS copies (
id INTEGER PRIMARY KEY,
title_id INTEGER NOT NULL,
status TEXT NOT NULL CHECK (status in ('available','on_loan','lost','withdrawn')) DEFAULT 'available',
FOREIGN KEY (title_id) REFERENCES titles(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS loans (
id INTEGER PRIMARY KEY,
copy_id INTEGER NOT NULL,
member_id INTEGER NOT NULL,
loaned_at TEXT NOT NULL,
due_at TEXT NOT NULL,
returned_at TEXT,
renewals_count INTEGER NOT NULL DEFAULT 0,
FOREIGN KEY (copy_id) REFERENCES copies(id) ON DELETE RESTRICT,
FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE RESTRICT
);

