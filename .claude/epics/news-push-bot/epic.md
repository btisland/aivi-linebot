---
name: news-push-bot
status: backlog
created: 2025-12-09T07:51:33Z
progress: 0%
prd: .claude/prds/news-push-bot.md
github: https://github.com/btisland/aivi-linebot/issues/1
---

# Epic: news-push-bot

## 概述

實作一個輕量級的 LINE bot 指令處理功能，當使用者傳送 `/aivi` 指令時，即時爬取 AIVI 科技博客首頁（https://www.aivi.fyi/），提取最新 5 則文章的標題與連結，並以格式化訊息回傳給使用者。

**核心技術策略**：採用簡潔的模組化架構，使用高效能的 Python 爬蟲套件，整合現有（或新建）的 LINE bot webhook 機制，確保 10 秒內完成整個流程。

## 架構決策

### AD-1: 網頁爬取技術選型
**決策**：使用 `httpx` + `selectolax`
**理由**：
- `httpx` 提供現代化的 async HTTP client，效能優於 requests
- `selectolax` 是基於 C 的快速 HTML 解析器，比 BeautifulSoup4 快 5-10 倍
- 適合解析靜態 HTML（AIVI 網站不需要 JavaScript 渲染）
- 輕量級，相依套件少，部署簡單
**備案**：若網站有 JavaScript 渲染需求，改用 `playwright` 無頭瀏覽器

### AD-2: LINE bot 框架
**決策**：使用官方 `line-bot-sdk` Python 套件
**理由**：
- LINE 官方維護，API 相容性佳
- 文件完整，社群支援充足
- 提供完整的 webhook 處理與訊息回覆功能
- 輕量級，適合單一功能 bot

### AD-3: 程式架構設計
**決策**：採用三層分離架構
```
指令處理層（Handler）→ 爬蟲服務層（Scraper）→ 訊息格式化層（Formatter）
```
**理由**：
- 關注點分離，各層職責明確
- 爬蟲邏輯可獨立測試，不依賴 LINE bot
- 易於擴展（未來可新增其他新聞來源）
- 便於維護（網站結構改變只需調整 Scraper）

### AD-4: 錯誤處理策略
**決策**：快速失敗（Fail Fast）+ 友善錯誤訊息
**理由**：
- 單一使用者場景，不需複雜的重試機制
- 網路錯誤最多重試 2 次（避免超時）
- 所有錯誤都回傳清楚的中文訊息給使用者
- 記錄完整錯誤日誌供除錯使用

### AD-5: 訊息格式設計
**決策**：使用簡單文字訊息 + emoji
**理由**：
- 實作簡單，不需處理複雜的 Flex Message JSON
- 可讀性高，符合使用者需求
- 效能佳，傳輸資料量小
- 格式範例：
```
📰 AIVI 最新文章

1. 文章標題一
   🔗 https://www.aivi.fyi/article-1

2. 文章標題二
   🔗 https://www.aivi.fyi/article-2
```

### AD-6: 部署策略
**決策**：GitHub → Hugging Face Space，Webhook 部署在 Hugging Face
**理由**：
- 程式碼先推送到 GitHub 進行版本控制
- 透過 GitHub Actions 自動同步到 Hugging Face Space
- Webhook 服務運行在 Hugging Face Space（免費且穩定）
- 本機開發使用 ngrok 建立 HTTPS tunnel 供測試
**部署流程**：
1. 本機開發與測試
2. 推送到 GitHub main 分支
3. GitHub Actions 自動同步到 Hugging Face
4. Hugging Face Space 自動重新部署 webhook 服務

### AD-7: 套件管理工具
**決策**：使用 `uv` 作為套件管理工具
**理由**：
- 比 pip 快 10-100 倍的安裝速度
- 內建虛擬環境管理（`uv venv`）
- 現代化的相依套件解析
- 與 pyproject.toml 完美整合
- 專案已採用 uv，保持一致性
**使用方式**：
```bash
# 安裝相依套件
uv sync --all-extras

# 新增套件
編輯 pyproject.toml → uv sync
```

