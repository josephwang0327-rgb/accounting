from flask import Flask
from line_bot_interface import create_line_bot
from database import init_db, add_transaction, get_daily_total, get_transactions
from datetime import datetime

DB_PATH = "my_transactions.db"

# 初始化資料庫
init_db(DB_PATH)

app = Flask(__name__)

def handle_message(user_id, message_text):
    """
    處理 Line Bot 訊息的主函式，低耦合設計。
    只負責解析指令，資料操作透過 database.py。
    """
    message_text = message_text.strip()

    # 處理支出指令
    if message_text.startswith("spend "):
        content = message_text[6:].strip()
        try:
            # 假設格式: spend lunch 60 optional_note
            parts = content.split(maxsplit=2)  # 最多拆成三個部分
            if len(parts) < 2:
                return "格式錯誤，請輸入: spend 用途 金額 [備註]"
            purpose = parts[0]
            amount = float(parts[1])
            note = parts[2] if len(parts) == 3 else None

            add_transaction(DB_PATH, purpose, amount, note)
            return f"已紀錄支出: {purpose} {amount} 元" + (f"，備註: {note}" if note else "")

        except ValueError:
            return "金額格式錯誤，請輸入數字。"

    # 處理收入指令
    elif message_text.startswith("income "):
        content = message_text[7:].strip()
        try:
            # 假設格式: income salary 20000 optional_note
            parts = content.split(maxsplit=2)
            if len(parts) < 2:
                return "格式錯誤，請輸入: income 來源 金額 [備註]"
            purpose = parts[0]
            amount = float(parts[1])
            note = parts[2] if len(parts) == 3 else None

            add_transaction(DB_PATH, purpose, amount, note)
            return f"已紀錄收入: {purpose} {amount} 元" + (f"，備註: {note}" if note else "")

        except ValueError:
            return "金額格式錯誤，請輸入數字。"

    # 查詢今天總支出
    elif message_text.lower() == "today":
        today_str = datetime.now().strftime("%Y-%m-%d")
        total = get_daily_total(DB_PATH, today_str)
        return f"今天總支出: {total} 元"

    # 查詢今天明細
    elif message_text.lower() == "list":
        today_str = datetime.now().strftime("%Y-%m-%d")
        rows = get_transactions(DB_PATH, today_str)
        if not rows:
            return "今天沒有任何紀錄。"
        reply = "今天紀錄:\n"
        for r in rows:
            purpose, amount, note, created_at = r
            reply += f"{created_at} - {purpose} {amount} 元"
            if note:
                reply += f" ({note})"
            reply += "\n"
        return reply

    else:
        return "沒辨識到指令，請用 spend/income 開頭，或輸入 today/list 查詢"

# 將 Flask app 與 Line Bot handler 結合
create_line_bot(app, handle_message)

if __name__ == "__main__":
    app.run(port=5000)