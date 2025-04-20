#!/bin/bash
set -e

# スクリプトの開始をログに出力
echo "Starting Flutter Web App Setup"

# Flutterパッケージの更新
cd /app
echo "Running flutter pub get..."
flutter pub get

# デバッグ情報の表示
echo "Flutter version:"
flutter --version
echo "Pub packages:"
flutter pub deps

# assetsディレクトリの確認
echo "Checking assets directories..."
mkdir -p /app/assets/images
mkdir -p /app/assets/icons

# ダミーアセットの作成
echo "Creating placeholder assets..."
echo '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#2196F3"/></svg>' > /app/assets/icons/placeholder.svg
echo '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100" height="100" fill="#E0E0E0"/><text x="50" y="50" font-family="Arial" font-size="12" text-anchor="middle" alignment-baseline="middle" fill="#757575">Image</text></svg>' > /app/assets/images/placeholder.svg

# webアプリをビルド
echo "Building Flutter web app..."
flutter build web --release

# index.htmlが正しく生成されたか確認
echo "Verifying build output..."
if [ ! -f /app/build/web/index.html ]; then
  echo "ERROR: index.html not found in build output!"
  echo "Build directory contents:"
  ls -la /app/build/web/
  exit 1
fi

# 実行ディレクトリ内のwebコンテンツを配信
echo "Starting web server on port 8080..."
cd /app/build/web
python3 -m http.server 8080 --bind 0.0.0.0
