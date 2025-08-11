import sqlite3
import bcrypt

# --- Database Initialization ---
def init_user_db():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    # Create learning_paths table
    c.execute('''
        CREATE TABLE IF NOT EXISTS learning_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            topic TEXT NOT NULL,
            path_data TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    # --- NEW: Create feedback table ---
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

# --- User Management (No Changes Needed) ---
def add_user(username, password):
    # ... same as before
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError: # Username already exists
        return False
    finally:
        conn.close()


def check_user(username, password):
    # ... same as before
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        return True
    return False


# --- Learning Path Management (No Changes Needed) ---
def save_path(username, topic, path_data):
    # ... same as before
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO learning_paths (username, topic, path_data) VALUES (?, ?, ?)", (username, topic, path_data))
    conn.commit()
    conn.close()


def get_user_paths(username):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    # IMPORTANT: We now need the path ID to link feedback
    c.execute("SELECT id, topic, path_data FROM learning_paths WHERE username = ?", (username,))
    paths = c.fetchall()
    conn.close()
    return paths

# --- NEW: Feedback Functions ---
def add_feedback(path_id, username, rating):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    try:
        # 'INSERT OR REPLACE' will add a new rating or update an existing one
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