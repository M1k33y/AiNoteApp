import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/topics.db")

def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

# ---------------------------
# CRUD Topics
# ---------------------------

def create_topic(name, description=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO topics (name, description) VALUES (?, ?)", (name, description))
    conn.commit()
    conn.close()

def get_topics():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM topics ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def update_topic(topic_id, name, description):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE topics SET name=?, description=? WHERE id=?", (name, description, topic_id))
    conn.commit()
    conn.close()

def delete_topic(topic_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM topics WHERE id=?", (topic_id,))
    conn.commit()
    conn.close()

# ---------------------------
# CRUD Notes
# ---------------------------

def create_note(topic_id, title, content):
    conn = get_conn()
    c = conn.cursor()
    created = datetime.now().isoformat()
    c.execute("""
        INSERT INTO notes (topic_id, title, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (topic_id, title, content, created))
    conn.commit()
    conn.close()

def get_notes_by_topic(topic_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM notes WHERE topic_id=? ORDER BY id DESC", (topic_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def update_note(note_id, title, content):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE notes SET title=?, content=? WHERE id=?", (title, content, note_id))
    conn.commit()
    conn.close()

def delete_note(note_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()
