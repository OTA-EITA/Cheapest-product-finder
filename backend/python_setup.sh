#!/bin/bash

# Python 3.11のインストール
install_python() {
    echo "Python 3.11のインストールを開始..."
    
    # 必要な依存関係のインストール
    sudo apt-get update
    sudo apt-get install -y software-properties-common

    # deadsnakesリポジトリの追加
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update

    # Python 3.11のインストール
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
    
    # システムのデフォルトPythonを変更しない
    
    # バージョン確認
    python3.11 --version
}

# 仮想環境の作成と依存関係のインストール
setup_virtual_env() {
    echo "仮想環境の作成と依存関係のインストール..."
    
    # 3.11用の仮想環境作成
    python3.11 -m venv .venv_3.11
    source .venv_3.11/bin/activate

    # 最新のpipとsetuptoolsにアップグレード
    pip install --upgrade pip setuptools wheel

    # 依存関係のインストール
    pip install -r requirements.txt

    # Noxのインストール
    pip install nox

    deactivate
}

# メイン実行
main() {
    install_python
    setup_virtual_env
}

main
