import sqlite3
from datetime import datetime
import psycopg2
import os

def init_db(db_path):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id SERIAL PRIMARY KEY,
        amount INTEGER,
        category TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_transaction(db_path, purpose, amount, note=None):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(
        "INSERT INTO transactions (purpose, amount, note, created_at) VALUES (?, ?, ?, ?)",
        (purpose, amount, note, now)
    )
    conn.commit()
    conn.close()

def get_daily_total(db_path, date_str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT SUM(amount) FROM transactions WHERE DATE(created_at) = ?",
        (date_str,)
    )
    total = cur.fetchone()[0] or 0
    conn.close()
    return total

def get_transactions(db_path, date_str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT purpose, amount, note, created_at FROM transactions WHERE DATE(created_at) = ? ORDER BY created_at ASC",
        (date_str,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows