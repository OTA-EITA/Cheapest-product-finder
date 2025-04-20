# ベースイメージの選択
FROM python:3.11-slim-bullseye

# 作業ディレクトリの設定
WORKDIR /app

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    postgresql-client \
    netcat-openbsd \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をコピー
COPY requirements.txt .

# 依存関係のインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# 環境変数の設定
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ポートの公開
EXPOSE 8000

# エントリーポイントの設定
CMD ["sh", "-c", "while ! nc -z postgres 5432; do sleep 1; done && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
