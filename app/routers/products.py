from fastapi import APIRouter, Depends, HTTPException, Path, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import statistics
from ..models import get_db, Product, Price, Favorite, User
from ..schemas import ProductResponse, PriceHistoryResponse, FavoriteCreate, FavoriteResponse, PriceAnalysisResponse
from ...scraping import ScraperManager

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
    refresh: bool = Query(False, description="価格を再取得するかどうか"),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    特定の商品の価格履歴を取得
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品が見つかりませんでした")
    
    # 当日のデータがない場合、あるいは強制リフレッシュが指定された場合、バックグラウンドで価格を更新
    today = datetime.now().date()
    latest_price = db.query(Price).filter(
        Price.product_id == product_id,
        func.date(Price.timestamp) == today
    ).first()
    
    if refresh or not latest_price:
        background_tasks.add_task(
            update_product_prices, 
            product_id=product_id, 
            db=db
        )
    
    from_date = datetime.utcnow() - timedelta(days=days)
    prices = db.query(Price).filter(
        Price.product_id == product_id,
        Price.timestamp >= from_date
    ).order_by(Price.timestamp).all()
    
    return PriceHistoryResponse(product=product, prices=prices)

@router.get("/price-analysis/{product_id}", response_model=PriceAnalysisResponse)
async def analyze_price(  
    product_id: int = Path(..., description="商品ID"),
    days: int = Query(90, description="分析する価格履歴の日数"),
    db: Session = Depends(get_db)
):
    """
    特定の商品の価格分析を行う
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品が見つかりませんでした")
    
    # 指定された日数分の価格履歴を取得
    from_date = datetime.utcnow() - timedelta(days=days)
    prices = db.query(Price).filter(
        Price.product_id == product_id,
        Price.timestamp >= from_date
    ).order_by(Price.timestamp).all()
    
    if not prices:
        raise HTTPException(status_code=404, detail="価格履歴が見つかりませんでした")
    
    # 価格データの分析
    price_values = [p.price for p in prices]
    min_price = min(price_values)
    max_price = max(price_values)
    avg_price = sum(price_values) / len(price_values)
    median_price = statistics.median(price_values)
    
    # 価格変動率の計算
    price_fluctuation = (max_price - min_price) / avg_price * 100
    
    # 価格トレンドの分析
    first_prices = price_values[:len(price_values)//3]  # 最初の1/3
    last_prices = price_values[-len(price_values)//3:]  # 最後の1/3
    
    first_avg = sum(first_prices) / len(first_prices)
    last_avg = sum(last_prices) / len(last_prices)
    
    if last_avg < first_avg * 0.95:  # 5%以上下落
        price_trend = "下落傾向"
    elif last_avg > first_avg * 1.05:  # 5%以上上昇
        price_trend = "上昇傾向"
    else:
        price_trend = "横這い"
    
    # 購入タイミングの推奨
    if price_trend == "下落傾向":
        best_time_to_buy = "下落傾向が続いているため、あと1-2週間待つのがお得です"
    elif price_trend == "上昇傾向":
        best_time_to_buy = "価格が上昇傾向のため、今が購入タイミングかもしれません"
    else:
        current_price = price_values[-1]
        if current_price < avg_price * 0.95:
            best_time_to_buy = "現在価格が平均よりも安いため、購入に適したタイミングです"
        else:
            best_time_to_buy = "価格が横這いため、大きな変動は期待できません"
    
    return PriceAnalysisResponse(
        min_price=min_price,
        max_price=max_price,
        avg_price=avg_price,
        median_price=median_price,
        price_trend=price_trend,
        best_time_to_buy=best_time_to_buy,
        price_fluctuation=price_fluctuation,
        price_history_days=days,
        product=product
    )

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

# バックグラウンドで実行される価格更新関数
async def update_product_prices(product_id: int, db: Session):
    """商品の最新価格をスクレイピングして取得し、データベースを更新する"""
    logger.info(f"Updating prices for product ID: {product_id}")
    
    try:
        # 商品情報の取得
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            logger.error(f"Product not found: {product_id}")
            return
        
        # スクレイパーを使って最新価格を取得
        scraper_manager = ScraperManager()
        source_site = product.source
        
        # 商品のURLからドメインを判定して適切なスクレイパーを選択
        site_key = None
        if 'amazon' in product.url.lower():
            site_key = 'amazon'
        elif 'rakuten' in product.url.lower():
            site_key = 'rakuten'
        elif 'yahoo' in product.url.lower():
            site_key = 'yahoo'
        
        if not site_key:
            logger.error(f"Unknown site for URL: {product.url}")
            return
        
        # 商品名で検索して価格を取得
        results = scraper_manager.search_site(
            site_key, 
            product.name, 
            max_results=5,
            include_shipping=True
        )
        
        # URLが一致する商品を探す
        matching_product = None
        for result in results:
            if product.url in result.get('url', ''):
                matching_product = result
                break
        
        # 一致する商品が見つからなかった場合は最初の結果を使用
        if not matching_product and results:
            matching_product = results[0]
        
        if matching_product and 'price' in matching_product:
            # 価格情報を保存
            shipping_fee = 0
            if 'shipping' in matching_product and matching_product['shipping']:
                # 送料情報があれば数値に変換（もしあれば）
                shipping_text = matching_product['shipping']
                if isinstance(shipping_text, str) and '円' in shipping_text:
                    try:
                        shipping_fee = float(shipping_text.replace('円', '').replace(',', '').strip())
                    except ValueError:
                        shipping_fee = 0
                
            new_price = Price(
                product_id=product_id,
                price=matching_product['price'],
                shipping_fee=shipping_fee,
                total_price=matching_product['price'] + shipping_fee,
                currency="JPY",
                timestamp=datetime.utcnow()
            )
            db.add(new_price)
            db.commit()
            logger.info(f"Updated price for product ID {product_id}: {matching_product['price']}")
        else:
            logger.warning(f"No matching product or price found for product ID: {product_id}")
    
    except Exception as e:
        logger.error(f"Error updating prices for product ID {product_id}: {str(e)}")
        db.rollback()