### AD-8: 測試策略（本機 vs CI）
**決策**：本機「小步快跑」，CI「完整驗證」
**理由**：
- 本機開發需要快速迭代與即時回饋
- CI 環境負責守護程式碼品質的最後一道防線
- 避免本機執行耗時測試影響開發節奏
- 確保合併到 main 的程式碼都經過完整驗證

**本機開發測試策略**：
- ✅ 小步快跑，只執行快速測試
- ✅ 不跑完整測試與 coverage
- ✅ 測試單一分支時，覆蓋率可能只有約 75%，本機不要求補齊
- ✅ 專注於當前修改的模組，快速驗證邏輯正確性

**CI 測試策略（GitHub Actions）**：
- ✅ 執行完整測試（包括標記為 `slow` 的測試）
- ✅ 開啟 coverage 分析
- ✅ 使用 `--cov-fail-under=80` 門檻檢查
- ✅ 未達標即禁止合併到 main

**測試標記範例**：
```python
import pytest

@pytest.mark.slow
def test_full_scraping_with_real_network():
    """標記為 slow 的測試只在 CI 執行"""
    pass

def test_parse_article_html():
    """快速單元測試，本機和 CI 都會執行"""
    pass
```

## 技術方案

### 爬蟲模組（Scraper Module）

#### 核心功能
- 發送 HTTP GET 請求至 AIVI 首頁
- 解析 HTML 結構，提取文章元素
- 提取每篇文章的標題與 URL
- 返回結構化資料（list of dict）

#### AIVI 網站 HTML 結構
**重要**：新聞文章的標題和連結位於 `<h2>` 標籤內的 `<a>` 元素中

**實際 HTML 結構**：
```html
<h2 class="archive__item-title no_toc" itemprop="headline">
  <a href="/llms/introduce-Nano-Banana-Pro" rel="permalink">
    🚀Nano Banana Pro全能实测！强得离谱！...
  </a>
</h2>
```

**CSS 選擇器策略**：
- **選項 1（推薦）**：`h2.archive__item-title > a`（使用 class 選擇器，更精確）
- **選項 2**：`h2[itemprop="headline"] > a`（使用 itemprop 屬性）
- **選項 3**：`h2 > a[rel="permalink"]`（使用 rel 屬性）

#### 技術實作細節
```python
# 資料結構
Article = {
    "title": str,  # 文章標題
    "url": str     # 文章完整 URL
}

# 函式簽章
async def scrape_aivi_news(max_articles: int = 5) -> List[Article]

# 選擇器範例（使用 selectolax）
from selectolax.parser import HTMLParser

def parse_articles(html: str, max_articles: int = 5) -> List[Article]:
    """解析 AIVI 首頁 HTML，提取文章資訊

    參數：
        html: AIVI 首頁的 HTML 內容
        max_articles: 最多返回幾則文章（預設 5）

    返回：
        文章清單，每個元素包含 title 和 url
    """
    tree = HTMLParser(html)
    articles = []

    # 使用 class 選擇器定位文章連結
    for link in tree.css('h2.archive__item-title > a'):
        title = link.text(strip=True)
        url = link.attributes.get('href', '')

        # 處理相對路徑（加上網域）
        if url.startswith('/'):
            url = f'https://www.aivi.fyi{url}'

        articles.append({
            'title': title,
            'url': url
        })

        # 達到數量限制即停止
        if len(articles) >= max_articles:
            break

    return articles
```

#### 錯誤處理
- `httpx.TimeoutException`: 5 秒 timeout，重試 2 次
- `httpx.HTTPError`: 記錄 HTTP 狀態碼，回傳空清單
- `selectolax.parser.ParsingError`: 記錄完整 HTML，回傳錯誤
- 找不到文章元素：記錄「HTML 結構可能已變更」警告，回傳空清單

### LINE Bot 整合模組

