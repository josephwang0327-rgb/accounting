import sqlite3
from datetime import datetime
import psycopg2
import os

def init_db():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
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
        "INSERT INTO transactions (category, amount, note, created_at) VALUES (%s, %s, %s, %s)",
        (category, amount, note, now)
    )
    conn.commit()
    conn.close()

def get_daily_total(date_str):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(
        "SELECT SUM(amount) FROM transactions WHERE DATE(created_at) = %s",
        (date_str,)
    )
    total = cur.fetchone()[0] or 0
    conn.close()
    return total

def get_transactions(date_str):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(
        "SELECT category, amount, note, created_at FROM transactions WHERE DATE(created_at) = %s ORDER BY created_at ASC",
        (date_str,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_one_day_transactions(date_str):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(
        "SELECT category, amount, note, created_at FROM transactions WHERE DATE(created_at) = %s ORDER BY created_at ASC",
        (date_str,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_this_month():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(
        "SELECT category, amount, note, created_at FROM transactions WHERE DATE_TRUNC('month', created_at::timestamp) = DATE_TRUNC('month', CURRENT_DATE) ORDER BY created_at ASC"
    )
    rows = cur.fetchall()
    cur.execute(
        "SELECT SUM(amount) FROM transactions WHERE DATE_TRUNC('month', created_at::timestamp) = DATE_TRUNC('month', CURRENT_DATE)"
    )
    total = cur.fetchone()[0] or 0#
    conn.close()
    return rows, total

'''def get_this_month_total():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    # 同樣需要將 created_at 強制轉型為 timestamp
    cur.execute(
        "SELECT SUM(amount) FROM transactions WHERE DATE_TRUNC('month', created_at::timestamp) = DATE_TRUNC('month', CURRENT_DATE)"
    )
    total = cur.fetchone()[0] or 0
    conn.close()
    return total'''

def get_one_month_transactions(month_str):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    # 關鍵：將 TEXT 轉為 TIMESTAMP，並將輸入補齊為 YYYY-MM-01
    query = """
        SELECT category, amount, note, created_at 
        FROM transactions 
        WHERE DATE_TRUNC('month', created_at::timestamp) = DATE_TRUNC('month', %s::date) 
        ORDER BY created_at ASC
    """
    # 補齊日期，例如將 "2023-10" 變成 "2023-10-01"
    formatted_month = f"{month_str}-01" 
    cur.execute(query, (formatted_month,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_one_month_total(month_str):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(
        "SELECT SUM(amount) FROM transactions WHERE DATE_TRUNC('month', created_at::timestamp) = DATE_TRUNC('month', %s::date)",
        (month_str,)
    )
    total = cur.fetchone()[0] or 0
    conn.close()
    return total