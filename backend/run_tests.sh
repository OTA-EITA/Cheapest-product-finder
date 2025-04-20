#!/bin/bash

# 仮想環境を作成・有効化
python3 -m venv .venv
source .venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt

# テストを実行
pytest tests/

# 仮想環境を終了
deactivate
