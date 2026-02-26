from flask import Flask, request, jsonify

def create_line_bot(app, handle_message_callback):
    """
    建立 Line Bot webhook handler。
    參數:
        app: Flask app
        handle_message_callback: function, 接收 (user_id, message_text) 兩個參數
                                 返回要回覆的文字
    """

    @app.route("/callback", methods=['POST'])
    def callback():
        data = request.get_json()
        # 簡單檢查格式
        if "events" not in data or len(data["events"]) == 0:
            return jsonify({"status": "no events"})

        event = data["events"][0]

        # 目前只處理文字訊息
        if event.get("type") != "message" or event["message"]["type"] != "text":
            return jsonify({"status": "ignored"})

        user_id = event["source"]["userId"]
        message_text = event["message"]["text"]

        # 呼叫 main 提供的 callback 去處理訊息
        reply_text = handle_message_callback(user_id, message_text)

        # 回覆給 Line
        return jsonify({
            "status": "ok",
            "reply": reply_text
        })

    return app