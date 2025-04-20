from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# DB依存関係
from database.base import get_db

# 検索エンドポイント
from services.product_service import ProductSearchService
search_router = APIRouter(prefix="/search", tags=["検索"])

@search_router.get("/")
def search_products(
    query: str, 
    min_price: float = None, 
    max_price: float = None, 
    categories: str = None,
    db: Session = Depends(get_db)
):
    """
    商品検索エンドポイント
    """
    # カテゴリーの文字列を処理
    # URLエンコードされた文字列をデコード
    category = categories
    
    return ProductSearchService.search_products(
        db,
        query, 
        min_price, 
        max_price, 
        category
    )

# 価格履歴エンドポイント
price_history_router = APIRouter(prefix="/price-history", tags=["価格履歴"])

@price_history_router.get("/{product_id}")
def get_price_history(product_id: str, db: Session = Depends(get_db)):
    """
    商品の価格履歴取得エンドポイント
    """
    return ProductSearchService.get_price_history(db, product_id)

# 価格アラートエンドポイント
from .price_alerts import router as price_alerts_router

# レコメンデーションエンドポイント
recommendations_router = APIRouter(prefix="/recommendations", tags=["レコメンデーション"])

@recommendations_router.get("/")
def get_recommendations(db: Session = Depends(get_db)):
    """
    パーソナライズされた商品推奨エンドポイント
    """
    from services.product_service import ProductRecommendationService
    return ProductRecommendationService.get_personalized_recommendations(db, 'user1')
