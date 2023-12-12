DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS feed;
DROP TABLE IF EXISTS article;

CREATE TABLE category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    show_in_main BOOL
);

CREATE TABLE feed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, 
    url  TEXT NOT NULL,
    category_id INTEGER,
    FOREIGN KEY(category_id) REFERENCES category(id)
);

CREATE TABLE article (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    read BOOL,
    date_published DATETIME,
    date_fetched DATETIME,
    feed_id INTEGER NOT NULL,
    FOREIGN KEY(feed_id) REFERENCES feed(id)
);