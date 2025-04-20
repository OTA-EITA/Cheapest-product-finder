from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from ..models import get_db, Product, Price, Favorite, User
from ..schemas import ProductResponse, PriceHistoryResponse, FavoriteCreate, FavoriteResponse

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

# ロガーの設定
logger = logging.getLogger(__name__)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int = Path(..., description="商品ID"),
    db: Session = Depends(get_db)
):
    """
    特定の商品情報を取得
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品が見つかりませんでした")
    return product

@router.get("/price-history/{product_id}", response_model=PriceHistoryResponse)
async def get_price_history(
    product_id: int = Path(..., description="商品ID"),
    days: int = Query(30, description="取得する履歴の日数"),
    db: Session = Depends(get_db)
):
    """
    特定の商品の価格履歴を取得
    """
    from datetime import datetime, timedelta
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品が見つかりませんでした")
    
    # 指定された日数分の価格履歴を取得
    from_date = datetime.utcnow() - timedelta(days=days)
    prices = db.query(Price).filter(
        Price.product_id == product_id,
        Price.timestamp >= from_date
    ).order_by(Price.timestamp).all()
    
    return PriceHistoryResponse(product=product, prices=prices)

@router.post("/favorites", response_model=FavoriteResponse)
async def add_favorite(
    favorite: FavoriteCreate,
    user_id: int = Query(..., description="ユーザーID"),
    db: Session = Depends(get_db)
):
    """
    お気に入りに商品を追加
    """
    # ユーザーと商品の存在チェック
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりませんでした")
    
    product = db.query(Product).filter(Product.id == favorite.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品が見つかりませんでした")
    
    # すでにお気に入りに追加されているかチェック
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.product_id == favorite.product_id
    ).first()
    
    if existing_favorite:
        return existing_favorite
    
    # 新しいお気に入りを作成
    db_favorite = Favorite(
        user_id=user_id,
        product_id=favorite.product_id
    )
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    
    return db_favorite

@router.get("/favorites", response_model=List[FavoriteResponse])
async def get_favorites(
    user_id: int = Query(..., description="ユーザーID"),
    db: Session = Depends(get_db)
):
    """
    ユーザーのお気に入り商品一覧を取得
    """
    favorites = db.query(Favorite).filter(Favorite.user_id == user_id).all()
    return favorites

@router.delete("/favorites/{favorite_id}")
async def remove_favorite(
    favorite_id: int = Path(..., description="お気に入りID"),
    user_id: int = Query(..., description="ユーザーID"),
    db: Session = Depends(get_db)
):
    """
    お気に入りから商品を削除
    """
    favorite = db.query(Favorite).filter(
        Favorite.id == favorite_id,
        Favorite.user_id == user_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="指定されたお気に入りが見つかりませんでした")
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "お気に入りから削除されました", "favorite_id": favorite_id}
