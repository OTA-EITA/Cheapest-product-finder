#!/bin/bash
# デベロップメントモードに切り替えるスクリプト

# docker-entrypoint-dev.shに実行権限を付与
chmod +x ~/src/cheapest-price-finder/flutter_app/docker-entrypoint-dev.sh
echo "Permissions set for docker-entrypoint-dev.sh"

# docker-compose.ymlを修正
cd ~/src/cheapest-price-finder/

# コンテナを停止
docker-compose down flutter_app

# docker-entrypoint.shを開発用に置き換え
cp ~/src/cheapest-price-finder/flutter_app/docker-entrypoint-dev.sh ~/src/cheapest-price-finder/flutter_app/docker-entrypoint.sh
chmod +x ~/src/cheapest-price-finder/flutter_app/docker-entrypoint.sh

# コンテナを再ビルド
docker-compose build --no-cache flutter_app

# コンテナを起動
docker-compose up -d flutter_app

echo "Flutter app container has been rebuilt and restarted in development mode"
echo "Please wait a few moments for the development server to start"
echo "Then access the app at http://localhost:8080"
echo "Check logs with: docker-compose logs -f flutter_app"
