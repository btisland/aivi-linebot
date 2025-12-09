"""整合測試：指令處理流程

測試從指令接收到訊息回覆的完整流程，包含指令處理器與爬蟲模組的整合。
"""

import time
import pytest
from unittest.mock import Mock, AsyncMock

from src.handlers.command_handler import handle_aivi_command, format_news_message


class TestCommandIntegration:
    """指令處理整合測試

    測試指令處理器與爬蟲模組的整合流程。
    """

    @pytest.mark.asyncio
    async def test_handle_aivi_command_success(self, mocker):
        """測試 /aivi 指令成功執行

        驗證：
        - 爬蟲被正確呼叫
        - LINE API reply_message 被呼叫
        - 訊息格式正確
        - 包含所有文章標題和連結
        """
        # Mock LINE Bot API
        mock_api_client = Mock()
        mock_line_bot_api = Mock()
        mock_api_client.__enter__ = Mock(return_value=mock_api_client)
        mock_api_client.__exit__ = Mock(return_value=False)

        # Mock MessagingApi
        mocker.patch(
            'src.handlers.command_handler.MessagingApi',
            return_value=mock_line_bot_api
        )

        # Mock 爬蟲回傳資料
        mock_scrape = mocker.patch(
            'src.handlers.command_handler.scrape_aivi_news',
            new_callable=AsyncMock
        )
        mock_scrape.return_value = [
            {'title': 'Test Article 1', 'url': 'https://www.aivi.fyi/test-1'},
            {'title': 'Test Article 2', 'url': 'https://www.aivi.fyi/test-2'},
        ]

        # Mock event
        mock_event = Mock()
        mock_event.reply_token = 'test_token'

        # 執行指令處理
        await handle_aivi_command(mock_event, mock_api_client)

        # 驗證爬蟲被呼叫
        mock_scrape.assert_called_once_with(max_articles=5)

        # 驗證 reply_message 被呼叫
        assert mock_line_bot_api.reply_message.called
        call_args = mock_line_bot_api.reply_message.call_args

        # 驗證訊息格式
        reply_request = call_args[0][0]
        message = reply_request.messages[0]
        message_text = message.text

        assert '📰 AIVI 最新文章' in message_text
        assert 'Test Article 1' in message_text
        assert 'https://www.aivi.fyi/test-1' in message_text
        assert 'Test Article 2' in message_text
        assert 'https://www.aivi.fyi/test-2' in message_text

    @pytest.mark.asyncio
    async def test_handle_aivi_command_no_articles(self, mocker):
        """測試爬取到空清單

        驗證：
        - 爬蟲返回空清單時的處理
        - 顯示「目前沒有找到新文章」訊息
        - LINE API 仍被正確呼叫
        """
        # Mock LINE Bot API
        mock_api_client = Mock()
        mock_line_bot_api = Mock()
        mock_api_client.__enter__ = Mock(return_value=mock_api_client)
        mock_api_client.__exit__ = Mock(return_value=False)

        mocker.patch(
            'src.handlers.command_handler.MessagingApi',
            return_value=mock_line_bot_api
        )

        # Mock 爬蟲返回空清單
        mock_scrape = mocker.patch(
            'src.handlers.command_handler.scrape_aivi_news',
            new_callable=AsyncMock
        )
        mock_scrape.return_value = []

        # Mock event
        mock_event = Mock()
        mock_event.reply_token = 'test_token'

        # 執行指令處理
        await handle_aivi_command(mock_event, mock_api_client)

        # 驗證 reply_message 被呼叫
        call_args = mock_line_bot_api.reply_message.call_args
        reply_request = call_args[0][0]
        message_text = reply_request.messages[0].text

        # 驗證訊息內容
        assert '目前沒有找到新文章' in message_text

    @pytest.mark.asyncio
    async def test_handle_aivi_command_scraper_error(self, mocker):
        """測試爬蟲拋出異常

        驗證：
        - 爬蟲拋出異常時的錯誤處理
        - 回覆錯誤訊息給使用者
        - 錯誤訊息格式正確
        """
        # Mock LINE Bot API
        mock_api_client = Mock()
        mock_line_bot_api = Mock()
        mock_api_client.__enter__ = Mock(return_value=mock_api_client)
        mock_api_client.__exit__ = Mock(return_value=False)

        mocker.patch(
            'src.handlers.command_handler.MessagingApi',
            return_value=mock_line_bot_api
        )

        # Mock 爬蟲拋出異常
        mock_scrape = mocker.patch(
            'src.handlers.command_handler.scrape_aivi_news',
            new_callable=AsyncMock
        )
        mock_scrape.side_effect = Exception("Network error")

        # Mock event
        mock_event = Mock()
        mock_event.reply_token = 'test_token'

        # 執行指令處理
        await handle_aivi_command(mock_event, mock_api_client)

        # 驗證錯誤訊息被回覆
        call_args = mock_line_bot_api.reply_message.call_args
        reply_request = call_args[0][0]
        message_text = reply_request.messages[0].text

        assert '❌' in message_text
        assert '無法取得新聞' in message_text

    @pytest.mark.asyncio
    async def test_handle_aivi_command_line_api_error(self, mocker):
        """測試 LINE API 拋出異常

        驗證：
        - LINE API 呼叫失敗時的處理
        - 嘗試回覆錯誤訊息
        - 錯誤被正確記錄
        """
        # Mock LINE Bot API 拋出異常
        mock_api_client = Mock()
        mock_line_bot_api = Mock()
        mock_api_client.__enter__ = Mock(return_value=mock_api_client)
        mock_api_client.__exit__ = Mock(return_value=False)

        # 第一次呼叫成功取得文章，第二次回覆時拋出異常
        mock_line_bot_api.reply_message.side_effect = Exception("LINE API error")

        mocker.patch(
            'src.handlers.command_handler.MessagingApi',
            return_value=mock_line_bot_api
        )

        # Mock 爬蟲正常返回
        mock_scrape = mocker.patch(
            'src.handlers.command_handler.scrape_aivi_news',
            new_callable=AsyncMock
        )
        mock_scrape.return_value = [
            {'title': 'Test Article', 'url': 'https://www.aivi.fyi/test'},
        ]

        # Mock event
        mock_event = Mock()
        mock_event.reply_token = 'test_token'

        # 執行指令處理 (不應拋出異常，內部已處理)
        await handle_aivi_command(mock_event, mock_api_client)

        # 驗證 reply_message 被呼叫了兩次（第一次失敗，第二次嘗試回覆錯誤訊息）
        assert mock_line_bot_api.reply_message.call_count == 2


class TestMessageFormatting:
    """訊息格式化測試

    測試 format_news_message() 函式在各種情況下的輸出格式。
    """

    def test_format_news_message_with_articles(self):
        """測試正常文章格式化

        驗證：
        - 包含標題「📰 AIVI 最新文章」
        - 每篇文章有編號
        - 每篇文章包含標題和連結
        - 格式正確
        """
        articles = [
            {'title': 'Article 1', 'url': 'https://example.com/1'},
            {'title': 'Article 2', 'url': 'https://example.com/2'},
        ]
        message = format_news_message(articles)

        assert '📰 AIVI 最新文章' in message
        assert '1. Article 1' in message
        assert '🔗 https://example.com/1' in message
        assert '2. Article 2' in message
        assert '🔗 https://example.com/2' in message

    def test_format_news_message_empty(self):
        """測試空文章清單

        驗證：
        - 包含標題
        - 顯示「目前沒有找到新文章」訊息
        """
        message = format_news_message([])

        assert '📰 AIVI 最新文章' in message
        assert '目前沒有找到新文章' in message

    def test_format_news_message_max_5_articles(self):
        """測試最多顯示 5 則文章

        驗證：
        - 當超過 5 篇文章時，只顯示前 5 篇
        - 第 6 篇以後的文章不顯示
        """
        articles = [
            {'title': f'Article {i}', 'url': f'https://example.com/{i}'}
            for i in range(10)
        ]
        message = format_news_message(articles)

        # 驗證只有 5 則文章
        assert '1. Article 0' in message
        assert '5. Article 4' in message
        assert '6. Article 5' not in message
        assert 'Article 9' not in message

    def test_format_news_message_missing_fields(self):
        """測試文章缺少欄位

        驗證：
        - 缺少標題時顯示「無標題」
        - 缺少 URL 時仍正常顯示
        """
        articles = [
            {'url': 'https://example.com/1'},  # 缺少 title
            {'title': 'Article 2'},  # 缺少 url
        ]
        message = format_news_message(articles)

        assert '無標題' in message
        assert 'Article 2' in message

    def test_format_news_message_single_article(self):
        """測試單一文章

        驗證：
        - 單一文章的格式正確
        - 編號從 1 開始
        """
        articles = [
            {'title': 'Single Article', 'url': 'https://example.com/single'},
        ]
        message = format_news_message(articles)

        assert '1. Single Article' in message
        assert '🔗 https://example.com/single' in message
        assert '2.' not in message


