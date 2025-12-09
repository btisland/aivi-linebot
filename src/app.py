"""LINE Bot Webhook 服務

這是 LINE Bot 的核心入口，負責接收 LINE 平台的事件通知，
驗證簽章並將事件分派給對應的處理器。
"""

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
import logging
import asyncio

from src.handlers.command_handler import handle_aivi_command

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 從環境變數載入 LINE credentials
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# 檢查環境變數是否存在
if not LINE_CHANNEL_ACCESS_TOKEN:
    logger.warning("警告：未設定 LINE_CHANNEL_ACCESS_TOKEN 環境變數")
if not LINE_CHANNEL_SECRET:
    logger.warning("警告：未設定 LINE_CHANNEL_SECRET 環境變數")

# 建立 LINE Bot API 設定
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN or '')

# 建立 Webhook Handler
handler = WebhookHandler(LINE_CHANNEL_SECRET or '')


@app.route("/webhook", methods=['POST'])
def webhook():
    """LINE Bot webhook endpoint

    接收 LINE 平台的事件通知，驗證簽章並處理事件。

    Returns:
        str: 成功時返回 'OK'

    Raises:
        400: 缺少簽章 header 或簽章驗證失敗
        500: 處理事件時發生錯誤
    """
    # 取得 X-Line-Signature header
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        logger.warning("缺少 X-Line-Signature header")
        abort(400)

    # 取得 request body
    body = request.get_data(as_text=True)
    logger.info(f"收到 webhook 請求：{body}")

    # 驗證簽章並處理事件
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("簽章驗證失敗")
        abort(400)
    except Exception as e:
        logger.error(f"處理事件時發生錯誤：{e}")
        abort(500)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """處理文字訊息事件

    檢查訊息是否為 /aivi 指令，若是則呼叫指令處理器。
    指令匹配不區分大小寫。

    Args:
        event: LINE MessageEvent 物件，包含訊息內容和來源資訊
    """
    message_text = event.message.text.strip().lower()
    user_id = event.source.user_id
    logger.info(f"收到來自使用者 {user_id} 的訊息：{event.message.text}")

    # 檢查是否為 /aivi 指令
    if message_text == "/aivi":
        logger.info("偵測到 /aivi 指令，開始處理")
        # 使用 asyncio 執行非同步指令處理
        with ApiClient(configuration) as api_client:
            asyncio.run(handle_aivi_command(event, api_client))
    else:
        # 其他訊息不處理
        logger.debug(f"非指令訊息，不處理: {message_text}")
        pass


if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    logger.info(f"啟動 Flask 服務，監聽 port {port}")

    # 檢查必要的環境變數
    if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
        logger.warning(
            "未設定完整的 LINE credentials，請確保以下環境變數已設定：\n"
            "  - LINE_CHANNEL_ACCESS_TOKEN\n"
            "  - LINE_CHANNEL_SECRET"
        )

    app.run(host='0.0.0.0', port=port, debug=True)
