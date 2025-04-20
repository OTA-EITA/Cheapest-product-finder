from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# スキーマとエンドポイントのインポート
from api.endpoints import (
    search_router, 
    price_history_router, 
    price_alerts_router, 
    recommendations_router
)

# コンフィグとDB初期化
from core.config import settings
from database.base import engine, Base, get_db
from sqlalchemy.orm import Session

# 初期データ投入用
from services.product_service import initialize_test_data

# アプリケーションの初期化
app = FastAPI(
    title="最安値検索アプリ",
    description="複数の通販サイトから最安値の商品を検索するAPI",
    version="1.0.0"
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では具体的なオリジンに制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの追加
app.include_router(search_router)
app.include_router(price_history_router)
app.include_router(price_alerts_router)
app.include_router(recommendations_router)

# データベーステーブルの作成
@app.on_event("startup")
def startup():
    # テーブルの作成
    Base.metadata.create_all(bind=engine)
    
    # テスト用データの初期化
    db = next(get_db())
    initialize_test_data(db)

# ヘルスチェックエンドポイント
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
