import sqlite3
from datetime import datetime

def init_db(db_path):
    conn = sqlite3.connect(db_path)#建立資料庫連線
    cur = conn.cursor()#建立游標
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purpose TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL
        )
    ''')#若不存在，建立資料表
    conn.commit()
    conn.close()

def add_transaction(db_path, purpose, amount, note=None, created_at):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (purpose, amount, note, created_at) VALUES (?, ?, ?, ?)",
        (purpose, amount, note, created_at)
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
    total = cur.fetchone()[0] or 0#如果沒有交易，SUM會回傳None，所以用or 0來確保total是數字
    conn.close()
    return total

def get_transactions(db_path, date_str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT purpose, amount, note, created_at FROM transactions WHERE DATE(created_at) = ? ORDER BY created_at ASC",
        (date_str,)
    )#取得指定日期的所有交易，按照時間排序
    rows = cur.fetchall()#fetchall()會回傳所有符合條件的資料列，格式是list of tuples，每個tuple代表一筆交易
    conn.close()
    return rows