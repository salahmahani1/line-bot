from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "اوامر":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="📌 اوامر البوت:\nاوامر\nحماية")
        )

@handler.add(MemberLeftEvent)
def anti_kick(event):
    group_id = event.source.group_id
    user_id = event.left.members[0].user_id
    try:
        line_bot_api.add_member_to_group(group_id, user_id)
        line_bot_api.push_message(
            group_id,
            TextSendMessage(text="🚫 ممنوع الطرد في الجروب")
        )
    except:
        pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
