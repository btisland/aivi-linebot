# 開發指南

本文件提供 AIVI News LINE Bot 專案的詳細開發指引，包含專案結構、開發流程、測試策略和程式碼風格規範。

## 專案結構詳解

```
aivi-linebot/
├── src/                          # 主要程式碼
│   ├── __init__.py
│   ├── app.py                    # Flask webhook 服務入口
│   ├── scrapers/                 # 爬蟲模組
│   │   ├── __init__.py
│   │   └── aivi_scraper.py       # AIVI 科技博客爬蟲
│   ├── handlers/                 # 指令處理器
│   │   ├── __init__.py
│   │   └── command_handler.py    # /aivi 指令處理器
│   └── utils/                    # 工具函式（保留供未來擴充）
│       └── __init__.py
├── tests/                        # 測試檔案
│   ├── test_scrapers/
│   │   └── test_aivi_scraper.py  # 爬蟲單元測試
│   └── test_handlers/
│       └── test_command_handler.py  # 指令處理器整合測試
├── docs/                         # 專案文件
│   ├── development.md            # 本檔案
│   └── deployment-checklist.md   # 部署檢查清單
├── .github/workflows/            # GitHub Actions
│   └── sync-to-hf.yml            # 自動同步到 Hugging Face
├── .env.example                  # 環境變數範本
├── Dockerfile                    # Hugging Face Space 部署用
├── README_HF.md                  # Hugging Face Space 說明
├── README.md                     # 專案主要說明文件
├── pyproject.toml                # 專案設定與相依套件定義
└── uv.lock                       # 套件版本鎖定檔（由 uv 自動產生）
```

## 模組說明

### src/app.py
Flask webhook 服務的核心入口，負責：
- 接收 LINE 平台的 webhook 事件
- 驗證 webhook 簽章（X-Line-Signature）
- 將訊息事件分派給對應的指令處理器
- 環境變數載入與錯誤處理

**關鍵函式**：
- `webhook()`: Webhook endpoint，處理 POST 請求
- `handle_message()`: 訊息事件處理器，檢查是否為 `/aivi` 指令

### src/scrapers/aivi_scraper.py
爬取 AIVI 科技博客文章清單的爬蟲模組：
- 使用 `httpx.AsyncClient` 進行非同步 HTTP 請求
- 使用 `selectolax.HTMLParser` 解析 HTML
- 完整的錯誤處理（timeout、HTTP 錯誤、解析錯誤）
- 回傳標題與連結的清單

**主要函式**：
- `scrape_aivi_news()`: 爬取最新 5 則文章

### src/handlers/command_handler.py
處理 `/aivi` 指令的處理器：
- 呼叫爬蟲模組取得文章清單
- 格式化訊息（標題 + 連結）
- 使用 LINE Messaging API 回傳訊息
- 錯誤處理與友善錯誤訊息

**主要函式**：
- `handle_aivi_command()`: 處理 `/aivi` 指令的主邏輯

## 開發流程

### 分支策略

本專案採用簡化的 Git Flow：

- **main**: 正式環境分支，受保護
- **epic/news-push-bot**: 主要開發分支（目前使用 worktree）
- **feature/xxx**: 功能分支（從 epic 分支建立）
- **hotfix/xxx**: 緊急修復分支（從 main 建立）

### 工作流程

#### 1. 新增功能

```bash
# 1. 從 epic 分支建立功能分支
git checkout epic/news-push-bot
git pull origin epic/news-push-bot
git checkout -b feature/新功能名稱

# 2. 實作功能並撰寫測試
# 編輯程式碼...

# 3. 執行測試確保品質
pytest -m "not slow"

# 4. 提交變更
git add .
git commit -m "Issue #X: 新增 XXX 功能

- 實作內容說明
- 測試覆蓋
"

# 5. 推送並建立 PR
git push origin feature/新功能名稱
# 在 GitHub 建立 PR 到 epic/news-push-bot
```

#### 2. 修復 Bug

```bash
# 1. 建立修復分支
git checkout epic/news-push-bot
git checkout -b fix/bug描述

# 2. 重現 bug 並撰寫測試
# 先撰寫會失敗的測試，確保測試能捕捉 bug

# 3. 修復 bug
# 編輯程式碼...

# 4. 驗證測試通過
pytest

# 5. 提交變更
git add .
git commit -m "Issue #X: 修復 XXX bug

- Bug 描述
- 修復方法
- 新增測試案例
"
```

