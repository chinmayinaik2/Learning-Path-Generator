import sqlite3
import bcrypt

def init_user_db():
    """Initializes the database and creates all necessary tables if they don't exist."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    # Learning paths table
    c.execute('''
        CREATE TABLE IF NOT EXISTS learning_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            topic TEXT NOT NULL,
            path_data TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    # Feedback table
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            rating INTEGER NOT NULL, -- 1 for helpful, -1 for not helpful
            UNIQUE(path_id, username),
            FOREIGN KEY (path_id) REFERENCES learning_paths (id),
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()

# --- User Management ---
def add_user(username, password):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        return True
    return False

# --- Learning Path Management ---
def save_path(username, topic, path_data):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO learning_paths (username, topic, path_data) VALUES (?, ?, ?)", (username, topic, path_data))
    conn.commit()
    conn.close()

def get_user_paths(username):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT id, topic, path_data FROM learning_paths WHERE username = ?", (username,))
    paths = c.fetchall()
    conn.close()
    return paths

# --- Feedback Management ---
def add_feedback(path_id, username, rating):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO feedback (path_id, username, rating) VALUES (?, ?, ?)", (path_id, username, rating))
        conn.commit()
    finally:
        conn.close()

def get_feedback(path_id, username):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT rating FROM feedback WHERE path_id = ? AND username = ?", (path_id, username))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# --- Admin Functions ---
def get_all_feedback_with_details():
    """Joins feedback and learning_paths tables to get a full report."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        SELECT 
            f.username,
            lp.topic,
            f.rating
        FROM feedback f
        JOIN learning_paths lp ON f.path_id = lp.id
    ''')
    feedback_details = c.fetchall()
    conn.close()
    return feedback_details