#### 核心功能
- 接收並驗證 LINE webhook 請求
- 解析使用者訊息，識別 `/aivi` 指令（不區分大小寫）
- 呼叫爬蟲模組取得新聞資料
- 格式化訊息並回傳給使用者
- 處理所有異常情況

#### Webhook 處理流程
1. 接收 LINE webhook POST 請求
2. 驗證簽章（LINE Channel Secret）
3. 解析事件類型（MessageEvent）
4. 檢查訊息類型（TextMessage）
5. 比對指令（`/aivi`，不區分大小寫）
6. 觸發新聞爬取
7. 格式化並回覆訊息

#### 技術實作細節
```python
# 指令匹配邏輯
command = message_text.strip().lower()
if command == "/aivi":
    # 觸發新聞爬取
```

### 訊息格式化模組

#### 核心功能
- 將文章清單轉換為格式化的 LINE 文字訊息
- 處理空清單情況（無文章）
- 確保訊息長度符合 LINE 限制（5000 字元）

#### 格式化邏輯
```python
def format_news_message(articles: List[Article]) -> str:
    if not articles:
        return "目前沒有找到新文章"

    message = "📰 AIVI 最新文章\n\n"
    for i, article in enumerate(articles[:5], 1):
        message += f"{i}. {article['title']}\n"
        message += f"   🔗 {article['url']}\n\n"

    return message.strip()
```

### 基礎設施需求

#### 環境變數
```bash
LINE_CHANNEL_SECRET=xxx
LINE_CHANNEL_ACCESS_TOKEN=xxx
```

#### 套件管理（使用 uv）
**重要**：本專案使用 `uv` 進行套件管理，不使用 pip

**安裝相依套件**：
```bash
# 安裝所有相依套件（含 dev 套件）
uv sync --all-extras

# 只安裝生產相依套件
uv sync
```

**新增套件流程**：
1. 編輯 `pyproject.toml`，在 `dependencies` 或 `optional-dependencies[dev]` 區段加入套件
2. 執行 `uv sync --all-extras`
3. uv 會自動更新 `uv.lock` 並安裝套件

#### 套件相依（pyproject.toml）
```toml
[project]
dependencies = [
    "line-bot-sdk>=3.0.0",
    "httpx>=0.27.0",
    "selectolax>=0.3.0",
    "flask>=3.0.0",  # 或 fastapi
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
]
```

#### Webhook Endpoint
- Route: `POST /webhook`
- 接收 LINE 平台的事件通知
- 驗證請求來源
- 處理訊息事件
- 部署位置：Hugging Face Space

## 實作策略

### 開發階段

#### Phase 1: 爬蟲核心開發
**目標**：獨立完成 AIVI 網站爬蟲，可單獨測試
**產出**：
- `src/scrapers/aivi_scraper.py`
- 單元測試檔案

**關鍵任務**：
1. 分析 AIVI 網站 HTML 結構（手動檢查）
2. 實作 HTTP 請求與 HTML 解析邏輯
3. 處理邊界情況（無文章、網站無法訪問）
4. 撰寫單元測試（mock HTTP 回應）

#### Phase 2: LINE Bot 整合
**目標**：建立 webhook 服務並整合爬蟲模組
**產出**：
- `src/handlers/command_handler.py`
- `src/app.py`（webhook 服務入口）

**關鍵任務**：
1. 設定 LINE bot 開發環境（ngrok 用於本機測試）
2. 實作 webhook 接收與簽章驗證
3. 實作 `/aivi` 指令處理邏輯
4. 整合爬蟲模組
5. 實作訊息格式化與回覆

#### Phase 3: 測試與優化
**目標**：確保各種情境都能正確處理
**產出**：完整測試涵蓋率與效能優化

**關鍵任務**：
1. 端對端測試（實際在 LINE 中測試）
2. 錯誤情境測試（網站無法訪問、解析失敗）
3. 效能測試（確保 < 10 秒回應）
4. 日誌與監控設定

### 風險緩解

