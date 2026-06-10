from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DB_FILE = 'netflix_system.db'

def init_db():
    """Initialize the database with the catalog table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create the catalog table for Netflix CRUD if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        creator TEXT NOT NULL,
        media_type TEXT NOT NULL,
        views INTEGER DEFAULT 0
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS device
                        (device_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, account_id INTEGER, device_type TEXT, 
                        device_name TEXT, last_active TIMESTAMP,
                        FOREIGN KEY (account_id) REFERENCES account (account_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS subscription_plan
                        (plan_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, plan_name TEXT, price_monthly REAL, 
                        max_profiles INTEGER, max_simultaneous_streams INTEGER)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS account
                        (account_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, email TEXT, password_hash TEXT, 
                        created_at TIMESTAMP, account_status TEXT, 
                        plan_id INTEGER, country_code TEXT, 
                        preferred_language TEXT,
                        FOREIGN KEY (plan_id) REFERENCES subscription_plan (plan_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS payment
                        (payment_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, account_id INTEGER, amount REAL, 
                        payment_date TIMESTAMP, payment_method TEXT, 
                        status TEXT, plan_id INTEGER,
                        FOREIGN KEY (account_id) REFERENCES account (account_id),
                        FOREIGN KEY (plan_id) REFERENCES subscription_plan (plan_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS language
                        (language_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, language_name TEXT, iso_code TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS profile
                        (profile_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, account_id INTEGER, profile_name TEXT, 
                        avatar_url TEXT, is_kids BOOLEAN, maturity_rating TEXT, 
                        language_id INTEGER,
                        FOREIGN KEY (account_id) REFERENCES account (account_id),
                        FOREIGN KEY (language_id) REFERENCES language (language_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS studio
                        (studio_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, studio_name TEXT, country TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS content
                        (content_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, title TEXT, content_type TEXT, 
                        release_year INTEGER, maturity_rating TEXT, 
                        description TEXT, duration_mins INTEGER, 
                        studio_id INTEGER, is_original BOOLEAN,
                        FOREIGN KEY (studio_id) REFERENCES studio (studio_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS season
                        (season_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, content_id INTEGER, season_number INTEGER, 
                        release_year INTEGER,
                        FOREIGN KEY (content_id) REFERENCES content (content_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS episode
                        (episode_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, season_id INTEGER, episode_number INTEGER, 
                        title TEXT, duration_mins INTEGER,
                        FOREIGN KEY (season_id) REFERENCES season (season_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS video_asset
                        (asset_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, content_id INTEGER, episode_id INTEGER, 
                        resolution TEXT, file_url TEXT, codec TEXT,
                        FOREIGN KEY (content_id) REFERENCES content (content_id),
                        FOREIGN KEY (episode_id) REFERENCES episode (episode_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS genre
                        (genre_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, genre_name TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS content_genre
                        (content_id INTEGER, genre_id INTEGER,
                        PRIMARY KEY (content_id, genre_id),
                        FOREIGN KEY (content_id) REFERENCES content (content_id),
                        FOREIGN KEY (genre_id) REFERENCES genre (genre_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS person
                        (person_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, full_name TEXT, birth_date DATE, 
                        nationality TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS content_person
                        (content_id INTEGER, person_id INTEGER, role_type TEXT,
                        PRIMARY KEY (content_id, person_id),
                        FOREIGN KEY (content_id) REFERENCES content (content_id),
                        FOREIGN KEY (person_id) REFERENCES person (person_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS content_track
                        (track_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, content_id INTEGER, language_id INTEGER, 
                        track_type TEXT,
                        FOREIGN KEY (content_id) REFERENCES content (content_id),
                        FOREIGN KEY (language_id) REFERENCES language (language_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS watch_history
                        (watch_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, profile_id INTEGER, content_id INTEGER, 
                        episode_id INTEGER, watched_at TIMESTAMP, 
                        progress_seconds INTEGER,
                        FOREIGN KEY (profile_id) REFERENCES profile (profile_id),
                        FOREIGN KEY (content_id) REFERENCES content (content_id),
                        FOREIGN KEY (episode_id) REFERENCES episode (episode_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS my_list
                        (list_item_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, profile_id INTEGER, content_id INTEGER, 
                        added_at TIMESTAMP,
                        FOREIGN KEY (profile_id) REFERENCES profile (profile_id),
                        FOREIGN KEY (content_id) REFERENCES content (content_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS rating
                        (rating_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, profile_id INTEGER, content_id INTEGER, 
                        rating_value TEXT, rated_at TIMESTAMP,
                        FOREIGN KEY (profile_id) REFERENCES profile (profile_id),
                        FOREIGN KEY (content_id) REFERENCES content (content_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Authors
                        (author_id INTEGER PRIMARY KEY 
                        AUTOINCREMENT, name TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Books
                        (book_id INTEGER PRIMARY KEY
                        AUTOINCREMENT, title TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Book_Authors
                        (book_id INTEGER, author_id INTEGER,
                        PRIMARY KEY (book_id, author_id),
                        FOREIGN KEY (book_id) REFERENCES Books (book_id),
                        FOREIGN KEY (author_id) REFERENCES Authors
                        (author_id))''')

    conn.commit()
    conn.close()


@app.route('/')
def index():
    """READ: Displays all media items in the catalog."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM catalog")
    media_items = cursor.fetchall()
    conn.close()
    return render_template('index.html', media_items=media_items)


@app.route('/search')
def search():
    """SEARCH: Search for shows by title or creator."""
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM catalog WHERE title LIKE ? OR creator LIKE ? ORDER BY views DESC",
            (f"%{query}%", f"%{query}%")
        )
        results = cursor.fetchall()
        conn.close()
    
    return render_template('search.html', results=results, query=query)


@app.route('/add', methods=['GET', 'POST'])
def add_media():
    """CREATE: Adds a new anime, movie, or show to the database."""
    if request.method == 'POST':
        title = request.form['title']
        creator = request.form['creator']
        media_type = request.form['media_type']
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO catalog (title, creator, media_type) VALUES (?, ?, ?)",
            (title, creator, media_type)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('add_media.html')


@app.route('/watch', methods=['POST'])
def watch_media():
    """UPDATE: Increments the view/stream count of a specific title."""
    media_id = request.form['media_id']
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE catalog SET views = views + 1 WHERE id = ?", (media_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/delete/<int:media_id>')
def delete_media(media_id):
    """DELETE: Removes an item from the catalog."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM catalog WHERE id = ?", (media_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/trending')
def trending():
    """TOP 10 LEADERBOARD: Displays top 10 titles sorted by most views."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM catalog ORDER BY views DESC LIMIT 10")
    stats = cursor.fetchall()
    conn.close()
    return render_template('trending.html', stats=stats)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
