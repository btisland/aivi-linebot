---
created: 2025-12-10T00:25:29Z
last_updated: 2025-12-10T00:25:29Z
version: 1.0
author: Claude Code PM System
---

# 系統架構模式

## 整體架構風格

### Webhook-Based 事件驅動架構
專案採用事件驅動架構，由 LINE Platform 主動推送事件到我們的 webhook。

```
LINE Platform (事件源)
    ↓ HTTP POST
Webhook Endpoint (app.py)
    ↓ 事件分發
Command Handlers (處理邏輯)
    ↓ 資料抓取
Scrapers (外部資料源)
    ↓ 格式化回應
LINE Reply API (回應使用者)
```

**優勢**:
- 即時回應使用者訊息
- 無需輪詢，節省資源
- 可靠的訊息傳遞（LINE 平台保證）

## 核心設計模式

### 1. Handler Pattern (指令處理模式)
**位置**: `src/handlers/command_handler.py`

**結構**:
```python
def handle_aivi_command(event, line_bot_api):
    """處理 /aivi 指令"""
    # 1. 呼叫爬蟲
    # 2. 格式化訊息
    # 3. 回傳給使用者
```

**優勢**:
- 單一職責：每個指令一個 handler
- 易於擴展：新增指令只需新增 handler
- 可測試性高：獨立測試每個 handler

**擴展方式**:
```python
# app.py 中的路由邏輯
if text.lower() == "/aivi":
    handle_aivi_command(event, line_bot_api)
elif text.lower() == "/news":  # 未來新指令
    handle_news_command(event, line_bot_api)
```

### 2. Scraper Pattern (爬蟲模式)
**位置**: `src/scrapers/aivi_scraper.py`

**結構**:
```python
async def fetch_aivi_news(limit: int = 5) -> list[dict]:
    """
    非同步爬取 AIVI 最新文章

    Returns:
        [{"title": str, "link": str}, ...]
    """
```

**特徵**:
- **非同步設計**: 使用 `async/await` 避免阻塞
- **結構化回傳**: 統一的資料格式 (dict)
- **錯誤處理**: 網路錯誤、解析錯誤都有處理
- **可設定性**: 透過參數控制爬取數量

**資料流**:
```
HTTP 請求 → HTML 內容 → CSS 選擇器 → 結構化資料
```

### 3. Dependency Injection (相依性注入)
**範例**: `line_bot_api` 傳遞

```python
# app.py - 建立 API 實例
line_bot_api = LineBotApi(channel_access_token)

# 傳遞給 handler
handle_aivi_command(event, line_bot_api)
```

**優勢**:
- 可測試性：測試時可注入 mock 物件
- 解耦：handler 不直接建立相依物件
- 彈性：可抽換不同的 API 實作

## 錯誤處理策略

### 分層錯誤處理

**第一層：Webhook 層** (`app.py`)
```python
@app.route("/webhook", methods=['POST'])
def webhook():
    try:
        # 簽章驗證
        # 事件處理
    except InvalidSignatureError:
        # 記錄並回傳 400
    except Exception as e:
        # 記錄並回傳 500
```

**第二層：Handler 層** (`command_handler.py`)
```python
def handle_aivi_command(event, line_bot_api):
    try:
        # 呼叫爬蟲
        news = asyncio.run(fetch_aivi_news())
    except Exception as e:
        # 友善錯誤訊息給使用者
        reply_text = "抱歉，目前無法取得新聞..."
```

**第三層：Scraper 層** (`aivi_scraper.py`)
```python
async def fetch_aivi_news():
    try:
        # HTTP 請求
    except httpx.RequestError:
        # 網路錯誤
        raise
    except Exception:
        # 解析錯誤
        raise
```

### 錯誤訊息設計原則
- **對使用者**: 友善、具體、提供替代方案
- **對開發者**: 詳細、包含 stack trace、記錄到 log

## 資料流模式