### 提交訊息規範

遵循以下格式：

```
Issue #編號: 簡短描述（50 字以內）

- 詳細說明第一點
- 詳細說明第二點
- 詳細說明第三點
```

**範例**：
```
Issue #8: 完成專案文件與部署設定

- 更新 README.md（專案說明、開發指南）
- 建立 docs/development.md（詳細開發文件）
- 建立 GitHub Actions workflow（自動同步到 HF）
- 建立 Dockerfile（Hugging Face 部署）
```

**注意**：
- 使用繁體中文台灣用語
- 不要加入 Claude Code 的 co-author 訊息
- 使用 Issue 編號追蹤變更

## 測試策略

### 測試層級

1. **單元測試**（Unit Tests）
   - 測試單一模組或函式
   - 使用 mock 隔離外部相依
   - 範例：`test_aivi_scraper.py`

2. **整合測試**（Integration Tests）
   - 測試多個模組的整合
   - 標記為 `@pytest.mark.slow`
   - 範例：`test_command_handler.py`

### 測試執行

```bash
# 快速測試（本機開發用，排除慢速測試）
pytest -m "not slow"

# 完整測試（含慢速測試）
pytest

# 測試覆蓋率報告
pytest --cov=src --cov-report=term-missing

# 測試覆蓋率報告（HTML 格式）
pytest --cov=src --cov-report=html
# 查看 htmlcov/index.html

# 執行特定測試檔案
pytest tests/test_scrapers/test_aivi_scraper.py

# 執行特定測試函式
pytest tests/test_scrapers/test_aivi_scraper.py::test_scrape_aivi_news_success
```

### 撰寫測試指南

#### 1. 單元測試範例

```python
import pytest
from unittest.mock import AsyncMock, patch
from src.scrapers.aivi_scraper import scrape_aivi_news

@pytest.mark.asyncio
async def test_scrape_aivi_news_success():
    """測試成功爬取文章"""
    # Arrange: 準備測試資料
    mock_html = """
    <div class="post-list">
        <article><h2><a href="/post1">文章標題 1</a></h2></article>
    </div>
    """

    # Act: 執行測試
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value.text = mock_html
        mock_get.return_value.status_code = 200
        result = await scrape_aivi_news()

    # Assert: 驗證結果
    assert len(result) == 1
    assert result[0]['title'] == '文章標題 1'
    assert result[0]['url'] == 'https://blog.aivislab.com/post1'
```

#### 2. 整合測試範例

```python
@pytest.mark.slow
@pytest.mark.asyncio
async def test_handle_aivi_command_integration(mocker):
    """整合測試：從指令到回覆"""
    # Arrange
    mock_event = mocker.Mock()
    mock_event.reply_token = "test_token"
    mock_api_client = mocker.Mock()

    # Mock 爬蟲結果
    mocker.patch(
        'src.handlers.command_handler.scrape_aivi_news',
        return_value=[{'title': 'Test', 'url': 'https://test.com'}]
    )

    # Act
    await handle_aivi_command(mock_event, mock_api_client)

    # Assert
    # 驗證是否呼叫了 LINE API
    assert mock_api_client.called
```

### 測試覆蓋率目標

- **整體覆蓋率**: > 80%
- **核心模組**: > 90%
  - `src/scrapers/aivi_scraper.py`
  - `src/handlers/command_handler.py`
- **入口檔案**: > 70%
  - `src/app.py`

## 程式碼風格指南

### Python 風格

遵循 **PEP 8** 規範，並加入以下專案特定規則：

#### 1. 註解與文件字串

**使用繁體中文台灣用語**：

```python
def scrape_aivi_news() -> list[dict]:
    """爬取 AIVI 科技博客最新文章

    從 AIVI 科技博客首頁爬取最新 5 則文章的標題與連結。
    使用 httpx 進行非同步請求，selectolax 解析 HTML。

    Returns:
        list[dict]: 文章清單，每個元素包含 'title' 和 'url' 鍵

    Raises:
        httpx.TimeoutException: 請求逾時
        httpx.HTTPStatusError: HTTP 錯誤
    """
    pass
```

