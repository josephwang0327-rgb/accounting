import sqlite3
from datetime import datetime
import psycopg2
import os

def init_db():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id SERIAL PRIMARY KEY,
        category TEXT NOT NULL,
        amount INTEGER NOT NULL,
        note TEXT,
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def add_transaction(category, amount, note=None):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(
        "INSERT INTO transactions (category, amount, note, created_at) VALUES (?, ?, ?, ?)",
        (category, amount, note, now)
    )
    conn.commit()
    conn.close()

def get_daily_total(date_str):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(
        "SELECT SUM(amount) FROM transactions WHERE DATE(created_at) = ?",
        (date_str,)
    )
    total = cur.fetchone()[0] or 0
    conn.close()
    return total

def get_transactions(date_str):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(
        "SELECT category, amount, note, created_at FROM transactions WHERE DATE(created_at) = ? ORDER BY created_at ASC",
        (date_str,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows