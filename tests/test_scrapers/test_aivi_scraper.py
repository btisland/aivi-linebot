"""AIVI 爬蟲模組單元測試

測試 AIVI 爬蟲模組的各種情境，包括正常情況、錯誤處理、邊界情況。
使用 mock 技術模擬 HTTP 回應，避免真實網路請求。
"""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock

from src.scrapers.aivi_scraper import (
    scrape_aivi_news,
    parse_articles,
    AIVI_BASE_URL,
    AIVI_HOMEPAGE_URL,
)


class TestParseArticles:
    """測試 parse_articles 函式的各種情境"""

    def test_parse_articles_normal(self):
        """測試正常 HTML 解析"""
        html = '''
        <h2 class="archive__item-title"><a href="/llms/article-1">AI 技術趨勢分析</a></h2>
        <h2 class="archive__item-title"><a href="/news/article-2">機器學習最新發展</a></h2>
        <h2 class="archive__item-title"><a href="/tech/article-3">深度學習應用案例</a></h2>
        '''
        articles = parse_articles(html, max_articles=5)

        assert len(articles) == 3
        assert articles[0]['title'] == 'AI 技術趨勢分析'
        assert articles[0]['url'] == 'https://www.aivi.fyi/llms/article-1'
        assert articles[1]['title'] == '機器學習最新發展'
        assert articles[1]['url'] == 'https://www.aivi.fyi/news/article-2'
        assert articles[2]['title'] == '深度學習應用案例'
        assert articles[2]['url'] == 'https://www.aivi.fyi/tech/article-3'

    def test_parse_articles_empty(self):
        """測試空 HTML"""
        articles = parse_articles("")
        assert articles == []

    def test_parse_articles_no_articles(self):
        """測試找不到文章元素"""
        html = '''
        <div class="content">
            <p>這裡沒有文章</p>
        </div>
        '''
        articles = parse_articles(html)
        assert articles == []

    def test_parse_articles_relative_urls(self):
        """測試相對路徑轉換為絕對路徑"""
        html = '''
        <h2 class="archive__item-title"><a href="/article">相對路徑測試</a></h2>
        <h2 class="archive__item-title"><a href="https://www.aivi.fyi/absolute">絕對路徑測試</a></h2>
        '''
        articles = parse_articles(html)

        assert len(articles) == 2
        # 相對路徑應該被轉換為絕對路徑
        assert articles[0]['url'] == 'https://www.aivi.fyi/article'
        # 絕對路徑應該保持不變
        assert articles[1]['url'] == 'https://www.aivi.fyi/absolute'

    def test_parse_articles_max_limit(self):
        """測試最大文章數限制"""
        html = '''
        <h2 class="archive__item-title"><a href="/1">文章 1</a></h2>
        <h2 class="archive__item-title"><a href="/2">文章 2</a></h2>
        <h2 class="archive__item-title"><a href="/3">文章 3</a></h2>
        <h2 class="archive__item-title"><a href="/4">文章 4</a></h2>
        <h2 class="archive__item-title"><a href="/5">文章 5</a></h2>
        <h2 class="archive__item-title"><a href="/6">文章 6</a></h2>
        '''
        # 限制最多 3 則
        articles = parse_articles(html, max_articles=3)

        assert len(articles) == 3
        assert articles[0]['title'] == '文章 1'
        assert articles[1]['title'] == '文章 2'
        assert articles[2]['title'] == '文章 3'

    def test_parse_articles_incomplete_data(self):
        """測試不完整的文章資料（缺少標題或連結）"""
        html = '''
        <h2 class="archive__item-title"><a href="/valid">正常文章</a></h2>
        <h2 class="archive__item-title"><a href="">缺少 URL</a></h2>
        <h2 class="archive__item-title"><a href="/no-title"></a></h2>
        '''
        articles = parse_articles(html)

        # 只應該解析到完整的文章
        assert len(articles) == 1
        assert articles[0]['title'] == '正常文章'

    def test_parse_articles_with_whitespace(self):
        """測試標題包含空白字元的處理"""
        html = '''
        <h2 class="archive__item-title"><a href="/article">  標題前後有空白  </a></h2>
        '''
        articles = parse_articles(html)

        assert len(articles) == 1
        # 應該自動去除前後空白
        assert articles[0]['title'] == '標題前後有空白'

    def test_parse_articles_exception_handling(self, mocker):
        """測試解析時發生未預期的錯誤"""
        # Mock HTMLParser 讓它拋出異常
        mocker.patch('src.scrapers.aivi_scraper.HTMLParser', side_effect=Exception("解析錯誤"))

        html = '<h2 class="archive__item-title"><a href="/test">測試</a></h2>'
        articles = parse_articles(html)

        # 發生錯誤應該返回空清單
        assert articles == []


