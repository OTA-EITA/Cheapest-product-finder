from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from .models import Base, engine
from .routers import search_router, products_router, alerts_router, users_router

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# データベースの初期化（開発環境）
Base.metadata.create_all(bind=engine)

# アプリケーションの作成
app = FastAPI(
    title="最安値検索アプリ API",
    description="複数の通販サイトから商品の最安値を検索するAPIサービス",
    version="0.1.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(search_router)
app.include_router(products_router)
app.include_router(alerts_router)
app.include_router(users_router)

@app.get("/")
async def root():
    """
    APIのルートエンドポイント
    """
    return {
        "message": "最安値検索アプリAPIへようこそ",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
