from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-lite")

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    prompt = f"""
請判斷以下內容是「中文」還是「印尼文」。
如果是中文，翻譯成「印尼文」。
如果是印尼文，翻譯成「繁體中文」。
只輸出翻譯結果。

內容：
{user_text}
"""

    response = model.generate_content(prompt)
    translated = response.text.strip()

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=translated)
    )


if __name__ == "__main__":
    import os
    port = int(os.environ["PORT"])
    app.run(host="0.0.0.0", port=port)



