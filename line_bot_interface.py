import os
from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

def create_line_bot(app, handle_message_callback):

    # 從環境變數讀取
    CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
    ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

    if not CHANNEL_SECRET or not ACCESS_TOKEN:
        raise ValueError("請先設定環境變數 LINE_CHANNEL_SECRET 與 LINE_CHANNEL_ACCESS_TOKEN")

    line_bot_api = LineBotApi(ACCESS_TOKEN)
    handler = WebhookHandler(CHANNEL_SECRET)

    @app.route("/callback", methods=['POST'])
    def callback():
        signature = request.headers.get('X-Line-Signature', '')
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return 'OK'

    @handler.add(MessageEvent, message=TextMessage)
    def handle_text_message(event):
        user_id = event.source.user_id
        message_text = event.message.text

        # 呼叫 main 提供的函式
        reply_text = handle_message_callback(user_id, message_text)

        # 回覆 LINE
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

    return app