---
created: 2025-12-10T00:25:29Z
last_updated: 2025-12-10T00:25:29Z
version: 1.0
author: Claude Code PM System
---

# 專案結構

## 目錄架構

```
aivi-linebot/
├── .claude/                    # Claude Code 專案管理
│   ├── commands/              # 自訂斜線指令
│   ├── context/               # 專案上下文文件（本目錄）
│   ├── epics/                 # Epic 追蹤
│   ├── hooks/                 # Git hooks
│   ├── rules/                 # 開發規則
│   └── scripts/               # 管理腳本
│
├── .github/                   # GitHub 設定
│   └── workflows/
│       └── sync-to-hf.yml    # Hugging Face 同步 CI/CD
│
├── .idea/                     # PyCharm IDE 設定
│
├── .venv/                     # Python 虛擬環境 (uv 管理)
│
├── docs/                      # 專案文件
│   ├── deployment-checklist.md  # 部署檢查清單
│   ├── development.md           # 開發指南
│   └── test-results.md          # 測試結果文件
│
├── src/                       # 主要程式碼
│   ├── __init__.py
│   ├── app.py                 # Flask webhook 入口
│   ├── handlers/              # 指令處理器
│   │   ├── __init__.py
│   │   └── command_handler.py
│   ├── scrapers/              # 網頁爬蟲
│   │   ├── __init__.py
│   │   └── aivi_scraper.py
│   └── utils/                 # 工具函式
│       └── __init__.py
│
├── tests/                     # 測試檔案
│   ├── __init__.py
│   ├── test_handlers/         # 指令處理器測試
│   │   └── __init__.py
│   ├── test_integration/      # 整合測試
│   │   ├── __init__.py
│   │   └── test_command_flow.py
│   └── test_scrapers/         # 爬蟲測試
│       ├── __init__.py
│       └── test_aivi_scraper.py
│
├── .coverage                  # Coverage 報告資料
├── .env.example               # 環境變數範本
├── .gitignore                 # Git 忽略清單
├── CLAUDE.md                  # Claude 開發規則
├── Dockerfile                 # Docker 容器設定
├── pyproject.toml             # Python 專案設定
├── README.md                  # 專案說明（GitHub）
├── README_HF.md               # 專案說明（Hugging Face）
└── uv.lock                    # 套件版本鎖定
```

## 模組組織

### src/ 模組
所有應用程式邏輯放在 `src/` 目錄下，不打包到 site-packages。

**執行方式**:
```bash
source .venv/bin/activate
python src/app.py
```

### 核心模組說明

#### app.py - Flask Webhook 服務
- LINE Bot webhook endpoint (`/webhook`)
- 簽章驗證
- 訊息事件路由

#### scrapers/ - 爬蟲模組
- `aivi_scraper.py`: AIVI 科技博客爬蟲
  - 使用 httpx (非同步 HTTP)
  - 使用 selectolax (快速 HTML 解析)
  - 回傳最新 5 則文章

#### handlers/ - 指令處理器
- `command_handler.py`: `/aivi` 指令處理
  - 不區分大小寫的指令匹配
  - 訊息格式化
  - 錯誤處理

#### utils/ - 工具函式
- 保留供未來擴充
- 目前為空模組

## 測試結構

### 測試組織原則
- 測試檔案名稱格式: `test_*.py`
- 測試類別格式: `Test*`
- 測試函式格式: `test_*`

### 測試類型分佈
1. **單元測試** (`test_scrapers/`, `test_handlers/`)
   - 測試個別模組功能
   - 使用 mock 隔離相依性

2. **整合測試** (`test_integration/`)
   - 測試端對端流程
   - 標記為 `@pytest.mark.slow`

### 測試執行
```bash
# 快速測試（排除慢速）
pytest -m "not slow"

# 完整測試含覆蓋率
pytest --cov=src --cov-report=term-missing
```

## 檔案命名慣例

### Python 檔案
- 模組: `lowercase_with_underscores.py`
- 類別內部使用: `ClassName`
- 函式: `function_name()`
- 常數: `CONSTANT_NAME`

### 文件檔案
- 一律使用小寫加連字符: `deployment-checklist.md`
- 避免空格和特殊字元

### 設定檔
- 環境變數範本: `.env.example`
- Python 設定: `pyproject.toml`
- Docker: `Dockerfile` (無副檔名)

## 路徑約定

### 絕對路徑使用時機
- 讀寫專案根目錄檔案
- CI/CD 腳本中

### 相對路徑使用時機
- 模組內 import
- 測試檔案中的測試資料

### Import 模式
```python
# 正確：從 src 根目錄 import
from scrapers.aivi_scraper import fetch_aivi_news
from handlers.command_handler import handle_aivi_command

# 避免：相對 import
# from ..scrapers import aivi_scraper  # 不推薦
```

## 設定檔位置

### 專案層級
- `pyproject.toml` - Python 專案設定、相依套件、pytest 設定
- `uv.lock` - 套件版本鎖定（由 uv 自動產生，需提交）
- `.gitignore` - Git 忽略規則

### 開發工具
- `.idea/` - PyCharm 設定（部分提交）
- `.venv/` - 虛擬環境（不提交）

### 部署
- `Dockerfile` - Hugging Face Space 部署
- `.github/workflows/sync-to-hf.yml` - 自動同步腳本

### Claude Code
- `CLAUDE.md` - 開發規則（專案根目錄）
- `.claude/` - 指令、上下文、Epic 管理

## 特殊目錄說明

### .claude/epics/
Epic 追蹤系統，記錄大型功能開發：
- `news-push-bot/` - 新聞推送功能 Epic
  - `execution-status.md` - 執行狀態
  - `updates/` - 進度更新

### .github/workflows/
GitHub Actions CI/CD：
- `sync-to-hf.yml` - 推送到 main 分支時自動同步到 Hugging Face
