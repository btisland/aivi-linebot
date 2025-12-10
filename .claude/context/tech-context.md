---
created: 2025-12-10T00:25:29Z
last_updated: 2025-12-10T00:25:29Z
version: 1.0
author: Claude Code PM System
---

# 技術上下文

## Python 環境

### 版本需求
- **Python**: >= 3.10
- **套件管理器**: uv (Astral 開發的快速 Python 套件管理工具)

### 虛擬環境
- **位置**: `.venv/`
- **啟動方式**: `source .venv/bin/activate`
- **管理方式**: uv 自動管理

## 核心相依套件

### 生產環境套件 (dependencies)

| 套件 | 版本 | 用途 |
|------|------|------|
| `line-bot-sdk` | >= 3.0.0 | LINE Messaging API 官方 SDK |
| `httpx` | >= 0.27.0 | 現代非同步 HTTP 客戶端 |
| `selectolax` | >= 0.3.0 | 快速 HTML/XML 解析器 |
| `flask` | >= 3.0.0 | 輕量級 Web 框架 (webhook 服務) |

### 開發環境套件 (optional-dependencies.dev)

| 套件 | 版本 | 用途 |
|------|------|------|
| `pytest` | >= 7.0.0 | 測試框架 |
| `pytest-cov` | >= 4.0.0 | 測試覆蓋率報告 |
| `pytest-asyncio` | >= 0.21.0 | 非同步測試支援 |
| `pytest-mock` | >= 3.10.0 | Mock 功能增強 |

## 技術堆疊說明

### Web 框架 - Flask
**選擇原因**:
- 輕量級，適合簡單的 webhook 服務
- 成熟穩定，社群支援良好
- 部署簡單，資源消耗低

**使用方式**:
- 單一 endpoint: `/webhook`
- 處理 LINE 平台的 POST 請求
- 簽章驗證確保請求來自 LINE

### HTTP 客戶端 - httpx
**選擇原因**:
- 支援非同步請求（async/await）
- API 設計現代化，類似 requests
- 內建 HTTP/2 支援
- 更好的效能和 timeout 控制

**優勢**:
```python
# 非同步爬取，不阻塞主執行緒
async with httpx.AsyncClient() as client:
    response = await client.get(url, timeout=10.0)
```

### HTML 解析 - selectolax
**選擇原因**:
- 基於 Modest engine，速度比 BeautifulSoup 快 5-10 倍
- 記憶體使用量更少
- 支援 CSS 選擇器
- 適合簡單到中等複雜度的爬蟲

**效能比較**:
- BeautifulSoup: ~100ms (10 次解析)
- selectolax: ~10-20ms (10 次解析)

### LINE Bot SDK
**版本**: v3 (最新版本)

**功能使用**:
- Webhook 簽章驗證
- 訊息事件處理
- Reply Message API
- 文字訊息格式化

## 開發工具

### 套件管理 - uv
**特色**:
- Rust 編寫，速度極快
- 相容 pip、pip-tools
- 自動管理虛擬環境
- 鎖定檔案 (`uv.lock`) 確保可重現建置

**常用指令**:
```bash
# 安裝所有相依套件
uv sync --all-extras

# 新增套件
# 1. 編輯 pyproject.toml
# 2. uv sync --all-extras
```

### 測試框架 - pytest
**設定** (pyproject.toml):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=src --cov-report=term-missing"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]
```

**測試策略**:
- 單元測試：快速、隔離、使用 mock
- 整合測試：標記為 `slow`，實際網路請求

### 程式碼品質工具
**目前使用**:
- pytest-cov: 測試覆蓋率 (目標 > 80%)

**未來考慮**:
- black: 程式碼格式化
- ruff: Linting (Rust 編寫，極快)
- mypy: 靜態型別檢查

## CI/CD

### GitHub Actions
**工作流程**: `.github/workflows/sync-to-hf.yml`

**觸發條件**:
- 推送到 `main` 分支

**執行步驟**:
1. Checkout 程式碼
2. 替換 README.md (使用 README_HF.md)
3. 推送到 Hugging Face Space
4. Hugging Face 自動重新建置 Docker image

**需要的 Secret**:
- `HF_TOKEN`: Hugging Face 個人存取權杖 (Write 權限)

## 部署環境

### Hugging Face Space
**類型**: Docker Space (Persistent)

**優勢**:
- 免費方案支援永久運行
- 自動 HTTPS
- 簡單的環境變數管理
- Git-based 部署流程

**容器設定**: `Dockerfile`
```dockerfile
FROM python:3.10-slim
# 安裝 uv、相依套件
# 暴露 PORT (預設 7860)
# 執行 src/app.py
```

**環境變數** (在 HF Space 設定頁面):
- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `PORT` (自動設定為 7860)

## 外部服務

### LINE Messaging API
**用途**: 接收使用者訊息、傳送回覆

**需要設定**:
1. LINE Developers Console 建立 Channel
2. 取得 Channel Secret 和 Access Token
3. 設定 Webhook URL (HF Space URL + `/webhook`)

**API 限制**:
- Reply Message 必須在收到事件後立即使用
- 每個事件只能 reply 一次

### AIVI 科技博客
**爬取目標**: https://blog.aivislab.com/

**爬取內容**:
- 文章標題
- 文章連結
- 最新 5 則文章

**爬取策略**:
- CSS 選擇器定位文章列表
- 無需 JavaScript 渲染
- Timeout: 10 秒
- 錯誤處理：網路錯誤、解析錯誤

## 資料流

```
使用者發送 /aivi
    ↓
LINE Platform → POST /webhook
    ↓
Flask app.py (簽章驗證)
    ↓
handle_message() (指令匹配)
    ↓
command_handler.handle_aivi_command()
    ↓
aivi_scraper.fetch_aivi_news() (非同步爬取)
    ↓
格式化訊息
    ↓
LINE Reply Message API
    ↓
使用者收到文章清單
```

## 效能考量

### 回應時間目標
- 總回應時間: < 10 秒
- 爬蟲請求: < 5 秒
- 訊息處理: < 1 秒

### 資源使用
- 記憶體: ~200MB (Flask + 相依套件)
- CPU: 單核心足夠（低流量）
- 網路: 每次請求 ~50KB (AIVI 頁面大小)

### 擴展性考量
- 目前架構: 單一服務，同步處理
- 流量限制: 低流量個人專案 (< 100 requests/min)
- 擴展方案:
  - 增加快取機制（Redis）
  - 使用非同步框架（FastAPI）
  - 容器橫向擴展
