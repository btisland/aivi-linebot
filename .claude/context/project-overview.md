---
created: 2025-12-10T00:25:29Z
last_updated: 2025-12-10T00:25:29Z
version: 1.0
author: Claude Code PM System
---

# 專案概覽

## 功能摘要

AIVI News LINE Bot 是一個輕量級的新聞查詢機器人，提供即時的 AIVI 科技博客文章查詢功能。

### 核心功能清單

1. **新聞查詢** (`/aivi` 指令)
   - 即時爬取 AIVI 科技博客最新文章
   - 回傳文章標題和連結
   - 預設顯示最新 5 則文章

2. **Webhook 服務**
   - 接收 LINE Platform 的訊息事件
   - 驗證 webhook 簽章
   - 分發事件到對應的處理器

3. **錯誤處理**
   - 網路錯誤提示
   - 解析錯誤處理
   - 友善的使用者錯誤訊息

4. **自動化部署**
   - GitHub Actions CI/CD
   - 自動同步到 Hugging Face Space
   - Docker 容器化部署

## 目前狀態

### 開發階段
**狀態**: ✅ MVP 完成，生產環境運行中

### 已實作功能
- ✅ LINE Bot 基礎架構
- ✅ `/aivi` 指令處理
- ✅ AIVI 科技博客爬蟲
- ✅ 錯誤處理機制
- ✅ 單元測試和整合測試
- ✅ CI/CD 自動部署
- ✅ Docker 容器化
- ✅ 完整專案文件

### 待實作功能
- ⏳ 更多新聞來源支援
- ⏳ 快取機制
- ⏳ 監控和日誌系統
- ⏳ 使用者訂閱功能
- ⏳ 定期推播功能

## 整合點

### 外部服務整合

#### 1. LINE Messaging API
**整合方式**: LINE Bot SDK v3
**功能**:
- Webhook 事件接收
- Reply Message API
- 簽章驗證

**設定需求**:
- Channel Secret
- Channel Access Token
- Webhook URL 設定

#### 2. AIVI 科技博客
**整合方式**: 網頁爬蟲
**URL**: https://blog.aivislab.com/
**爬取方式**:
- httpx AsyncClient (HTTP 請求)
- selectolax (HTML 解析)
- CSS 選擇器定位文章

**爬取內容**:
- 文章標題
- 文章連結
- 最新 5 則文章

#### 3. Hugging Face Space
**整合方式**: Git-based 部署
**功能**:
- Docker 容器運行
- 自動重新建置
- 環境變數管理

**部署流程**:
```
GitHub main 分支
    ↓
GitHub Actions
    ↓
Hugging Face Space
    ↓
Docker Rebuild
    ↓
服務上線
```

## 技術堆疊

### 後端
- **語言**: Python 3.10+
- **Web 框架**: Flask 3.0+
- **LINE SDK**: line-bot-sdk 3.0+
- **HTTP 客戶端**: httpx 0.27+
- **HTML 解析**: selectolax 0.3+

### 測試
- **框架**: pytest 7.0+
- **覆蓋率**: pytest-cov 4.0+
- **非同步**: pytest-asyncio 0.21+
- **Mock**: pytest-mock 3.10+

### DevOps
- **套件管理**: uv
- **CI/CD**: GitHub Actions
- **容器化**: Docker
- **部署平台**: Hugging Face Space

### 開發工具
- **IDE**: PyCharm (設定已提交)
- **版本控制**: Git + GitHub
- **專案管理**: Claude Code PM System

## 架構概覽

### 高層架構圖
```
┌─────────────┐
│ LINE User   │
└──────┬──────┘
       │ /aivi
       ↓
┌─────────────────┐
│ LINE Platform   │
└──────┬──────────┘
       │ Webhook POST
       ↓
┌──────────────────────┐
│ Flask App (app.py)   │
│ - 簽章驗證           │
│ - 事件路由           │
└──────┬───────────────┘
       │
       ↓
┌───────────────────────┐
│ Command Handler       │
│ - handle_aivi_command │
└──────┬────────────────┘
       │
       ↓
┌──────────────────────┐
│ AIVI Scraper         │
│ - fetch_aivi_news    │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│ AIVI 科技博客        │
│ (blog.aivislab.com)  │
└──────────────────────┘
```

