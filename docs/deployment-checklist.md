# 部署檢查清單

本文件記錄將 AIVI News LINE Bot 部署到 Hugging Face Space 的完整步驟。由於涉及外部服務設定，部分步驟需要手動完成。

## 部署前準備

### 1. 確認帳號與權限

- [ ] **GitHub 帳號**
  - 已登入 GitHub
  - 對 `btisland/aivi-linebot` repository 有 write 權限

- [ ] **Hugging Face 帳號**
  - 已註冊 [Hugging Face](https://huggingface.co/)
  - 已建立 Hugging Face Space：`btisland/aivi-linebot`
  - Space 類型選擇：**Docker**

- [ ] **LINE Developers 帳號**
  - 已登入 [LINE Developers Console](https://developers.line.biz/console/)
  - 已建立 Messaging API Channel
  - 已取得 Channel Secret 和 Channel Access Token

### 2. 確認必要檔案

- [ ] `Dockerfile` 已建立
- [ ] `README_HF.md` 已建立
- [ ] `.github/workflows/sync-to-hf.yml` 已建立
- [ ] `pyproject.toml` 設定正確
- [ ] `uv.lock` 已產生且為最新版本

## 部署步驟

### 步驟 1: 設定 GitHub Secrets

1. 前往 GitHub repository: `https://github.com/btisland/aivi-linebot`
2. 點擊 **Settings** → **Secrets and variables** → **Actions**
3. 點擊 **New repository secret**
4. 新增以下 secret：

   | Name | Value | 說明 |
   |------|-------|------|
   | `HF_TOKEN` | （從 HF Settings 取得） | Hugging Face access token |

#### 如何取得 Hugging Face Token

1. 登入 [Hugging Face](https://huggingface.co/)
2. 點擊右上角頭像 → **Settings**
3. 左側選單選擇 **Access Tokens**
4. 點擊 **New token**
5. 設定：
   - Name: `github-actions-sync`
   - Role: **Write**（需要寫入權限）
6. 點擊 **Generate token**
7. **複製 token**（只會顯示一次！）
8. 貼到 GitHub Secrets 的 `HF_TOKEN` 欄位

**檢查點**：
- [ ] GitHub Secrets 中已新增 `HF_TOKEN`
- [ ] Token 權限為 **Write**

### 步驟 2: 建立 Hugging Face Space

1. 前往 [Hugging Face Spaces](https://huggingface.co/spaces)
2. 點擊 **Create new Space**
3. 設定：
   - **Owner**: `btisland`
   - **Space name**: `aivi-linebot`
   - **License**: MIT
   - **Select the Space SDK**: **Docker**
   - **Space hardware**: CPU Basic（免費）
   - **Visibility**: Public
4. 點擊 **Create Space**

**檢查點**：
- [ ] Hugging Face Space 已建立
- [ ] Space URL: `https://huggingface.co/spaces/btisland/aivi-linebot`
- [ ] SDK 類型為 **Docker**

### 步驟 3: 設定 Hugging Face Space 環境變數

1. 進入您的 Space: `https://huggingface.co/spaces/btisland/aivi-linebot`
2. 點擊 **Settings** 標籤
3. 找到 **Repository secrets** 區塊
4. 新增以下環境變數：

   | Name | Value | 必填 |
   |------|-------|------|
   | `LINE_CHANNEL_SECRET` | （從 LINE Developers 取得） | ✅ |
   | `LINE_CHANNEL_ACCESS_TOKEN` | （從 LINE Developers 取得） | ✅ |
   | `PORT` | `7860` | ❌（預設值） |

#### 如何取得 LINE Credentials

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇您的 Provider
3. 選擇您的 Messaging API Channel
4. **Channel Secret**:
   - 位置：Basic settings 頁面
   - 複製「Channel secret」欄位
5. **Channel Access Token**:
   - 位置：Messaging API 頁面
   - 找到「Channel access token (long-lived)」區塊
   - 如果還沒有 token，點擊「Issue」發行
   - 複製 token

**檢查點**：
- [ ] `LINE_CHANNEL_SECRET` 已設定
- [ ] `LINE_CHANNEL_ACCESS_TOKEN` 已設定
- [ ] 環境變數顯示為 **Secrets**（不可見）

### 步驟 4: 推送到 GitHub main 分支

1. 確認目前在 `epic/news-push-bot` 分支
2. 確認所有變更已提交
3. 將變更 merge 到 `main` 分支：

```bash
# 切換到 main 分支
git checkout main

# 合併 epic 分支
git merge epic/news-push-bot

# 推送到 GitHub
git push origin main
```

**注意**：推送到 `main` 分支會自動觸發 GitHub Actions！

**檢查點**：
- [ ] 變更已推送到 `main` 分支
- [ ] GitHub Actions workflow 已自動觸發

### 步驟 5: 監控 GitHub Actions 執行

1. 前往 GitHub repository
2. 點擊 **Actions** 標籤
3. 查看最新的 workflow run：「Sync to Hugging Face」
4. 點擊進入，查看執行細節

**可能的狀態**：
- ✅ **Success**: 同步成功
- ❌ **Failure**: 同步失敗（檢查錯誤訊息）

**常見錯誤**：
- `Authentication failed`: 檢查 `HF_TOKEN` 是否正確
- `remote: Repository not found`: 檢查 Hugging Face Space 是否已建立
- `Permission denied`: 檢查 token 權限是否為 Write

**檢查點**：
- [ ] GitHub Actions workflow 執行成功
- [ ] 查看 logs 確認推送到 HF 成功

### 步驟 6: 監控 Hugging Face Space 建置

1. 前往您的 Space: `https://huggingface.co/spaces/btisland/aivi-linebot`
2. 點擊 **Logs** 標籤
3. 觀察 Docker build 過程

**建置階段**：
1. **Fetching**: 下載程式碼
2. **Building**: 建置 Docker image
3. **Running**: 啟動容器

**預期時間**：初次建置約 3-5 分鐘

**可能的錯誤**：
- `Dockerfile not found`: 確認 `Dockerfile` 在 repository 根目錄
- `pip install failed`: 檢查 `pyproject.toml` 和 `uv.lock`
- `Port 7860 is already in use`: 不太可能發生，但可能需要重啟

**檢查點**：
- [ ] Docker build 成功
- [ ] 容器啟動成功
- [ ] 查看 logs 確認 Flask 服務正在運行
- [ ] Space 狀態顯示為 **Running**

### 步驟 7: 設定 LINE Webhook URL

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇您的 Messaging API Channel
3. 進入「Messaging API」頁面
4. 找到「Webhook settings」區塊
5. 點擊「Edit」
6. 輸入 Webhook URL：
   ```
   https://btisland-aivi-linebot.hf.space/webhook
   ```
7. 點擊「Update」
8. 啟用「Use webhook」開關
9. 點擊「Verify」按鈕

**預期結果**：
- ✅ Webhook URL 驗證成功
- 顯示 **Success**

**如果驗證失敗**：
- 檢查 Hugging Face Space 是否正在運行
- 檢查 URL 是否正確（`/webhook` 結尾）
- 查看 HF Space logs 是否有錯誤訊息
- 確認環境變數已正確設定

**檢查點**：
- [ ] Webhook URL 已設定
- [ ] 「Use webhook」已啟用
- [ ] Webhook URL 驗證成功

### 步驟 8: 停用自動回覆訊息（可選）

如果不想要 LINE 的預設自動回覆：

1. 在 LINE Developers Console 的同一頁面
2. 找到「Auto-reply messages」區塊
3. 點擊「Edit」
4. 關閉「Auto-reply messages」開關

**檢查點**：
- [ ] 自動回覆已停用（如果需要）

## 部署後驗證

### 測試 1: 健康檢查

在瀏覽器開啟：
```
https://btisland-aivi-linebot.hf.space/
```

**預期結果**：
- 看到回應（即使是 404 或其他，表示服務有回應）

### 測試 2: Webhook 端對端測試

1. 在 LINE 中加入您的 Bot 為好友
2. 傳送 `/aivi` 指令
3. 等待 3-10 秒

**預期結果**：
- ✅ Bot 回覆 5 則 AIVI 文章（標題 + 連結）

**如果沒有回覆**：
- 檢查 HF Space logs（可能有錯誤訊息）
- 檢查 LINE webhook 是否已啟用
- 在 LINE Developers Console 查看 webhook logs
- 手動測試爬蟲功能（見下方）

### 測試 3: 手動測試爬蟲功能

在本機執行：

```bash
# 啟動虛擬環境
source .venv/bin/activate

# 測試爬蟲
python -c "
import asyncio
from src.scrapers.aivi_scraper import scrape_aivi_news

articles = asyncio.run(scrape_aivi_news())
print(f'爬取到 {len(articles)} 篇文章')
for article in articles:
    print(f'- {article[\"title\"]}')
"
```

**預期結果**：
- 顯示 5 篇文章標題

**檢查點**：
- [ ] 服務健康檢查通過
- [ ] Webhook 端對端測試通過
- [ ] 爬蟲功能正常運作

## 監控與維護

### 日常監控

定期檢查（建議每週）：
- [ ] Hugging Face Space 是否正常運行
- [ ] GitHub Actions 是否有失敗的 workflow
- [ ] LINE webhook logs 是否有異常

### 查看 Hugging Face Space Logs

```bash
# 方法 1: 在 HF Space UI 查看
https://huggingface.co/spaces/btisland/aivi-linebot → Logs 標籤

# 方法 2: 使用 HF CLI（需安裝）
huggingface-cli space logs btisland/aivi-linebot
```

### 查看 LINE Webhook Logs

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇您的 Messaging API Channel
3. 進入「Messaging API」頁面
4. 找到「Webhook」區塊
5. 點擊「View logs」

## 更新部署

### 方式 1: 自動部署（推薦）

只要推送到 GitHub `main` 分支，GitHub Actions 會自動同步到 HF Space：

```bash
# 在 epic 分支完成開發
git checkout epic/news-push-bot
git add .
git commit -m "Issue #X: 功能更新"
git push origin epic/news-push-bot

# Merge 到 main（自動觸發部署）
git checkout main
git merge epic/news-push-bot
git push origin main
```

### 方式 2: 手動推送到 Hugging Face

如果 GitHub Actions 失敗，可手動推送：

```bash
# 新增 HF remote
git remote add hf https://huggingface.co/spaces/btisland/aivi-linebot

# 推送到 HF
git push hf main --force
```

**注意**：需要先設定 HF credentials（使用 `huggingface-cli login`）

## 回滾（Rollback）

如果新版本有問題，回滾到上一個版本：

```bash
# 1. 在本機回滾
git checkout main
git reset --hard HEAD~1

# 2. 強制推送（觸發重新部署）
git push origin main --force
```

**警告**：`--force` 會覆蓋遠端歷史，謹慎使用！

## 除錯指南

### 問題：GitHub Actions 推送失敗

**症狀**：
```
remote: Permission denied
fatal: Authentication failed
```

**解決方法**：
1. 檢查 `HF_TOKEN` 是否正確
2. 確認 token 權限為 **Write**
3. 重新產生 token 並更新 GitHub Secrets

### 問題：Docker build 失敗

**症狀**：
```
ERROR: failed to solve: process "/bin/sh -c uv sync --frozen" did not complete successfully
```

**解決方法**：
1. 檢查 `pyproject.toml` 語法
2. 確認 `uv.lock` 已提交到 repository
3. 本機測試 Docker build：
   ```bash
   docker build -t aivi-linebot-test .
   ```

### 問題：Flask 服務無法啟動

**症狀**：HF Space logs 顯示 port 錯誤或匯入錯誤

**解決方法**：
1. 檢查 `PORT` 環境變數（應為 7860）
2. 確認 `src/app.py` 中的 port 設定正確
3. 檢查所有模組匯入路徑

### 問題：LINE webhook 驗證失敗

**症狀**：LINE Developers Console 顯示 webhook URL 無法連線

**解決方法**：
1. 確認 HF Space 狀態為 **Running**
2. 檢查 webhook URL 是否正確（`/webhook` 結尾）
3. 查看 HF Space logs 是否有錯誤
4. 確認環境變數 `LINE_CHANNEL_SECRET` 已設定

### 問題：Bot 無法回覆訊息

**症狀**：傳送 `/aivi` 沒有回應

**解決方法**：
1. 查看 HF Space logs（可能有錯誤訊息）
2. 檢查 LINE webhook logs（是否有收到事件）
3. 確認環境變數 `LINE_CHANNEL_ACCESS_TOKEN` 已設定
4. 手動測試爬蟲功能（見上方）
5. 檢查 AIVI 網站是否變更 HTML 結構

## 總結檢查清單

### 部署前
- [ ] 所有檔案已建立且正確
- [ ] 測試通過（pytest）
- [ ] 變更已提交到 Git

### 部署中
- [ ] GitHub Secrets 已設定（HF_TOKEN）
- [ ] Hugging Face Space 已建立
- [ ] HF Space 環境變數已設定
- [ ] 推送到 main 分支
- [ ] GitHub Actions 執行成功
- [ ] HF Space 建置成功

### 部署後
- [ ] Webhook URL 已設定並驗證
- [ ] 端對端測試通過（傳送 `/aivi` 有回覆）
- [ ] 定期監控服務狀態

## 相關連結

- [GitHub Repository](https://github.com/btisland/aivi-linebot)
- [Hugging Face Space](https://huggingface.co/spaces/btisland/aivi-linebot)
- [LINE Developers Console](https://developers.line.biz/console/)
- [Hugging Face Docs - Spaces](https://huggingface.co/docs/hub/spaces)
- [LINE Messaging API Docs](https://developers.line.biz/en/docs/messaging-api/)

---

**最後更新**: 2025-12-09
如有任何問題，請查看 [docs/development.md](development.md) 或提交 GitHub Issue。
