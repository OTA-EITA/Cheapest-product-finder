#!/bin/bash
# 全ての修正を実行するスクリプト

# docker-entrypoint.shに実行権限を付与
chmod +x ~/src/cheapest-price-finder/flutter_app/docker-entrypoint.sh
echo "Permissions set for docker-entrypoint.sh"

# コンテナの再起動
cd ~/src/cheapest-price-finder/
docker-compose down flutter_app
docker-compose build flutter_app
docker-compose up -d flutter_app

echo "Flutter app container has been rebuilt and restarted"
echo "Please wait a few moments for the build process to complete"
echo "Then access the app at http://localhost:8080"