#### 2. Type Hints

**所有函式都要有 type hints**：

```python
# ✅ 正確
async def scrape_aivi_news() -> list[dict[str, str]]:
    pass

def format_message(articles: list[dict]) -> str:
    pass

# ❌ 錯誤（缺少 type hints）
async def scrape_aivi_news():
    pass
```

#### 3. 命名規則

- **函式與變數**: `snake_case`
- **類別**: `PascalCase`
- **常數**: `UPPER_SNAKE_CASE`
- **私有成員**: 前綴 `_`

```python
# 函式與變數
def handle_aivi_command():
    user_message = "test"

# 類別
class ArticleScraper:
    pass

# 常數
MAX_ARTICLES = 5
TIMEOUT_SECONDS = 10

# 私有成員
def _parse_html(html: str):
    pass
```

#### 4. 錯誤處理

**永遠要有明確的錯誤處理**：

```python
# ✅ 正確：明確處理可能的錯誤
try:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
except httpx.TimeoutException:
    logger.error("請求逾時")
    return []
except httpx.HTTPStatusError as e:
    logger.error(f"HTTP 錯誤: {e.response.status_code}")
    return []
except Exception as e:
    logger.error(f"未預期的錯誤: {e}")
    return []
```

#### 5. 日誌記錄

使用適當的日誌等級：

```python
import logging

logger = logging.getLogger(__name__)

# DEBUG: 詳細的除錯資訊
logger.debug(f"收到 HTML: {html[:100]}...")

# INFO: 一般資訊性訊息
logger.info("開始爬取 AIVI 文章")

# WARNING: 警告訊息（不影響功能）
logger.warning("未設定環境變數，使用預設值")

# ERROR: 錯誤訊息（影響功能）
logger.error(f"爬取失敗: {error}")

# CRITICAL: 嚴重錯誤（系統無法運行）
logger.critical("無法載入設定檔")
```

### 匯入順序

遵循 PEP 8 的匯入順序：

```python
# 1. 標準函式庫
import os
import logging
from typing import Optional

# 2. 第三方套件
import httpx
from selectolax.parser import HTMLParser
from flask import Flask, request

# 3. 本地模組
from src.scrapers.aivi_scraper import scrape_aivi_news
from src.utils.helpers import format_message
```

## 除錯技巧

### 1. 檢查 LINE Webhook 事件

在 `src/app.py` 的 `handle_message` 函式中加入：

```python
logger.info(f"收到事件: {event}")
logger.info(f"事件類型: {type(event)}")
logger.info(f"訊息內容: {event.message.text}")
```

### 2. 測試爬蟲模組

使用命令列直接測試爬蟲：

```bash
# Python 命令列測試
python -c "
import asyncio
from src.scrapers.aivi_scraper import scrape_aivi_news

result = asyncio.run(scrape_aivi_news())
for article in result:
    print(f'{article[\"title\"]}: {article[\"url\"]}')
"
```

或建立臨時測試腳本：

```python
# test_scraper.py
import asyncio
from src.scrapers.aivi_scraper import scrape_aivi_news

async def main():
    articles = await scrape_aivi_news()
    print(f"爬取到 {len(articles)} 篇文章：")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   {article['url']}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

執行：
```bash
python test_scraper.py
```

### 3. 本機測試 LINE Webhook

使用 ngrok 建立 HTTPS tunnel：

```bash
# Terminal 1: 啟動 Flask 服務
python src/app.py

# Terminal 2: 啟動 ngrok
ngrok http 5000
```

複製 ngrok 提供的 HTTPS URL（例如 `https://abc123.ngrok.io`），到 LINE Developers Console 設定：
- Webhook URL: `https://abc123.ngrok.io/webhook`
- 啟用 "Use webhook"
- 點擊 "Verify" 驗證

### 4. 檢查環境變數

```bash
# 檢查環境變數是否正確載入
python -c "
import os
from dotenv import load_dotenv

load_dotenv()
print('LINE_CHANNEL_SECRET:', os.getenv('LINE_CHANNEL_SECRET'))
print('LINE_CHANNEL_ACCESS_TOKEN:', os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
"
```

