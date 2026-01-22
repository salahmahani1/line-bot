from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import *
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("SECRET"))

protect_list = []

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def message(event):
    text = event.message.text

    if text == "حماية on":
        protect_list.append(event.source.group_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="✅ تم تفعيل الحماية")
        )

    if text == "حماية off":
        protect_list.remove(event.source.group_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="❌ تم إيقاف الحماية")
        )

@handler.add(MemberLeftEvent)
def anti_kick(event):
    if event.source.group_id in protect_list:
        try:
            line_bot_api.invite_group_member(
                event.source.group_id,
                [event.left.member_id]
            )
        except:
            pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