class TestScrapeAiviNews:
    """測試 scrape_aivi_news 函式的各種情境"""

    @pytest.mark.asyncio
    async def test_scrape_aivi_news_success(self, mocker):
        """測試成功爬取文章（使用 mock）"""
        mock_html = '''
        <h2 class="archive__item-title"><a href="/test-1">測試文章 1</a></h2>
        <h2 class="archive__item-title"><a href="/test-2">測試文章 2</a></h2>
        '''

        # Mock HTTP 回應
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.raise_for_status = MagicMock()

        mock_get = mocker.patch('httpx.AsyncClient.get', new_callable=AsyncMock)
        mock_get.return_value = mock_response

        articles = await scrape_aivi_news()

        # 驗證結果
        assert len(articles) == 2
        assert articles[0]['title'] == '測試文章 1'
        assert articles[1]['title'] == '測試文章 2'

        # 驗證 HTTP 請求參數
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == AIVI_HOMEPAGE_URL
        assert call_args[1]['timeout'] == 5
        assert call_args[1]['follow_redirects'] is True

    @pytest.mark.asyncio
    async def test_scrape_aivi_news_http_error(self, mocker):
        """測試 HTTP 錯誤處理"""
        mock_get = mocker.patch('httpx.AsyncClient.get', new_callable=AsyncMock)
        mock_get.side_effect = httpx.HTTPError("Network error")

        articles = await scrape_aivi_news()

        # 發生錯誤應該返回空清單
        assert articles == []

    @pytest.mark.asyncio
    async def test_scrape_aivi_news_timeout(self, mocker):
        """測試 timeout 錯誤處理（含重試機制）"""
        mock_get = mocker.patch('httpx.AsyncClient.get', new_callable=AsyncMock)
        # 模擬三次都 timeout（初次 + 2 次重試）
        mock_get.side_effect = httpx.TimeoutException("Request timeout")

        articles = await scrape_aivi_news()

        # 應該返回空清單
        assert articles == []
        # 應該嘗試 3 次（初次 + MAX_RETRIES=2）
        assert mock_get.call_count == 3

    @pytest.mark.asyncio
    async def test_scrape_aivi_news_http_status_error(self, mocker):
        """測試 HTTP 狀態碼錯誤（如 404、500）"""
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_get = mocker.patch('httpx.AsyncClient.get', new_callable=AsyncMock)
        mock_get.return_value = mock_response
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=mock_response
        )

        articles = await scrape_aivi_news()

        # 發生錯誤應該返回空清單
        assert articles == []

    @pytest.mark.asyncio
    async def test_scrape_aivi_news_timeout_with_retry_success(self, mocker):
        """測試 timeout 重試機制成功情境"""
        mock_html = '<h2 class="archive__item-title"><a href="/success">重試成功</a></h2>'

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.raise_for_status = MagicMock()

        mock_get = mocker.patch('httpx.AsyncClient.get', new_callable=AsyncMock)
        # 第一次 timeout，第二次成功
        mock_get.side_effect = [
            httpx.TimeoutException("First timeout"),
            mock_response
        ]

        articles = await scrape_aivi_news()

        # 應該成功取得文章
        assert len(articles) == 1
        assert articles[0]['title'] == '重試成功'
        # 應該呼叫 2 次
        assert mock_get.call_count == 2

    @pytest.mark.asyncio
    async def test_scrape_aivi_news_max_articles_param(self, mocker):
        """測試 max_articles 參數正確傳遞"""
        mock_html = '''
        <h2 class="archive__item-title"><a href="/1">文章 1</a></h2>
        <h2 class="archive__item-title"><a href="/2">文章 2</a></h2>
        <h2 class="archive__item-title"><a href="/3">文章 3</a></h2>
        <h2 class="archive__item-title"><a href="/4">文章 4</a></h2>
        <h2 class="archive__item-title"><a href="/5">文章 5</a></h2>
        '''

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.raise_for_status = MagicMock()

        mock_get = mocker.patch('httpx.AsyncClient.get', new_callable=AsyncMock)
        mock_get.return_value = mock_response

        # 只要求 2 則文章
        articles = await scrape_aivi_news(max_articles=2)

        assert len(articles) == 2
        assert articles[0]['title'] == '文章 1'
        assert articles[1]['title'] == '文章 2'

    @pytest.mark.asyncio
    async def test_scrape_aivi_news_unexpected_exception(self, mocker):
        """測試爬取時發生未預期的錯誤"""
        mock_get = mocker.patch('httpx.AsyncClient.get', new_callable=AsyncMock)
        # 模擬一個非 httpx 的異常
        mock_get.side_effect = RuntimeError("未預期的錯誤")

        articles = await scrape_aivi_news()

        # 發生錯誤應該返回空清單
        assert articles == []


class TestSlowTests:
    """慢速測試（真實網路請求，僅在 CI 執行）"""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_real_aivi_website_scraping(self):
        """實際連線測試 AIVI 網站（僅 CI 執行）"""
        articles = await scrape_aivi_news(max_articles=3)

        # 驗證基本結構
        assert isinstance(articles, list)

        # 如果有文章，驗證資料格式
        if len(articles) > 0:
            assert all('title' in article for article in articles)
            assert all('url' in article for article in articles)
            assert all(article['url'].startswith('https://') for article in articles)
            assert all(AIVI_BASE_URL in article['url'] for article in articles)
            assert all(len(article['title']) > 0 for article in articles)
