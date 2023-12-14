from flask import Flask, request, g, render_template, redirect, url_for
import sqlite3
import click
import feedparser
import datetime
from time import mktime
from functools import wraps
import cfg

@click.command('initdb')
def init_db():
    db = sqlite3.connect(cfg.database, detect_types=sqlite3.PARSE_DECLTYPES)
    with open('schema.sql') as f:
        db.executescript(f.read())

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(cfg.database, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


app = Flask(__name__)
app.teardown_appcontext(close_db)
app.cli.add_command(init_db)


# HTTP basic auth
def check_auth(user, password):
    return (user == cfg.username and password == cfg.password)
def auth(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        auth = request.authorization
        if not (auth and check_auth(auth.username, auth.password)):
            return ('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required'})
        return f(**kwargs)
    return wrapped_view


# Add a feed to the database
def feed_add(url):
    feed = feedparser.parse(url)
    title = feed.feed.title
    link = feed.feed.link
    print(f'Fetched feed "{title}" ({link})')
    db = get_db()
    db.execute('INSERT INTO feed (name, url, site_url) VALUES (?, ?, ?)', (title, url, link))
    db.commit()

# Pull a feed and add the latest articles to the database
def feed_pull(feed_id, feed_url):
    print(f'Pulling articles for "{feed_url}"..')
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        post_id = entry.id
        title = entry.get('title') or '[no title]'
        url = entry.get('link') or ''

        MAX_SUMMARY_LEN = 250

        # If there is 'content' then this will be the full article
        #   The summary may also be the full article, or an actual summary
        # If 'content' is missing then the whole article is in the summary
        summary = entry.get('summary') or ''
        if entry.get('content') and len(entry['content']) > 0:
            content = entry['content'][0].value
        else:
            content = summary
        if len(summary) > MAX_SUMMARY_LEN:
            summary = summary[0:MAX_SUMMARY_LEN] + '...'

        date_published = datetime.datetime.fromtimestamp(mktime(entry.published_parsed))
        date_fetched = datetime.datetime.now() #timezone?

        db = get_db()
        db.execute("""INSERT INTO article (post_id, title, url, read, summary, content, date_published, date_fetched, feed_id)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                    (post_id, title, url, False, summary, content, date_published, date_fetched, feed_id))
        db.commit()


@app.route("/")
@auth
def home():
    items = []
    db = get_db()
    articles = db.execute('SELECT * from article ORDER BY date(date_published) DESC').fetchall()
    for row in articles:
        item = {}
        item['title'] = row['title']
        item['feed'] = db.execute('SELECT name from feed WHERE id = ?', (row['feed_id'],)).fetchone()['name']
        item['date'] = row['date_published'].strftime('%d %b %Y')
        item['time'] = row['date_published'].strftime('%H:%M')
        item['summary'] = row['summary']
        item['content'] = row['content']
        item['id'] = row['id']
        items.append(item)
    
    return render_template('index.html', items=items)

@app.route("/addfeed", methods=('GET', 'POST'))
@auth
def add_feed():
    if request.method == 'POST':
        url = request.form['url']
        feed_add(url)
        return redirect(url_for("home"))

    return render_template('addfeed.html')

@app.route("/refresh")
@auth
def refresh_feeds():
    db = get_db()
    feeds = db.execute('SELECT * from feed').fetchall()
    for row in feeds:
        feed_pull(row['id'], row['url'])

    return redirect(url_for("home"))

@app.route("/article/<int:artid>")
@auth
def read_article(artid):
    db = get_db()
    row = db.execute('SELECT * from article WHERE id = ?', (artid, )).fetchone()
    print(row)
    data = {}
    data['title'] = row['title']
    data['content'] = row['content']
    return render_template('article.html', data=data)
