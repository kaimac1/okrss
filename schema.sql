DROP TABLE IF EXISTS category;
--DROP TABLE IF EXISTS feed;
DROP TABLE IF EXISTS article;

CREATE TABLE category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    show_in_main BOOL
);

CREATE TABLE IF NOT EXISTS feed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, 
    url  TEXT NOT NULL,
    site_url TEXT NOT NULL,
    category_id INTEGER,
    FOREIGN KEY(category_id) REFERENCES category(id)
);

CREATE TABLE article (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- db id
    post_id TEXT NOT NULL, -- id given in the feed
    title TEXT NOT NULL,
    url TEXT,
    read BOOL,
    summary TEXT,
    content TEXT,
    date_published TIMESTAMP,
    date_fetched TIMESTAMP,
    feed_id INTEGER NOT NULL,
    UNIQUE(feed_id, post_id) ON CONFLICT IGNORE,
    FOREIGN KEY(feed_id) REFERENCES feed(id)
)