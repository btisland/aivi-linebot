---
title: AIVI News LINE Bot
emoji: 📰
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "4.44.0"
pinned: false
license: mit
---

# AIVI News LINE Bot

LINE Bot Webhook 服務，部署在 Hugging Face Space。當使用者在 LINE 傳送 `/aivi` 指令時，自動爬取 [AIVI 科技博客](https://blog.aivislab.com/)最新 5 則文章並回傳。

## 功能

- 📰 **即時爬取**：爬取 AIVI 科技博客最新 5 則文章
- 🤖 **LINE Bot 整合**：透過 LINE Messaging API 回傳結果
- ⚡️ **快速回應**：< 10 秒內完成爬取與回覆
- 🛡️ **錯誤處理**：完整的錯誤處理與友善錯誤訊息

## 環境變數設定

請在 Hugging Face Space Settings 中設定以下環境變數：

| 變數名稱 | 說明 | 必填 |
|---------|------|------|
| `LINE_CHANNEL_SECRET` | LINE Channel Secret | ✅ |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Channel Access Token | ✅ |
| `PORT` | 服務 port（預設 7860） | ❌ |

### 如何取得 LINE Credentials

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 建立新的 Provider（如果還沒有）
3. 建立新的 Messaging API Channel
4. 在 Channel 設定頁面取得：
   - **Channel Secret**（基本設定頁面）
   - **Channel Access Token**（Messaging API 頁面，需要先發行 Long-lived token）

## Webhook URL

部署完成後，Webhook URL 為：

```
https://josephchou-aivi-linebot.hf.space/webhook
```

請將此 URL 設定到 LINE Developers Console 的 Webhook URL 欄位。

### 設定步驟

1. 進入 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇您的 Messaging API Channel
3. 前往「Messaging API」頁面
4. 找到「Webhook settings」區塊
5. 點擊「Edit」，輸入：`https://josephchou-aivi-linebot.hf.space/webhook`
6. 啟用「Use webhook」開關
7. 點擊「Verify」按鈕，確認 webhook 可正常運作

## 技術架構

- **語言**：Python 3.10
- **Web 框架**：Flask（webhook 服務）
- **LINE Bot SDK**：line-bot-sdk 3.x
- **HTTP Client**：httpx（非同步請求）
- **HTML 解析**：selectolax（高效能 HTML parser）
- **套件管理**：uv
- **部署**：Docker（Hugging Face Space）

## 使用方式

1. 在 LINE 中加入您的 Bot 為好友
2. 傳送 `/aivi` 指令（不區分大小寫）
3. Bot 會回傳 AIVI 科技博客最新 5 則文章的標題和連結

## 原始碼

完整原始碼與開發文件：[https://github.com/btisland/aivi-linebot](https://github.com/btisland/aivi-linebot)

## 技術亮點

### 輕量化設計
- 使用 `selectolax` 而非 `BeautifulSoup`（快 5-10 倍）
- Docker image 大小 < 500MB
- 記憶體使用 < 256MB

### 高效能
- 非同步爬蟲（httpx）
- 完整的 timeout 與錯誤處理
- 回應時間 < 3 秒（符合 LINE webhook 要求）

### 可維護性
- 測試覆蓋率 > 80%
- 完整的型別註解（type hints）
- 清楚的模組化架構

## 部署資訊

- **Platform**: Hugging Face Space
- **SDK**: Docker
- **Space Type**: Persistent（持續運行）
- **Hardware**: CPU Basic（免費）

## 自動部署

本專案使用 GitHub Actions 自動同步：

1. 推送到 GitHub `main` 分支
2. GitHub Actions 觸發自動同步
3. Hugging Face Space 自動重新建置並部署

## 授權

MIT License

## 相關連結

- [GitHub Repository](https://github.com/btisland/aivi-linebot)
- [LINE Developers Console](https://developers.line.biz/console/)
- [AIVI 科技博客](https://blog.aivislab.com/)

---

**Last Updated**: 2025-12-09
**Maintained by**: [btisland](https://github.com/btisland)

<!-- Test sync: 2025-12-11 07:39:23 UTC -->
