#!/bin/bash
# コンテナを再起動するスクリプト

cd ~/src/cheapest-price-finder/

# コンテナを停止
docker-compose down flutter_app

# コンテナを再起動
docker-compose up -d flutter_app

echo "Flutter app container has been restarted"
echo "Please wait a few moments for the web server to start"
echo "Then access the app at http://localhost:8080"
echo "Check logs with: docker-compose logs -f flutter_app"