### 資料流
```
1. 使用者發送指令 → LINE Platform
2. LINE Platform → Webhook (POST + 簽章)
3. Flask 驗證簽章 → 分發事件
4. Handler 呼叫爬蟲 → fetch_aivi_news()
5. 爬蟲請求網站 → 解析 HTML
6. 回傳結構化資料 → Handler
7. 格式化訊息 → LINE Reply API
8. LINE Platform → 推送給使用者
```

## 效能特性

### 回應時間
- **目標**: < 10 秒
- **實際**: 通常 5-8 秒
- **瓶頸**: 網頁爬取時間（3-5 秒）

### 資源使用
- **記憶體**: ~200MB (Flask + 相依套件)
- **CPU**: 單核心足夠
- **網路**: 每次請求 ~50KB

### 可擴展性
- **目前**: 單一容器，同步處理
- **限制**: 低流量場景（< 100 req/min）
- **擴展**: 可加入快取、異步處理、負載平衡

## 可靠性與穩定性

### 錯誤處理層級
1. **Webhook 層**: InvalidSignatureError → 400
2. **Handler 層**: Exception → 友善錯誤訊息
3. **Scraper 層**: RequestError → 網路錯誤處理

### 容錯機制
- ✅ Timeout 設定（10 秒）
- ✅ 錯誤訊息友善化
- ✅ 簽章驗證防偽造請求
- ⏳ 重試機制（未實作）
- ⏳ Circuit breaker（未實作）

### 監控
- ⏳ 日誌系統（規劃中）
- ⏳ 錯誤追蹤（Sentry, 規劃中）
- ⏳ 效能監控（APM, 規劃中）

## 安全性

### 已實作
- ✅ Webhook 簽章驗證
- ✅ 環境變數管理（敏感資料不提交）
- ✅ HTTPS（HF Space 預設提供）

### 待加強
- ⏳ Rate limiting
- ⏳ 輸入驗證強化
- ⏳ 日誌脫敏

## 測試策略

### 測試覆蓋
- **單元測試**: 爬蟲、處理器
- **整合測試**: 端對端流程
- **覆蓋率**: > 80%

### 測試分類
- **快速測試**: 使用 mock，< 1 秒
- **慢速測試**: 實際網路請求，標記為 `@pytest.mark.slow`

### CI 整合
- GitHub Actions 自動執行測試
- 測試失敗會阻止部署

## 部署流程

### 環境
- **開發**: 本機 (`.venv` + `.env`)
- **生產**: Hugging Face Space (Docker)

### 部署步驟
```bash
# 1. 本機開發測試
pytest -m "not slow"

# 2. 提交變更
git add .
git commit -m "描述變更"
git push origin main

# 3. GitHub Actions 自動觸發
# - 執行測試
# - 同步到 HF Space

# 4. HF Space 自動重新建置
# - Docker build
# - 服務重啟
```

### 回滾策略
- Git revert 不良提交
- 推送回滾的 commit
- 自動觸發重新部署

## 文件資源

### 使用者文件
- `README.md` - 專案說明、使用方式
- `README_HF.md` - Hugging Face Space 專用說明

### 開發文件
- `docs/development.md` - 開發指南
- `docs/deployment-checklist.md` - 部署檢查清單
- `docs/test-results.md` - 測試結果文件

### 系統文件
- `.claude/context/` - 專案上下文（本目錄）
- `CLAUDE.md` - Claude 開發規則

## 維護與支援

### 維護活動
- ✅ 定期更新相依套件
- ✅ 監控測試覆蓋率
- ✅ 檢查部署狀態
- ⏳ 監控效能指標（規劃中）

### 問題追蹤
- GitHub Issues（目前無開啟的 issue）
- Epic 系統（`.claude/epics/`）

### 貢獻指南
- 開源專案，歡迎貢獻
- 提交前請確保測試通過
- 遵循專案程式碼風格

## 未來發展

### 短期 (1-3 個月)
- 新增更多新聞來源
- 實作快取機制
- 加入監控系統

### 中期 (3-6 個月)
- 使用者訂閱功能
- 定期推播
- Rich Menu 整合

### 長期 (6+ 個月)
- 個人化推薦
- 多語言支援
- 資料分析儀表板
