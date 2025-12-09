"""LINE Bot 指令處理器

負責處理使用者指令，包括指令匹配、呼叫爬蟲模組、格式化訊息，
並透過 LINE Bot API 回覆使用者。
"""

import logging
from typing import List, Dict

from linebot.v3.messaging import ApiClient, MessagingApi, TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent

from src.scrapers.aivi_scraper import scrape_aivi_news

# 設定日誌記錄器
logger = logging.getLogger(__name__)


def format_news_message(articles: List[Dict[str, str]]) -> str:
    """格式化文章清單為 LINE 訊息

    參數：
        articles: 文章清單，每個元素包含 title 和 url

    返回：
        格式化的訊息字串

    範例：
        >>> articles = [
        ...     {'title': '測試文章', 'url': 'https://www.aivi.fyi/test'},
        ...     {'title': 'AI 新聞', 'url': 'https://www.aivi.fyi/ai-news'}
        ... ]
        >>> message = format_news_message(articles)
        >>> '📰 AIVI 最新文章' in message
        True
        >>> '測試文章' in message
        True
    """
    if not articles:
        return "📰 AIVI 最新文章\n\n目前沒有找到新文章"

    message = "📰 AIVI 最新文章\n\n"

    for i, article in enumerate(articles[:5], 1):
        title = article.get('title', '無標題')
        url = article.get('url', '')
        message += f"{i}. {title}\n"
        message += f"   🔗 {url}\n\n"

    return message.strip()


async def handle_aivi_command(event: MessageEvent, api_client: ApiClient):
    """處理 /aivi 指令

    呼叫爬蟲模組取得最新文章，格式化訊息後透過 LINE Bot API 回覆使用者。
    若發生錯誤，會回覆錯誤訊息。

    參數：
        event: LINE MessageEvent 物件，包含訊息內容和 reply token
        api_client: LINE Messaging API 客戶端實例

    錯誤處理：
        - 爬蟲模組拋出異常：記錄日誌，回覆錯誤訊息
        - 文章清單為空：正常處理，回覆「目前沒有找到新文章」
        - LINE API 呼叫失敗：記錄錯誤，不重試

    範例：
        >>> # 在實際使用中，event 和 api_client 由 LINE Bot 框架提供
        >>> # await handle_aivi_command(event, api_client)
    """
    try:
        logger.info("開始處理 /aivi 指令")

        # 呼叫爬蟲模組取得最新文章
        articles = await scrape_aivi_news(max_articles=5)
        logger.info(f"爬取到 {len(articles)} 則文章")

        # 格式化訊息
        message_text = format_news_message(articles)

        # 回覆訊息
        with api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=message_text)]
                )
            )

        logger.info(f"成功回覆 {len(articles)} 則新聞")

    except Exception as e:
        logger.error(f"處理 /aivi 指令時發生錯誤: {e}", exc_info=True)

        # 回覆錯誤訊息
        error_message = "❌ 抱歉，目前無法取得新聞。請稍後再試。"

        try:
            with api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=error_message)]
                    )
                )
            logger.info("已回覆錯誤訊息")

        except Exception as reply_error:
            logger.error(f"回覆錯誤訊息時失敗: {reply_error}", exc_info=True)
