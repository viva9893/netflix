import sqlite3

def setup_database():
    """Setup Netflix database with popular anime data."""
    conn = sqlite3.connect('netflix_system.db')
    cursor = conn.cursor()

    print("Cleaning up old data...")
    cursor.execute("DROP TABLE IF EXISTS catalog")
    
    print("Creating catalog table...")
    cursor.execute('''CREATE TABLE IF NOT EXISTS catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        creator TEXT NOT NULL,
        media_type TEXT NOT NULL,
        views INTEGER DEFAULT 0
    )''')

    print("Seeding popular anime data...")
    anime_data = [
        ('Naruto', 'Studio Pierrot', 'Anime', 5420),
        ('Attack on Titan', 'Wit Studio', 'Anime', 8932),
        ('Death Note', 'Madhouse', 'Anime', 7654),
        ('One Piece', 'Toei Animation', 'Anime', 9215),
        ('My Hero Academia', 'Bones', 'Anime', 6843),
        ('Demon Slayer', 'ufotable', 'Anime', 8765),
        ('Jujutsu Kaisen', 'MAPPA', 'Anime', 7532),
        ('Steins;Gate', 'White Fox', 'Anime', 5421),
        ('Code Geass', 'Sunrise', 'Anime', 6123),
        ('Fullmetal Alchemist: Brotherhood', 'Bones', 'Anime', 9001),
        ('Neon Genesis Evangelion', 'GAINAX', 'Anime', 5678),
        ('Cowboy Bebop', 'Sunrise', 'Anime', 7890),
        ('Dragon Ball Z', 'Toei Animation', 'Anime', 8234),
        ('Bleach', 'Studio Pierrot', 'Anime', 6543),
        ('Tokyo Ghoul', 'Studio Pierrot', 'Anime', 7234),
    ]
    
    cursor.executemany(
        "INSERT INTO catalog (title, creator, media_type, views) VALUES (?, ?, ?, ?)", 
        anime_data
    )
    
    conn.commit()
    conn.close()
    print(" Database 'netflix_system.db' is refreshed and ready!")
    print(f"Added {len(anime_data)} popular anime titles")

if __name__ == "__main__":
    setup_database()