| 風險 | 影響 | 緩解策略 |
|------|------|----------|
| AIVI 網站結構改變 | 高 | 模組化爬蟲邏輯；記錄完整 HTML 以便快速調整 |
| 網站有反爬蟲機制 | 中 | 設定合理的 User-Agent；控制請求頻率 |
| LINE API 限制 | 低 | 單一使用者，流量極低 |
| 網路不穩定 | 中 | 實作重試機制；設定合理 timeout |

### 測試策略

本專案採用「本機快速迭代」+「CI 完整驗證」的雙軌測試策略。

#### 本機測試（小步快跑）
**目標**：快速驗證當前修改的邏輯，不阻礙開發節奏

**執行方式**：
```bash
# 只執行快速測試（排除 slow 標記）
pytest -m "not slow"

# 或測試特定模組
pytest tests/test_scraper.py
```

**特點**：
- ✅ 只執行快速單元測試
- ✅ 不執行完整測試套件
- ✅ 不執行 coverage 分析
- ✅ 測試單一分支時，覆蓋率可能只有 75%，本機不要求補齊
- ✅ 專注於當前修改的邏輯正確性

#### CI 測試（完整驗證）
**目標**：確保合併到 main 的程式碼品質達標

**GitHub Actions 設定**：
```yaml
# .github/workflows/test.yml 範例
- name: Run tests with coverage
  run: |
    pytest --cov=src --cov-report=term --cov-fail-under=80
```

**特點**：
- ✅ 執行所有測試（包括標記為 `slow` 的測試）
- ✅ 啟用 coverage 分析
- ✅ 使用 `--cov-fail-under=80` 門檻檢查
- ✅ 未達標則 CI 失敗，禁止合併到 main

#### 測試分類

**快速單元測試**（本機 + CI 都執行）：
- 爬蟲模組：Mock HTTP 回應，測試解析邏輯
- 格式化模組：測試各種資料輸入（空清單、多筆資料）
- 指令處理：測試指令匹配邏輯（大小寫、前後空白）

**慢速測試**（僅 CI 執行，標記為 `@pytest.mark.slow`）：
- 真實網路請求測試（實際爬取 AIVI 網站）
- 端對端整合測試（完整流程測試）
- 效能基準測試（回應時間驗證）

#### 測試標記範例
```python
import pytest

# 快速單元測試（本機會執行）
def test_parse_html_structure():
    """測試 HTML 解析邏輯"""
    html = '<h2 class="archive__item-title"><a href="/test">Title</a></h2>'
    articles = parse_articles(html)
    assert len(articles) == 1
    assert articles[0]['title'] == 'Title'

# 慢速測試（只在 CI 執行）
@pytest.mark.slow
def test_real_aivi_website_scraping():
    """實際連線測試 AIVI 網站"""
    articles = await scrape_aivi_news()
    assert len(articles) > 0
```

#### 手動測試檢查清單（部署前）
- [ ] 正常情況：傳送 `/aivi`，收到 1-5 則新聞
- [ ] 大小寫：測試 `/AIVI`、`/Aivi` 等變體
- [ ] 錯誤處理：中斷網路連線，檢查錯誤訊息
- [ ] 效能：測量從傳送指令到收到回覆的時間
- [ ] 連結可用性：點擊回覆中的連結，確認可正常開啟

## 工作分解預覽

以下為高階工作分類，將在 epic decompose 階段細化：

- [ ] **環境建置**：建立專案結構、安裝相依套件、設定環境變數
- [ ] **AIVI 爬蟲實作**：分析網站結構、實作爬蟲邏輯、錯誤處理
- [ ] **LINE Bot Webhook**：建立 webhook 服務、簽章驗證、事件處理
- [ ] **指令處理器**：實作 `/aivi` 指令匹配與執行邏輯
- [ ] **訊息格式化**：實作文章清單格式化為 LINE 訊息
- [ ] **整合與測試**：端對端測試、錯誤情境測試、效能驗證
- [ ] **文件與部署**：撰寫使用說明、部署至正式環境

