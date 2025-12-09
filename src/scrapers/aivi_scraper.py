"""AIVI 網站爬蟲模組

負責爬取 AIVI 網站（https://www.aivi.fyi/）的最新文章資訊。
"""

import logging
from typing import List, Dict
from urllib.parse import urljoin

import httpx
from selectolax.parser import HTMLParser

# 設定常數
AIVI_BASE_URL = "https://www.aivi.fyi"
AIVI_HOMEPAGE_URL = "https://www.aivi.fyi/"
REQUEST_TIMEOUT = 5  # 秒
MAX_RETRIES = 2
CSS_SELECTOR = "h2.archive__item-title > a"

# 設定日誌記錄器
logger = logging.getLogger(__name__)


def parse_articles(html: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """解析 AIVI 首頁 HTML，提取文章資訊

    參數：
        html: AIVI 首頁的 HTML 內容
        max_articles: 最多返回幾則文章（預設 5）

    返回：
        文章清單，每個元素包含 title 和 url

    範例：
        >>> html = '<h2 class="archive__item-title"><a href="/llms/test">測試</a></h2>'
        >>> parse_articles(html, max_articles=1)
        [{'title': '測試', 'url': 'https://www.aivi.fyi/llms/test'}]
    """
    try:
        tree = HTMLParser(html)
        article_links = tree.css(CSS_SELECTOR)

        if not article_links:
            logger.warning("找不到文章連結，HTML 結構可能已變更")
            return []

        articles = []
        for link in article_links[:max_articles]:
            title = link.text(strip=True)
            relative_url = link.attributes.get("href", "")

            if not title or not relative_url:
                logger.warning(f"文章資訊不完整：title={title}, url={relative_url}")
                continue

            # 處理相對路徑，加上 base URL
            absolute_url = urljoin(AIVI_BASE_URL, relative_url)

            articles.append({
                "title": title,
                "url": absolute_url
            })

        logger.info(f"成功解析 {len(articles)} 則文章")
        return articles

    except Exception as e:
        logger.error(f"解析 HTML 時發生錯誤：{e}")
        logger.warning("HTML 結構可能已變更")
        return []


async def scrape_aivi_news(max_articles: int = 5) -> List[Dict[str, str]]:
    """爬取 AIVI 最新文章

    參數：
        max_articles: 最多返回幾則文章（預設 5）

    返回：
        文章清單，每個元素包含 title 和 url

    異常：
        httpx.TimeoutException: 請求超時
        httpx.HTTPError: HTTP 錯誤

    範例：
        >>> import asyncio
        >>> articles = asyncio.run(scrape_aivi_news(max_articles=3))
        >>> len(articles) <= 3
        True
    """
    retry_count = 0

    while retry_count <= MAX_RETRIES:
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"正在爬取 AIVI 首頁... (嘗試 {retry_count + 1}/{MAX_RETRIES + 1})")
                response = await client.get(
                    AIVI_HOMEPAGE_URL,
                    timeout=REQUEST_TIMEOUT,
                    follow_redirects=True
                )
                response.raise_for_status()

                logger.info(f"成功取得 AIVI 首頁 (HTTP {response.status_code})")
                return parse_articles(response.text, max_articles)

        except httpx.TimeoutException as e:
            retry_count += 1
            logger.warning(f"請求超時 (嘗試 {retry_count}/{MAX_RETRIES + 1})：{e}")

            if retry_count > MAX_RETRIES:
                logger.error(f"已達最大重試次數 ({MAX_RETRIES})，放棄爬取")
                return []

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 錯誤 (狀態碼 {e.response.status_code})：{e}")
            return []

        except httpx.HTTPError as e:
            logger.error(f"HTTP 請求失敗：{e}")
            return []

        except Exception as e:
            logger.error(f"爬取時發生未預期的錯誤：{e}")
            return []

    return []
