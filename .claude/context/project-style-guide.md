---
created: 2025-12-10T00:25:29Z
last_updated: 2025-12-10T00:25:29Z
version: 1.0
author: Claude Code PM System
---

# 專案風格指南

## 語言規範

### 繁體中文台灣用語
**重要**: 本專案所有溝通、文件、註解一律使用**繁體中文台灣用語**。

#### 術語對照表
| 簡中/其他 | 台灣用語 |
|----------|---------|
| 菜單 | 選單 |
| 配置 | 設定 |
| 信息 | 訊息 |
| 存儲 | 儲存 |
| 集成 | 整合 |
| 內存 | 記憶體 |
| 文檔 | 文件 |
| 批量 | 批次 |
| 字符 | 字元 |
| 變量 | 變數 |
| 數據 | 資料 |
| 緩存 | 快取 |
| 庫 | 套件 |
| 模塊 | 模組 |
| 服務端 | 伺服器端 |
| 客戶端 | 用戶端 |
| 數據庫 | 資料庫 |
| 字段 | 欄位 |

### 程式碼註解語言
**繁體中文**，使用台灣用語。

```python
# ✅ 正確
def fetch_aivi_news(limit: int = 5):
    """
    爬取 AIVI 科技博客最新文章

    參數:
        limit: 要爬取的文章數量

    回傳:
        文章清單，每個元素包含標題和連結
    """
```

## Python 程式碼風格

### 命名慣例

#### 變數和函式
使用 **snake_case**（小寫 + 底線）

```python
# ✅ 正確
user_name = "Joseph"
article_count = 5

def fetch_news_articles():
    pass

def handle_aivi_command(event, line_bot_api):
    pass
```

```python
# ❌ 錯誤
userName = "Joseph"  # camelCase
ArticleCount = 5     # PascalCase

def fetchNewsArticles():  # camelCase
    pass
```

#### 類別
使用 **PascalCase**（每個字首字母大寫）

```python
# ✅ 正確
class NewsArticle:
    pass

class CommandHandler:
    pass
```

#### 常數
使用 **UPPER_SNAKE_CASE**（全大寫 + 底線）

```python
# ✅ 正確
MAX_ARTICLES = 5
DEFAULT_TIMEOUT = 10.0
AIVI_BLOG_URL = "https://blog.aivislab.com/"
```

#### 私有成員
使用 **單底線前綴** (慣例，非強制)

```python
# ✅ 正確
class Scraper:
    def __init__(self):
        self._cache = {}  # 私有屬性

    def _parse_html(self, html):  # 私有方法
        pass
```

### 型別提示

**必須**: 所有函式使用型別提示

```python
# ✅ 正確
def fetch_aivi_news(limit: int = 5) -> list[dict]:
    """爬取文章"""
    pass

async def get_html(url: str) -> str:
    """取得網頁內容"""
    pass

def handle_command(event: MessageEvent, api: LineBotApi) -> None:
    """處理指令"""
    pass
```

```python
# ❌ 錯誤
def fetch_aivi_news(limit=5):  # 無型別提示
    pass
```

### Docstring 格式

使用 **Google Style Docstrings**（繁體中文）

```python
def fetch_aivi_news(limit: int = 5) -> list[dict]:
    """
    爬取 AIVI 科技博客最新文章。

    此函式會發送 HTTP 請求到 AIVI 博客，解析 HTML 內容，
    並提取最新文章的標題和連結。

    參數:
        limit: 要爬取的文章數量，預設為 5

    回傳:
        文章清單，格式為:
        [
            {"title": "文章標題", "link": "https://..."},
            ...
        ]

    拋出:
        httpx.RequestError: 網路請求失敗時
        Exception: HTML 解析失敗時

    範例:
        >>> articles = await fetch_aivi_news(3)
        >>> print(len(articles))
        3
    """
```

### Import 順序

遵循 **PEP 8** 建議：

```python
# 1. 標準庫
import os
import asyncio
from typing import Optional

# 2. 第三方套件
import httpx
from flask import Flask, request
from linebot import LineBotApi

# 3. 專案內模組
from scrapers.aivi_scraper import fetch_aivi_news
from handlers.command_handler import handle_aivi_command
```

### 行長度
**最大 88 字元** (Black 預設值)

```python
# ✅ 可接受
def very_long_function_name(
    first_parameter: str,
    second_parameter: int,
    third_parameter: bool = False
) -> Optional[dict]:
    pass
```

### 縮排
**4 個空格**（不使用 Tab）

### 空行
- 函式之間：2 個空行
- 類別之間：2 個空行
- 函式內邏輯區塊：1 個空行

```python
class MyClass:
    pass


class AnotherClass:
    pass


def my_function():
    # 初始化
    x = 1

    # 處理邏輯
    result = x + 1

    return result


def another_function():
    pass
```

## 檔案結構慣例

### 模組檔案
- 檔名: `lowercase_with_underscores.py`
- 每個檔案專注單一職責

```
✅ 正確:
src/scrapers/aivi_scraper.py
src/handlers/command_handler.py

❌ 錯誤:
src/scrapers/AiviScraper.py
src/handlers/CommandHandler.py
```

### 測試檔案
- 格式: `test_<module_name>.py`
- 測試函式: `test_<function_name>`