**預估工作量**：7 個主要任務，每個任務 2-4 小時

## 相依性

### 外部相依
- **LINE Messaging API**
  - 狀態：需確認 Channel 已建立
  - 取得：LINE Developers Console
  - 影響：無 Channel 無法測試與部署

- **AIVI 網站可用性**
  - 狀態：需驗證可正常訪問
  - 檢查：測試爬取與解析
  - 影響：網站結構改變需調整爬蟲邏輯

### 技術相依
- **Python 套件**
  - `line-bot-sdk`: LINE bot 核心功能
  - `httpx`: 非同步 HTTP 客戶端
  - `selectolax`: 快速 HTML 解析
  - `flask` 或 `fastapi`: Webhook 服務框架

### 開發環境相依
- **Python 3.10+**: 需使用現代 Python 特性（type hints, async/await）
- **ngrok** 或類似工具：本機開發時需要 HTTPS tunnel 供 LINE webhook 使用
- **網路連線**：開發與測試階段需能訪問 AIVI 網站與 LINE API

### 內部相依
- **專案結構**：需建立 `src/` 目錄與子模組
- **設定檔**：需建立 `.env` 或類似機制管理敏感資訊

## 成功標準（技術層面）

### 功能驗收標準
- ✅ 使用者傳送 `/aivi` 指令後，10 秒內收到回覆
- ✅ 回覆包含 1-5 則 AIVI 最新文章（標題 + URL）
- ✅ 文章連結可正常點擊並開啟正確頁面
- ✅ 指令不區分大小寫（`/aivi`、`/AIVI`、`/Aivi` 均有效）
- ✅ 網站無法訪問時，回傳友善的錯誤訊息
- ✅ 網站無文章時，回傳「目前沒有找到新文章」
- ✅ 程式碼包含清晰的繁體中文註解

### 效能標準
- ✅ 95% 的請求在 10 秒內完成
- ✅ 平均回應時間 < 5 秒
- ✅ HTTP 請求 timeout 設定為 5 秒
- ✅ 最多重試 2 次（總共 3 次嘗試）

### 品質標準
- ✅ 爬蟲邏輯有單元測試涵蓋
- ✅ 指令處理邏輯有單元測試涵蓋
- ✅ 至少一個端對端測試
- ✅ 程式碼遵循 Python PEP 8 風格規範
- ✅ 無 critical 或 high severity 的程式碼問題

### 可靠性標準
- ✅ 爬取失敗不會導致 bot 崩潰
- ✅ 所有異常都有適當的錯誤處理
- ✅ 錯誤日誌包含足夠的除錯資訊
- ✅ 成功率 > 95%（排除目標網站故障）

### 可維護性標準
- ✅ 爬蟲邏輯與 bot 邏輯分離（不同檔案）
- ✅ 關鍵函式有 docstring 說明
- ✅ 網站 HTML 選擇器集中在設定區域（易於調整）
- ✅ README 包含本機開發與部署說明

## 預估工作量

### 時程預估
- **Phase 1（爬蟲核心）**：4-6 小時
  - 網站結構分析：1 小時
  - 爬蟲邏輯實作：2-3 小時
  - 單元測試：1-2 小時

- **Phase 2（Bot 整合）**：4-6 小時
  - Webhook 服務建立：2-3 小時
  - 指令處理實作：1-2 小時
  - 訊息格式化：1 小時

- **Phase 3（測試優化）**：3-4 小時
  - 端對端測試：1-2 小時
  - 錯誤情境測試：1 小時
  - 效能驗證與優化：1 小時

**總預估時間**：11-16 小時（約 2-3 個工作天）

### 資源需求
- **開發人員**：1 位 Python 後端工程師
- **技能要求**：
  - 熟悉 Python async/await
  - 了解 HTTP 協定與網頁爬蟲
  - LINE bot 開發經驗（或願意學習）

