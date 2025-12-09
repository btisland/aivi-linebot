# AI 新聞推播 LINE Bot

自動爬取台灣新聞網站（自由時報、聯合報），並透過 LINE Bot 推播給使用者的智慧型新聞服務。

## 功能特色

- 自動爬取台灣主要新聞網站
- 支援多種新聞分類（政治、社會、生活等）
- 透過 LINE Bot 推播新聞
- 使用者可透過指令訂閱/取消訂閱新聞
- 定時推播機制

## 技術架構

- **Web Framework**: Flask
- **HTTP Client**: httpx
- **HTML Parser**: selectolax
- **LINE Bot SDK**: line-bot-sdk
- **Testing**: pytest
- **Package Manager**: uv

## 環境建置

### 前置需求

- Python 3.10 或以上版本
- [uv](https://docs.astral.sh/uv/) 套件管理工具
- LINE Bot 帳號（需要 Channel Secret 和 Channel Access Token）

### 安裝步驟

#### 1. 建立虛擬環境與安裝相依套件

本專案使用 `uv` 作為套件管理工具。執行以下指令安裝所有相依套件（含開發用套件）：

```bash
# 安裝所有相依套件（含 dev 套件）
uv sync --all-extras

# 如果只需要安裝生產環境相依套件
uv sync
```

執行完成後，`uv` 會自動：
- 建立虛擬環境（`.venv/`）
- 安裝 `pyproject.toml` 中定義的所有套件
- 生成 `uv.lock` 檔案

#### 2. 設定環境變數

複製 `.env.example` 為 `.env` 並填入您的 LINE Bot 憑證：

```bash
cp .env.example .env
```

編輯 `.env` 檔案，填入真實的 LINE Bot 資訊：

```bash
LINE_CHANNEL_SECRET=你的_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=你的_access_token
```

#### 3. 啟動虛擬環境

```bash
source .venv/bin/activate
```

### 取得 LINE Bot 憑證

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 建立新的 Provider（如果還沒有）
3. 建立新的 Messaging API Channel
4. 在 Channel 設定頁面取得：
   - Channel Secret（基本設定頁面）
   - Channel Access Token（Messaging API 頁面，需要先發行）

## 專案結構

```
aivi-linebot/
├── src/
│   ├── scrapers/        # 爬蟲模組
│   ├── handlers/        # LINE Bot 指令處理器
│   ├── utils/           # 工具函式
│   └── app.py           # Webhook 服務入口
├── tests/               # 測試檔案
│   ├── test_scrapers/
│   └── test_handlers/
├── .env.example         # 環境變數範本
├── pyproject.toml       # 專案設定與相依套件
└── README.md
```

## 開發指南

### 執行測試

```bash
# 執行所有測試
pytest

# 執行測試並顯示覆蓋率
pytest --cov

# 執行特定測試檔案
pytest tests/test_scrapers/test_ltn.py
```

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

## 授權

[待補充]