### 5. 使用 pytest 的除錯功能

```bash
# 顯示詳細的測試輸出
pytest -v

# 顯示 print 輸出（pytest 預設會隱藏）
pytest -s

# 在第一個失敗時停止
pytest -x

# 進入 Python debugger（測試失敗時）
pytest --pdb
```

## 常見問題

### Q1: 測試時出現 "Event loop is closed" 錯誤

這是 pytest-asyncio 的已知問題。解決方法：

```python
# 在測試檔案開頭加入
import pytest

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
```

### Q2: httpx 請求在測試中很慢

使用 mock 取代真實的 HTTP 請求：

```python
from unittest.mock import AsyncMock, patch

@patch('httpx.AsyncClient.get')
async def test_scraper(mock_get):
    mock_get.return_value.text = "<html>...</html>"
    mock_get.return_value.status_code = 200

    result = await scrape_aivi_news()
    assert len(result) > 0
```

### Q3: 如何測試 LINE Bot 的回覆訊息？

使用 `pytest-mock` 模擬 LINE API：

```python
@pytest.mark.asyncio
async def test_handle_aivi_command(mocker):
    # Mock LINE API client
    mock_api = mocker.Mock()
    mock_event = mocker.Mock()
    mock_event.reply_token = "test_token"

    # Mock 爬蟲結果
    mocker.patch(
        'src.handlers.command_handler.scrape_aivi_news',
        return_value=[{'title': 'Test', 'url': 'https://test.com'}]
    )

    # 執行指令
    await handle_aivi_command(mock_event, mock_api)

    # 驗證 API 呼叫
    assert mock_api.reply_message.called
```

## 效能最佳化建議

### 1. 爬蟲最佳化

- 設定合理的 timeout（目前為 10 秒）
- 使用 HTTP/2（httpx 預設支援）
- 考慮加入快取機制（如果文章不常更新）

### 2. LINE Bot 回應時間

LINE 要求 webhook 在 **3 秒內**回應。目前的實作：
- 爬蟲: ~2 秒
- 格式化: < 0.1 秒
- LINE API 呼叫: ~0.5 秒
- **總計: ~2.6 秒** ✅

如果未來功能變複雜，考慮使用非同步回覆（Push Message）。

### 3. 記憶體使用

- 使用 `selectolax` 而非 `BeautifulSoup`（記憶體使用量減少 50%）
- 限制文章數量（目前為 5 則）
- 及時關閉 HTTP client（使用 `async with`）

## 開發工具推薦

### IDE 設定

推薦使用 **PyCharm** 或 **VS Code**：

#### PyCharm
1. 開啟專案目錄
2. 設定 Python interpreter: `.venv/bin/python`
3. 啟用 pytest 作為預設測試框架
4. 安裝 `.env` 支援插件

#### VS Code
1. 安裝 Python extension
2. 設定 Python interpreter: `.venv/bin/python`
3. 安裝 Pytest extension
4. 安裝 Python Docstring Generator

### 實用套件

```bash
# 程式碼格式化
uv pip install black

# 程式碼檢查
uv pip install ruff

# 型別檢查
uv pip install mypy
```

使用方式：

```bash
# 格式化程式碼
black src/ tests/

# 檢查程式碼品質
ruff check src/ tests/

# 型別檢查
mypy src/
```

## 參考資源

- [LINE Messaging API 文件](https://developers.line.biz/en/docs/messaging-api/)
- [httpx 文件](https://www.python-httpx.org/)
- [selectolax 文件](https://selectolax.readthedocs.io/)
- [pytest 文件](https://docs.pytest.org/)
- [uv 文件](https://docs.astral.sh/uv/)
- [PEP 8 風格指南](https://peps.python.org/pep-0008/)

## 貢獻指南

歡迎貢獻！請遵循以下步驟：

1. Fork 專案
2. 建立功能分支
3. 撰寫測試並確保測試通過
4. 遵循程式碼風格指南
5. 提交 Pull Request

所有 PR 都會經過以下檢查：
- ✅ 測試通過（覆蓋率 > 80%）
- ✅ 程式碼風格符合 PEP 8
- ✅ 所有函式都有 type hints 和文件字串
- ✅ Commit 訊息清楚明確

感謝您的貢獻！
