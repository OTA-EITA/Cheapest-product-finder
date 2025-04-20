# 最安値検索アプリ

複数の通販サイトから商品の最安値を簡単に比較できるFlutterアプリケーション

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

## 起動方法

### Dockerを使用して起動

```bash
# リポジトリのルートディレクトリで実行
docker compose up flutter_app --build
```

ブラウザで `http://localhost:8080` にアクセスしてアプリを確認できます。

### ローカルで開発する場合

1. Flutterをインストールしてください（[Flutter公式サイト](https://flutter.dev/docs/get-started/install)）

2. 依存関係をインストール
```bash
cd flutter_app
flutter pub get
```

3. アプリを実行
```bash
# Webで実行
flutter run -d chrome

# または
flutter run -d web-server --web-port=8080 --web-hostname=0.0.0.0
```

## プロジェクト構造

```
lib/
├── main.dart           # アプリのエントリーポイント
├── models/             # データモデル
├── screens/            # 画面
├── services/           # APIやデータサービス
├── utils/              # ユーティリティ関数やテーマ設定
└── widgets/            # 再利用可能なウィジェット
```

## 開発ロードマップ

- [x] 基本UI実装
- [x] 検索機能
- [x] 最安値比較表示
- [x] お気に入り機能
- [x] 価格履歴表示
- [ ] バックエンドAPI連携
- [ ] バーコードスキャン機能完成
- [ ] 価格予測機能
- [ ] AI機能の実装
