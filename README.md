# AIVI News LINE Bot

輕量級的 LINE bot，當使用者傳送 `/aivi` 指令時，即時爬取 [AIVI 科技博客](https://blog.aivislab.com/)最新 5 則文章並回傳。

## 功能特色

- 📰 爬取 AIVI 最新文章（標題 + 連結）
- 🤖 LINE Bot 指令處理（`/aivi`）
- ⚡️ 快速回應（< 10 秒）
- 🛡️ 完整的錯誤處理與友善錯誤訊息
- 🔍 不區分大小寫的指令匹配

## 技術架構

- **爬蟲**：httpx + selectolax（輕量、快速的 HTML 解析）
- **Bot 框架**：line-bot-sdk + Flask
- **套件管理**：uv（快速的 Python 套件管理工具）
- **測試**：pytest + pytest-asyncio + pytest-cov
- **部署**：Hugging Face Space（使用 Docker）

## 專案結構

```
aivi-linebot/
├── src/
│   ├── scrapers/        # 爬蟲模組
│   │   └── aivi_scraper.py
│   ├── handlers/        # LINE Bot 指令處理器
│   │   └── command_handler.py
│   ├── utils/           # 工具函式
│   └── app.py           # Flask webhook 服務入口
├── tests/               # 測試檔案
│   ├── test_scrapers/
│   └── test_handlers/
├── docs/                # 文件
│   ├── development.md   # 開發指南
│   └── deployment-checklist.md  # 部署檢查清單
├── .github/workflows/   # CI/CD 設定
│   └── sync-to-hf.yml
├── Dockerfile           # Hugging Face Space 部署用
├── README_HF.md         # Hugging Face Space 說明文件
├── .env.example         # 環境變數範本
├── pyproject.toml       # 專案設定與相依套件
└── uv.lock              # 套件版本鎖定檔
```

## 本機開發

### 前置需求

- Python 3.10 或以上版本
- [uv](https://docs.astral.sh/uv/) 套件管理工具
- LINE Bot 帳號（需要 Channel Secret 和 Channel Access Token）

### 環境建置

#### 1. 安裝相依套件

本專案使用 `uv` 作為套件管理工具：

```bash
# 建立虛擬環境並安裝所有相依套件（含 dev 套件）
uv sync --all-extras

# 啟動虛擬環境
source .venv/bin/activate
```

#### 2. 設定環境變數

複製 `.env.example` 為 `.env` 並填入您的 LINE Bot 憑證：

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

```bash
LINE_CHANNEL_SECRET=你的_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=你的_access_token
PORT=5000
```

#### 3. 取得 LINE Bot 憑證

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 建立新的 Provider（如果還沒有）
3. 建立新的 Messaging API Channel
4. 在 Channel 設定頁面取得：
   - **Channel Secret**（基本設定頁面）
   - **Channel Access Token**（Messaging API 頁面，需要先發行 Long-lived token）

### 執行測試

```bash
# 快速測試（本機開發用，排除慢速測試）
pytest -m "not slow"

# 完整測試（含 coverage 報告）
pytest --cov=src --cov-report=term-missing

# 執行特定測試檔案
pytest tests/test_scrapers/test_aivi_scraper.py
```

### 執行服務

```bash
# 啟動 Flask webhook 服務
python src/app.py
```

服務會在 `http://localhost:5000` 啟動，webhook endpoint 為 `/webhook`。

#### 本機測試 Webhook

由於 LINE webhook 需要 HTTPS，本機開發時可使用 [ngrok](https://ngrok.com/) 建立 tunnel：

```bash
# 安裝 ngrok（如果還沒安裝）
brew install ngrok

# 建立 HTTPS tunnel
ngrok http 5000
```

ngrok 會提供一個 HTTPS URL（例如 `https://abc123.ngrok.io`），將此 URL + `/webhook` 設定到 LINE Developers Console 的 Webhook URL 欄位。

### 新增相依套件

編輯 `pyproject.toml`，在適當的區段加入套件：

```toml
# 生產環境套件
dependencies = [
    "新套件名稱>=版本號",
]

# 或開發環境套件
[project.optional-dependencies]
dev = [
    "新套件名稱>=版本號",
]
```

然後執行：

```bash
uv sync --all-extras
```

## 部署流程

本專案使用 GitHub Actions 自動同步到 Hugging Face Space：

1. **推送到 GitHub main 分支**
   ```bash
   git push origin main
   ```

2. **GitHub Actions 自動觸發**
   - `.github/workflows/sync-to-hf.yml` 會自動執行
   - 將專案同步到 Hugging Face Space

3. **Hugging Face Space 自動重新部署**
   - 使用 `Dockerfile` 建置 Docker image
   - 自動啟動服務

詳細的部署設定步驟請參考 [docs/deployment-checklist.md](docs/deployment-checklist.md)。

## 使用方式

1. 在 LINE 中加入您的 Bot 為好友
2. 傳送 `/aivi` 指令
3. Bot 會回傳 AIVI 科技博客最新 5 則文章的標題和連結

## 開發指南

詳細的開發指南請參考 [docs/development.md](docs/development.md)，包含：
- 詳細的專案結構說明
- 開發流程與分支策略
- 測試策略與除錯技巧
- 程式碼風格指南

## 技術亮點

### 爬蟲實作
- 使用 `httpx` 進行非同步 HTTP 請求
- 使用 `selectolax` 進行快速 HTML 解析（比 BeautifulSoup 快 5-10 倍）
- 完整的錯誤處理與 timeout 設定

### LINE Bot 整合
- 使用 LINE Bot SDK v3（最新版本）
- Webhook 簽章驗證
- 非同步訊息處理

### 測試與品質
- 單元測試覆蓋率 > 80%
- 整合測試涵蓋主要流程
- 使用 pytest markers 區分快速與慢速測試

## 常見問題

### Q: 為什麼使用 selectolax 而不是 BeautifulSoup？
A: `selectolax` 是基於 Modest engine 的 HTML/XML 解析器，速度比 BeautifulSoup 快 5-10 倍，且記憶體使用量更少。對於簡單的爬蟲任務，selectolax 是更好的選擇。

### Q: 為什麼選擇 Hugging Face Space 而不是其他平台？
A: Hugging Face Space 提供免費的 Docker 容器部署，支援永久運行的服務（Persistent Space），適合部署 webhook 服務。相較於 Heroku（已取消免費方案）或 AWS（需要信用卡），HF Space 是個人專案的理想選擇。

### Q: 如何新增其他指令？
A: 在 `src/handlers/` 建立新的指令處理器，然後在 `src/app.py` 的 `handle_message` 函式中加入對應的判斷邏輯。記得撰寫測試！

## 授權

MIT License

## 相關連結

- [LINE Developers Console](https://developers.line.biz/console/)
- [Hugging Face Spaces](https://huggingface.co/spaces)
- [AIVI 科技博客](https://blog.aivislab.com/)
- [uv 文件](https://docs.astral.sh/uv/)
