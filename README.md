# 最安値検索アプリ

複数の通販サイトから商品の最安値を簡単に比較できるアプリケーション。

## プロジェクト概要

このアプリケーションは、ユーザーが欲しい商品の最安値を複数の通販サイト（Amazon, 楽天市場, Yahoo!ショッピングなど）から簡単に比較できる機能を提供します。価格履歴トラッキングや価格アラート機能なども備えており、最小の手間で最大の節約を実現することを目的としています。

## 機能

- 商品名での検索機能
- 複数の通販サイトでの価格比較
- 送料込みの総額表示
- 価格の安い順でのソート
- バーコードスキャン検索
- 価格履歴のトラッキング
- 価格アラート設定
- お気に入り商品の登録
- 検索履歴の保存

## 技術スタック

### フロントエンド
- Flutter (予定)
- Dart
- Provider / Riverpod

### バックエンド
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- BeautifulSoup (スクレイピング)
- Celery (非同期タスク)

### データベース
- Azure Cosmos DB (本番環境)
- SQLite (開発環境)
- Redis (キャッシュ)

### インフラ
- Microsoft Azure
- Docker
- Kubernetes (AKS)

## セットアップ

### 環境構築

1. リポジトリをクローン
```bash
git clone https://github.com/your-username/cheapest-price-finder.git
cd cheapest-price-finder
```

2. 仮想環境を作成して有効化
```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

3. 依存関係をインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定（.envファイルを作成）
```
DATABASE_URL=sqlite:///./cheapest_price_finder.db
```

### 実行方法

```bash
cd src/cheapest-price-finder
python -m app.main
```

アプリケーションは http://localhost:8000 で実行されます。
APIドキュメントは http://localhost:8000/docs で確認できます。

## API エンドポイント

- `/search` - 商品検索
- `/products` - 商品情報
- `/products/price-history/{product_id}` - 商品の価格履歴
- `/products/favorites` - お気に入り管理
- `/alerts` - 価格アラート管理
- `/users` - ユーザー管理

## 開発状況

- [x] スクレイピング基盤実装
- [x] バックエンドAPI実装
- [ ] データベースモデル実装
- [ ] フロントエンド実装
- [ ] デプロイ設定

## 貢献方法

1. このリポジトリをフォークする
2. 新しいブランチを作成する（`git checkout -b feature/amazing-feature`）
3. 変更をコミットする（`git commit -m 'Add some amazing feature'`）
4. ブランチにプッシュする（`git push origin feature/amazing-feature`）
5. Pull Requestを作成する

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
