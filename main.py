from flask import Flask
from line_bot_interface import create_line_bot
from database import init_db, add_transaction, get_daily_total, get_transactions, get_one_day_transactions
from database import get_this_month, get_one_month
from datetime import datetime


# 初始化資料庫
init_db()

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
            category = parts[0]
            amount = float(parts[1])
            note = parts[2] if len(parts) == 3 else None

            add_transaction(category, amount, note)
            return f"已紀錄支出: {category} {amount} 元" + (f" note: {note}" if note else "")

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
            category = parts[0]
            amount = float(parts[1])
            note = parts[2] if len(parts) == 3 else None

            add_transaction(category, amount, note)
            return f"已紀錄收入: {category} {amount} 元" + (f" note: {note}" if note else "")

        except ValueError:
            return "金額格式錯誤，請輸入數字。"

    # 查詢今天總支出
    elif message_text.lower() == "today":
        today_str = datetime.now().strftime("%Y-%m-%d")
        total = get_daily_total(today_str)
        return f"今天總支出: {total} 元"

    # 查詢今天明細
    elif message_text.lower() == "list":
        today_str = datetime.now().strftime("%Y-%m-%d")
        rows = get_transactions(today_str)
        if not rows:
            return "今天沒有任何紀錄。"
        reply = "Record of today:\n"
        for r in rows:
            category, amount, note, created_at = r
            reply += f"{created_at} - {category} {amount} dollars"
            if note:
                reply += f" ({note})"
            reply += "\n"
        return reply
    elif message_text.startswith("get_day "):#get a day record
        content = message_text[8:].strip()
        date_str= content
        if not date_str:
            return "wrong time format, please use YYYY-MM-DD"
        rows = get_one_day_transactions(date_str)
        if not rows:
            return f"{date_str} 沒有紀錄。"
        reply = f"Records for {date_str} :\n"
        for r in rows:
            category, amount, note, created_at = r
            reply += f"{created_at} - {category} {amount} dollars"
            if note:
                reply += f" ({note})"
            reply += "\n"
        return reply
    
    elif message_text.startswith("get_month "):#get a month record
        content = message_text[10:].strip()
        month_str= content
        if not month_str:
            return "wrong time format, please use YYYY-MM"
        rows, total = get_one_month(month_str)
        if not rows:
            return f"{month_str} no records."
        reply = f"Records for {month_str} :\n"
        for r in rows:
            category, amount, note, created_at = r
            reply += f"{created_at} - {category} {amount} dollars"
            if note:
                reply += f" ({note})"
            reply += "\n"
        reply += f"Total Expenditure of {month_str} is : {total} dollars"
        return reply
    elif message_text.lower() == "get_this_month":
        rows, total = get_this_month()
        if not rows:
            return "This month no records."
        reply = "Record of this month:\n"
        for r in rows:
            category, amount, note, created_at = r
            reply += f"{created_at} - {category} {amount} dollars"
            if note:
                reply += f" ({note})"
            reply += "\n"
        reply += f"Total Expenditure of this month is : {total} dollars"
        return reply
    elif message_text.lower() == "test":
        return "test successful"
    elif message_text.lower() == "help":
        return ("指令說明:\n"
                "1. spend category amount [note] - Record expenditure\n"
                "2. income source amount [note] - Recorded income\n"
                "3. today - Query today's total expenditure\n"
                "4. list - Query today's details\n"
                "5. get_day YYYY-MM-DD - Query records for a specific date\n"
                "6. get_month YYYY-MM - Query records and total for a specific month\n"
                "7. get_this_month - Query records and total for this month")
    else:
        return "Command not recognized. Type 'help' for instructions."

# 將 Flask app 與 Line Bot handler 結合
create_line_bot(app, handle_message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)