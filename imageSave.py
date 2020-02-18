import sys
import boto3
from io import BytesIO
from datetime import datetime
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageMessage,
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)

channel_secret = "LINE_CHANNEL_SECRET"               # Lineチャンネルトークン
channel_access_token = "LINE_CHANNEL_ACCESS_TOKEN"   # Lineアクセストークン
S3 = boto3.resource('s3')
BUCKET = 'S3_BUCKET'                                 # バケット名

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

def image_set(event, context):
    signature = event["headers"]["X-Line-Signature"]
    body = event["body"]

    ok_json = {"isBase64Encoded": False,
               "statusCode": 200,
               "headers": {},
               "body": ""}
    error_json = {"isBase64Encoded": False,
                  "statusCode": 403,
                  "headers": {},
                  "body": "Error"}

    # # テキストの場合
    @handler.add(MessageEvent, message=TextMessage)
    def message(line_event):
        text = "画像を送信してください"
        line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text=text))

    # 画像の場合
    @handler.add(MessageEvent, message=ImageMessage)
    def handle_image(line_event):
        text = "保存しました"
        line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text=text))

        message_id = line_event.message.id
        message_content = line_bot_api.get_message_content(message_id)
        image_bin = BytesIO(message_content.content)
        image = image_bin.getvalue()
        file_name = str(message_id) + '.jpg' # メッセージIDをファイル名とする
        S3.Object(BUCKET,file_name).put(Body=image)

    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        return error_json
    except InvalidSignatureError as e:
        return error_json
    return ok_json
