from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import *
import os

app = Flask(__name__)

# TOKENS من Environment Variables
line_bot_api = LineBotApi(os.getenv("ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("SECRET"))

# الجروبات اللي الحماية شغالة فيها
protect_list = []

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except:
        abort(400)

    return "OK"

# ====== استقبال الرسائل ======
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    group_id = event.source.group_id if event.source.type == "group" else None

    # اوامر
    if text == "اوامر":
        reply = (
            "🤖 أوامر البوت:\n\n"
            "🔐 حماية شغالة\n"
            "🔓 حماية واقفة\n"
            "📌 حالة\n"
            "📖 اوامر"
        )
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

    elif text == "حماية شغالة" and group_id:
        if group_id not in protect_list:
            protect_list.append(group_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="✅ الحماية اشتغلت يا كبير")
        )

    elif text == "حماية واقفة" and group_id:
        if group_id in protect_list:
            protect_list.remove(group_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="❌ الحماية اتقفلت")
        )

    elif text == "حالة" and group_id:
        if group_id in protect_list:
            msg = "🔐 الجروب تحت الحماية"
        else:
            msg = "🔓 مفيش حماية دلوقتي"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg)
        )

# ====== محاولة طرد ======
@handler.add(MemberLeftEvent)
def anti_kick(event):
    group_id = event.source.group_id

    if group_id in protect_list:
        line_bot_api.push_message(
            group_id,
            TextSendMessage(
                text="⚠️ خد بالك!\nفي حد اتطرد والجروب تحت الحماية 👀"
            )
        )

# ====== تشغيل السيرفر ======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