### 關鍵路徑
1. 取得 LINE Channel credentials（先決條件）
2. 建立開發環境（虛擬環境、套件安裝）
3. 實作爬蟲核心（阻塞後續工作）
4. 建立 webhook 服務（需 ngrok 或部署環境）
5. 端對端測試（需 LINE Channel 可用）

## 技術債務與後續優化

雖不在當前範圍，但值得記錄供未來參考：

### 效能優化
- 實作快取機制（避免短時間內重複爬取）
- 使用 Redis 快取最近一次的新聞結果（TTL: 5 分鐘）

### 功能擴展
- 支援更多新聞來源（設計可擴展的爬蟲介面）
- 實作定時推播（Cron job + 訊息推送）
- 使用者訂閱管理（資料庫儲存偏好）

### 監控與可觀測性
- 整合 Application Performance Monitoring（如 Sentry）
- 建立儀表板監控爬取成功率
- 設定告警通知（網站結構改變、爬取失敗率過高）

### 架構演進
- 微服務化（爬蟲服務獨立部署）
- 使用訊息佇列（RabbitMQ/Redis Queue）處理非同步爬取
- 容器化部署（Docker + Kubernetes）

## Tasks Created
- [ ] #2 - 專案環境建置與套件管理設定 (parallel: true)
- [ ] #3 - AIVI 網站爬蟲核心模組實作 (parallel: true)
- [ ] #4 - AIVI 爬蟲模組單元測試 (parallel: false)
- [ ] #5 - LINE Bot Webhook 服務建立 (parallel: true)
- [ ] #6 - 指令處理器與訊息格式化實作 (parallel: false)
- [ ] #7 - 整合測試與端對端驗證 (parallel: false)
- [ ] #8 - 文件撰寫與 Hugging Face 部署
Sync to Hugging Face (parallel: false)

總任務數：       7
可並行任務：       3
循序任務：4
## 附錄

### 相關文件
- PRD: `.claude/prds/news-push-bot.md`
- LINE Messaging API 文件: https://developers.line.biz/en/docs/messaging-api/
- httpx 文件: https://www.python-httpx.org/
- selectolax 文件: https://selectolax.readthedocs.io/

### 決策記錄（補充）
- **為何不用 Selenium/Playwright**：AIVI 網站是靜態 HTML，不需要執行 JavaScript，使用輕量級工具即可
- **為何不用 Flex Message**：簡單文字訊息已滿足需求，避免過度工程化
- **為何不實作快取**：MVP 階段專注核心功能，單一使用者場景下快取效益有限
- **為何選擇 httpx 而非 requests**：httpx 支援 async/await，效能更好，且為現代化的 HTTP 客戶端

### 開發環境設定參考

#### 初次設定
```bash
# 1. 建立虛擬環境（使用 uv）
uv venv

# 2. 啟動虛擬環境
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# 3. 安裝所有相依套件（含 dev 套件）
uv sync --all-extras

# 4. 設定環境變數
cp .env.example .env
# 編輯 .env，填入 LINE Channel credentials
```

#### 日常開發流程
```bash
# 1. 啟動虛擬環境
source .venv/bin/activate

# 2. 執行快速測試（本機）
pytest -m "not slow"

# 3. 執行本機開發伺服器
python src/app.py

# 4. 使用 ngrok 建立 HTTPS tunnel（供 LINE webhook 測試）
ngrok http 5000
# 將 ngrok 提供的 URL 設定到 LINE Developers Console
```

#### 新增套件
```bash
# 1. 編輯 pyproject.toml，加入套件版本
# 例如：在 dependencies 區段加入 "requests==2.31.0"

# 2. 同步相依套件（uv 會自動更新 uv.lock）
uv sync --all-extras

# 3. 提交變更
git add pyproject.toml uv.lock
git commit -m "Add new dependency: requests"
```

#### 部署到 Hugging Face
```bash
# 1. 推送到 GitHub main 分支
git push origin main

# 2. GitHub Actions 自動同步到 Hugging Face
# 3. Hugging Face Space 自動重新部署
# 4. 檢查 Hugging Face Space 日誌確認部署成功
```