### 請求-回應流程
```
1. LINE User → LINE Platform
   (傳送 "/aivi")

2. LINE Platform → Our Webhook
   (POST /webhook with signature)

3. Webhook → Handler
   (驗證簽章後分發事件)

4. Handler → Scraper
   (asyncio.run(fetch_aivi_news()))

5. Scraper → External Website
   (httpx.AsyncClient.get())

6. External Website → Scraper
   (HTML 內容)

7. Scraper → Handler
   (結構化資料)

8. Handler → LINE Platform
   (line_bot_api.reply_message())

9. LINE Platform → LINE User
   (文章清單)
```

### 非同步處理模式
**問題**: Flask 是同步框架，但爬蟲需要非同步

**解決方案**: 在同步 context 中使用 `asyncio.run()`
```python
# 同步函式中呼叫非同步函式
news = asyncio.run(fetch_aivi_news(limit=5))
```

**未來改進**: 考慮使用 FastAPI（原生非同步支援）

## 測試模式

### 單元測試策略
**Scraper 測試** (`test_aivi_scraper.py`):
```python
@pytest.mark.asyncio
async def test_fetch_aivi_news():
    # 實際網路請求（標記為 slow）
    news = await fetch_aivi_news(limit=3)
    assert len(news) == 3
```

**Handler 測試** (`test_command_handler.py`):
```python
def test_handle_aivi_command(mocker):
    # Mock 爬蟲函式
    mock_fetch = mocker.patch('scrapers.aivi_scraper.fetch_aivi_news')
    # 測試 handler 邏輯
```

### 整合測試策略
**端對端測試** (`test_command_flow.py`):
```python
@pytest.mark.slow
def test_full_command_flow():
    # 模擬 LINE webhook 請求
    # 驗證完整流程
```

## 設定管理模式

### 環境變數載入
**位置**: `app.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()  # 載入 .env 檔案

channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
```

**環境隔離**:
- **開發**: `.env` 檔案（不提交）
- **生產**: Hugging Face Space 環境變數設定

### 設定分層
1. **預設值**: 程式碼中的 fallback
2. **環境變數**: 覆寫預設值
3. **執行時參數**: 最高優先級（目前未使用）

## 部署模式

### 容器化部署
**Dockerfile 結構**:
```dockerfile
# 1. 基礎映像
FROM python:3.10-slim

# 2. 安裝相依套件
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync

# 3. 複製應用程式
COPY src/ ./src/

# 4. 暴露 Port
EXPOSE 7860

# 5. 啟動服務
CMD ["python", "src/app.py"]
```

### Git-based 部署流程
```
開發者 push → GitHub main
    ↓
GitHub Actions 觸發
    ↓
同步到 Hugging Face Space
    ↓
HF Space 自動 rebuild Docker
    ↓
服務重啟，新版本上線
```

## 可擴展性考量

### 目前架構限制
- 單一 webhook endpoint
- 同步處理訊息（Flask）
- 無快取機制
- 單一資料來源（AIVI）

### 擴展路徑

**1. 新增指令**:
```python
# 新增 handler
def handle_tech_news_command(event, line_bot_api):
    pass

# 路由中加入
if text.lower() == "/tech":
    handle_tech_news_command(event, line_bot_api)
```

**2. 新增資料源**:
```python
# src/scrapers/tech_scraper.py
async def fetch_tech_news():
    pass
```

**3. 效能優化**:
- 加入 Redis 快取爬蟲結果
- 遷移到 FastAPI (原生非同步)
- 使用 background tasks 處理慢速請求

**4. 監控與觀測**:
- 加入結構化 logging
- 整合 APM 工具（如 Sentry）
- 追蹤回應時間指標

## 安全模式

### Webhook 簽章驗證
```python
@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)  # SDK 驗證簽章
    except InvalidSignatureError:
        abort(400)
```

**防護**:
- 防止偽造請求
- 確保訊息來自 LINE Platform

### 敏感資料管理
- **Channel Secret** 和 **Access Token** 不提交到 Git
- 使用環境變數注入
- `.env.example` 提供範本但不包含實際值
