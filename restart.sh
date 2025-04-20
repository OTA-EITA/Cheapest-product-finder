#!/bin/bash

# Docker コンテナを停止
docker-compose down

# Docker コンテナを起動
docker-compose up -d

echo "アプリケーションを再起動しました。"
echo "- バックエンド: http://localhost:8000"
echo "- フロントエンド: http://localhost:8080"
