# Hugging Face Space 部署用 Dockerfile
# 基於 Python 3.10 slim 映像檔

FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統相依套件
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安裝 uv（Python 套件管理工具）
RUN pip install --no-cache-dir uv

# 複製專案檔案
COPY pyproject.toml uv.lock ./
COPY src ./src

# 安裝相依套件（使用 uv.lock 確保版本一致）
RUN uv sync --frozen

# 設定環境變數
# PORT: Hugging Face Space 的標準 port
ENV PORT=7860

# 暴露 port（供 Hugging Face Space 使用）
EXPOSE 7860

# 健康檢查（確保服務正常運行）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# 啟動 Flask 服務
# 使用 uv run 確保在正確的虛擬環境中執行
CMD ["uv", "run", "python", "src/app.py"]
