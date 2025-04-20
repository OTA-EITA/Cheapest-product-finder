#!/bin/bash
set -e

# スクリプトの開始をログに出力
echo "Starting Flutter Web App in development mode"

# Flutterパッケージの更新
cd /app
echo "Running flutter pub get..."
flutter pub get

# デバッグ情報の表示
echo "Flutter version:"
flutter --version

# assetsディレクトリの確認
echo "Checking assets directories..."
mkdir -p /app/assets/images
mkdir -p /app/assets/icons

# ダミーアセットの作成（必要な場合）
if [ ! -f /app/assets/icons/placeholder.svg ]; then
  echo "Creating placeholder assets..."
  echo '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#2196F3"/></svg>' > /app/assets/icons/placeholder.svg
  echo '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100" height="100" fill="#E0E0E0"/><text x="50" y="50" font-family="Arial" font-size="12" text-anchor="middle" alignment-baseline="middle" fill="#757575">Image</text></svg>' > /app/assets/images/placeholder.svg
fi

# ウェブアプリの開発モードで実行
echo "Starting Flutter web server in development mode..."
cd /app
flutter run -d web-server --web-port=8080 --web-hostname=0.0.0.0