```python
# tests/test_scrapers/test_aivi_scraper.py

@pytest.mark.asyncio
async def test_fetch_aivi_news():
    """測試爬取新聞功能"""
    pass

def test_parse_article_element():
    """測試文章元素解析"""
    pass
```

### `__init__.py`
保持簡潔，僅用於套件標記（通常為空）

```python
# ✅ 正確
# src/scrapers/__init__.py
# (空檔案)

# ❌ 避免
# src/scrapers/__init__.py
from .aivi_scraper import fetch_aivi_news  # 非必要
```

## 錯誤處理風格

### 明確的異常類型

```python
# ✅ 正確
try:
    response = await client.get(url)
except httpx.RequestError as e:
    logger.error(f"網路請求失敗: {e}")
    raise
except Exception as e:
    logger.error(f"未預期的錯誤: {e}")
    raise
```

```python
# ❌ 錯誤
try:
    response = await client.get(url)
except:  # 過於寬泛
    pass
```

### 友善的錯誤訊息

```python
# ✅ 正確 - 給使用者的訊息
error_message = "抱歉，目前無法取得新聞資訊。\n請稍後再試，或直接訪問 AIVI 博客。"

# ✅ 正確 - 給開發者的 log
logger.error(f"爬蟲失敗: {url}, 錯誤: {str(e)}, Stack: {traceback.format_exc()}")
```

## 註解風格

### 何時寫註解
1. **複雜邏輯**: 需要解釋「為什麼」
2. **非直觀行為**: 特殊處理
3. **暫時解決方案**: 標註 TODO

```python
# ✅ 好的註解
# 使用 asyncio.run() 因為 Flask 是同步框架
# 未來考慮遷移到 FastAPI 以原生支援非同步
news = asyncio.run(fetch_aivi_news(limit=5))

# TODO: 加入快取機制減少重複爬取
# Issue #42: https://github.com/.../issues/42
```

```python
# ❌ 不必要的註解
# 設定 limit 為 5
limit = 5

# 呼叫函式
result = fetch_news()
```

### TODO 格式

```python
# TODO(Joseph): 實作 Redis 快取
# TODO: 加入重試機制 - Issue #42
# FIXME: 此處可能有競態條件
# HACK: 臨時解決方案，等上游修復後移除
```

## Git Commit 規範

### Commit Message 格式

```
<type>: <subject>

<body>

<footer>
```

### Type 類型
- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文件變更
- `style`: 程式碼格式（不影響功能）
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 建置/工具變更

### 範例

```
feat: 加入 /tech 指令支援 TechCrunch 新聞

實作新的爬蟲模組 tech_scraper.py，支援爬取 TechCrunch
最新 5 則文章。包含單元測試和整合測試。

Closes #15
```

```
fix: 修正 AIVI 爬蟲解析錯誤

AIVI 網站更新結構，調整 CSS 選擇器以匹配新的
HTML 結構。新增更嚴謹的錯誤處理。

Fixes #23
```

### 禁止內容
❌ 不要加入 `Co-Authored-By: Claude` 等 AI 署名

## 測試風格

### 測試命名

```python
# ✅ 清楚描述測試情境
def test_fetch_aivi_news_returns_correct_count():
    pass

def test_handle_aivi_command_with_network_error():
    pass

def test_parse_html_with_empty_content():
    pass
```

### Arrange-Act-Assert 模式

```python
def test_fetch_news():
    # Arrange (準備)
    expected_count = 5

    # Act (執行)
    result = await fetch_aivi_news(limit=5)

    # Assert (驗證)
    assert len(result) == expected_count
    assert all("title" in article for article in result)
```

### Mock 使用

```python
def test_handle_command_with_mock(mocker):
    # Mock 外部相依
    mock_fetch = mocker.patch('scrapers.aivi_scraper.fetch_aivi_news')
    mock_fetch.return_value = [
        {"title": "測試文章", "link": "https://..."}
    ]

    # 測試 handler 邏輯
    handle_aivi_command(event, line_bot_api)
```

## 文件風格

### Markdown 慣例
- 標題階層清楚（H1 > H2 > H3）
- 使用列表呈現步驟
- 程式碼區塊標註語言

````markdown
## 安裝步驟

1. 安裝相依套件
   ```bash
   uv sync --all-extras
   ```

2. 設定環境變數
   ```bash
   cp .env.example .env
   ```
````

### README 結構
1. 專案簡介
2. 功能特色
3. 技術架構
4. 快速開始
5. 開發指南
6. 部署流程
7. 常見問題
8. 授權資訊

## 程式碼審查標準

### 必須檢查項目
- ✅ 型別提示完整
- ✅ Docstring 存在且正確
- ✅ 測試覆蓋新增的程式碼
- ✅ 無 linter 錯誤
- ✅ 遵循命名慣例
- ✅ 錯誤處理適當
- ✅ 註解使用繁體中文台灣用語

### 建議檢查項目
- 是否有過度設計
- 是否可簡化邏輯
- 是否有重複程式碼
- 是否符合 SOLID 原則

## 工具建議

### 推薦工具
- **格式化**: `black` (88 字元)
- **Linting**: `ruff` (快速、現代)
- **型別檢查**: `mypy`
- **Import 排序**: `isort`

### 未來整合
這些工具目前未強制使用，但建議在 pre-commit hooks 中加入。

---

**記住**: 一致性比完美更重要。當有疑問時，參考現有程式碼的風格。
