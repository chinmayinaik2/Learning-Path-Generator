import sqlite3
import bcrypt

def init_user_db():
    """Initializes the database and creates all necessary tables if they don't exist."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    # Users table with secret question/answer for password recovery
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            secret_question TEXT,
            secret_answer TEXT
        )
    ''')
    # Learning paths table with a new column to store the total requested duration
    c.execute('''
        CREATE TABLE IF NOT EXISTS learning_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            topic TEXT NOT NULL,
            path_data TEXT NOT NULL,
            total_duration_text TEXT, -- NEW: To store the original time input like "90 days"
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
    # Task Progress Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS task_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            path_id INTEGER NOT NULL,
            task_identifier TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0, -- 0 for not completed, 1 for completed
            UNIQUE(username, path_id, task_identifier),
            FOREIGN KEY (username) REFERENCES users (username),
            FOREIGN KEY (path_id) REFERENCES learning_paths (id)
        )
    ''')
    conn.commit()
    conn.close()

# --- User Management ---
def add_user(username, password, question, answer):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_answer = bcrypt.hashpw(answer.lower().encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (username, password, secret_question, secret_answer) VALUES (?, ?, ?, ?)", 
                  (username, hashed_password, question, hashed_answer))
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

def user_exists(username):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

# --- Password Reset ---
def get_secret_question(username):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT secret_question FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def check_secret_answer(username, answer):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT secret_answer FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(answer.lower().encode('utf-8'), result[0]):
        return True
    return False

def reset_password(username, new_password):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
    conn.commit()
    conn.close()

# --- Learning Path Management ---
def save_path(username, topic, path_data, time_period_text):
    """Saves a new learning path, including the original requested time frame."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO learning_paths (username, topic, path_data, total_duration_text) VALUES (?, ?, ?, ?)",
              (username, topic, path_data, time_period_text))
    conn.commit()
    conn.close()

def get_user_paths(username):
    """Retrieves all paths for a user, including the total duration text."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT id, topic, path_data, total_duration_text FROM learning_paths WHERE username = ?", (username,))
    paths = c.fetchall()
    conn.close()
    return paths

def update_path_data(path_id, new_path_data):
    """Updates the JSON data for an existing learning path."""
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("UPDATE learning_paths SET path_data = ? WHERE id = ?", (new_path_data, path_id))
    conn.commit()
    conn.close()

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

# --- Task Progress Management ---
def update_task_status(username, path_id, task_identifier, completed):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    status = 1 if completed else 0
    c.execute("INSERT OR REPLACE INTO task_progress (username, path_id, task_identifier, completed) VALUES (?, ?, ?, ?)",
              (username, path_id, task_identifier, status))
    conn.commit()
    conn.close()

def get_task_statuses_for_path(username, path_id):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT task_identifier, completed FROM task_progress WHERE username = ? AND path_id = ?",
              (username, path_id))
    statuses = dict(c.fetchall())
    conn.close()
    return statuses

# --- Admin Functions ---
def get_all_feedback_with_details():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        SELECT f.username, lp.topic, f.rating
        FROM feedback f JOIN learning_paths lp ON f.path_id = lp.id
    ''')
    feedback_details = c.fetchall()
    conn.close()
    return feedback_details
