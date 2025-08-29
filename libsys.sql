CREATE TABLE IF NOT EXISTS titles(
id INTEGER PRIMARY KEY,
title TEXT NOT NULL,
author TEXT NOT NULL,
pub_year INTEGER,
isbn TEXT UNIQUE,
created_at TEXT,
updated_at TEXT
)