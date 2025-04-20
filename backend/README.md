# 最安値検索アプリ - バックエンド

## Python環境

### 推奨環境
- Python 3.11
- 推奨: Python 3.11.4以降

### システム要件
- Python 3.11
- pip
- venv
- git

### セットアップ手順

1. Pythonのインストール
```bash
# deadsnakesリポジトリの追加
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update

# Python 3.11のインストール
sudo apt-get install python3.11 python3.11-venv python3.11-dev
```

2. プロジェクトセットアップ
```bash
# セットアップスクリプトの実行
chmod +x python_setup.sh
./python_setup.sh

# 仮想環境のアクティベート
source .venv_3.11/bin/activate

# Noxによるテスト実行
nox -s tests
```

### 開発ツール
- Nox: テスト自動化
- Pytest: ユニットテスト
- Black: コードフォーマット
- Flake8: 静的解析
- Mypy: 型チェック

### Docker利用
```bash
# イメージのビルド
docker build -t cheapest-price-finder .

# コンテナの実行
docker run -p 8000:8000 cheapest-price-finder
```

### 注意事項
- 仮想環境を必ず使用してください
- 依存関係は`requirements.txt`で管理されています
