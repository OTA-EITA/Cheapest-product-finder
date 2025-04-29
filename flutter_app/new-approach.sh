#!/bin/bash
# 新しいアプローチでFlutterウェブアプリを構築する

# 作業ディレクトリに移動
cd ~/src/cheapest-price-finder/

# コンテナを停止
echo "Stopping existing containers..."
docker-compose down flutter_app

# Dockerfileを元のシンプルな形に戻す
cat > ~/src/cheapest-price-finder/flutter_app/Dockerfile << 'EOF'
FROM ubuntu:22.04

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    openjdk-11-jdk \
    wget \
    python3 \
    python3-pip

# Flutter SDKのダウンロードと設定
RUN git clone https://github.com/flutter/flutter.git /flutter
ENV PATH="/flutter/bin:${PATH}"
RUN flutter channel stable
RUN flutter upgrade
RUN flutter config --enable-web

# 作業ディレクトリの設定
WORKDIR /app

# バインディングを確実にする
CMD ["flutter", "run", "-d", "web-server", "--web-port=8080", "--web-hostname=0.0.0.0"]
EOF

# docker-compose.ymlを修正
cat > ~/src/cheapest-price-finder/docker-compose.yml << 'EOF'
services:
  flutter_app:
    build:
      context: ./flutter_app
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    volumes:
      - ./flutter_app:/app
    environment:
      - DISPLAY=${DISPLAY}
    restart: unless-stopped
    profiles: ["frontend", "all"]

volumes:
  flutter_cache:
EOF

# index.htmlを標準的な形に戻す
mkdir -p ~/src/cheapest-price-finder/flutter_app/web
cat > ~/src/cheapest-price-finder/flutter_app/web/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <base href="$FLUTTER_BASE_HREF">

  <meta charset="UTF-8">
  <meta content="IE=Edge" http-equiv="X-UA-Compatible">
  <meta name="description" content="最安値検索アプリ">

  <!-- iOS meta tags & icons -->
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black">
  <meta name="apple-mobile-web-app-title" content="最安値検索アプリ">
  <link rel="apple-touch-icon" href="icons/Icon-192.png">

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="favicon.png"/>

  <title>最安値検索アプリ</title>
  <link rel="manifest" href="manifest.json">

  <script>
    // The value below is injected by flutter build, do not touch.
    var serviceWorkerVersion = null;
  </script>
  <!-- This script adds the flutter initialization JS code -->
  <script src="flutter.js" defer></script>
</head>
<body>
  <script>
    window.addEventListener('load', function(ev) {
      // Download main.dart.js
      _flutter.loader.loadEntrypoint({
        serviceWorker: {
          serviceWorkerVersion: serviceWorkerVersion,
        },
        onEntrypointLoaded: function(engineInitializer) {
          engineInitializer.initializeEngine().then(function(appRunner) {
            appRunner.runApp();
          });
        }
      });
    });
  </script>
</body>
</html>
EOF

# コンテナを再ビルド
echo "Rebuilding the container..."
docker-compose build --no-cache flutter_app

# コンテナを起動
echo "Starting the container..."
docker-compose up -d flutter_app

echo "Flutter app container has been rebuilt with a simpler approach"
echo "Please wait a few moments for the web server to start"
echo "Then access the app at http://localhost:8080"
echo "Check logs with: docker-compose logs -f flutter_app"