class TestPerformance:
    """效能測試（僅 CI 執行）

    測試系統的效能表現，確保回應時間符合需求。
    標記為 @pytest.mark.slow，可用 -m "not slow" 跳過。
    """

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_command_response_time(self, mocker):
        """測試指令回應時間（僅 CI 執行）

        驗證：
        - 整個流程回應時間 < 10 秒
        - 包含爬蟲、格式化、LINE API 呼叫
        """
        # Mock LINE Bot API
        mock_api_client = Mock()
        mock_line_bot_api = Mock()
        mock_api_client.__enter__ = Mock(return_value=mock_api_client)
        mock_api_client.__exit__ = Mock(return_value=False)

        mocker.patch(
            'src.handlers.command_handler.MessagingApi',
            return_value=mock_line_bot_api
        )

        # Mock 爬蟲返回資料
        mock_scrape = mocker.patch(
            'src.handlers.command_handler.scrape_aivi_news',
            new_callable=AsyncMock
        )
        mock_scrape.return_value = [
            {'title': f'Article {i}', 'url': f'https://example.com/{i}'}
            for i in range(5)
        ]

        # Mock event
        mock_event = Mock()
        mock_event.reply_token = 'test_token'

        # 測量執行時間
        start_time = time.time()
        await handle_aivi_command(mock_event, mock_api_client)
        elapsed_time = time.time() - start_time

        # 驗證回應時間 < 10 秒
        assert elapsed_time < 10, f"回應時間過長: {elapsed_time:.2f} 秒"

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_format_message_performance(self):
        """測試訊息格式化效能

        驗證：
        - 格式化大量文章的效能
        - 處理時間合理
        """
        # 建立 100 篇文章
        articles = [
            {'title': f'Article {i}' * 10, 'url': f'https://example.com/{i}'}
            for i in range(100)
        ]

        start_time = time.time()
        message = format_news_message(articles)
        elapsed_time = time.time() - start_time

        # 驗證格式化時間 < 1 秒
        assert elapsed_time < 1, f"格式化時間過長: {elapsed_time:.2f} 秒"

        # 驗證只顯示 5 篇
        assert '1. Article 0' in message
        assert '5. Article 4' in message


class TestEdgeCases:
    """邊界情況測試

    測試各種邊界情況和異常輸入。
    """

    @pytest.mark.asyncio
    async def test_handle_command_with_none_reply_token(self, mocker):
        """測試 reply_token 為 None

        驗證：
        - 系統能處理無效的 reply_token
        - 不會拋出未處理的異常
        """
        mock_api_client = Mock()
        mock_line_bot_api = Mock()
        mock_api_client.__enter__ = Mock(return_value=mock_api_client)
        mock_api_client.__exit__ = Mock(return_value=False)

        mocker.patch(
            'src.handlers.command_handler.MessagingApi',
            return_value=mock_line_bot_api
        )

        mock_scrape = mocker.patch(
            'src.handlers.command_handler.scrape_aivi_news',
            new_callable=AsyncMock
        )
        mock_scrape.return_value = [
            {'title': 'Test', 'url': 'https://example.com/test'},
        ]

        # Mock event with None reply_token
        mock_event = Mock()
        mock_event.reply_token = None

        # 執行指令處理（不應拋出異常）
        await handle_aivi_command(mock_event, mock_api_client)

    def test_format_message_with_special_characters(self):
        """測試特殊字元處理

        驗證：
        - 能正確處理標題中的特殊字元
        - Emoji 正常顯示
        - 換行符不影響格式
        """
        articles = [
            {'title': 'Article with emoji 🚀', 'url': 'https://example.com/1'},
            {'title': 'Article\nwith\nnewlines', 'url': 'https://example.com/2'},
            {'title': 'Article with "quotes" & symbols', 'url': 'https://example.com/3'},
        ]
        message = format_news_message(articles)

        assert '🚀' in message
        assert 'Article\nwith\nnewlines' in message
        assert '"quotes"' in message
        assert '&' in message

    def test_format_message_with_very_long_title(self):
        """測試超長標題

        驗證：
        - 能處理非常長的標題
        - 不會截斷或產生錯誤
        """
        long_title = 'A' * 1000
        articles = [
            {'title': long_title, 'url': 'https://example.com/long'},
        ]
        message = format_news_message(articles)

        assert long_title in message
        assert 'https://example.com/long' in message
