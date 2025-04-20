from celery import shared_task
import logging
from sqlalchemy.orm import sessionmaker
from ..models.database import engine
from ..models.models import Product, Price
from ...scraping import AmazonScraper, RakutenScraper, YahooShoppingScraper
import time
from datetime import datetime

# ロガーの設定
logger = logging.getLogger(__name__)

# データベースセッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# スクレイパーのインスタンスを作成
amazon_scraper = AmazonScraper()
rakuten_scraper = RakutenScraper()
yahoo_scraper = YahooShoppingScraper()

@shared_task(name="app.tasks.price_update.update_all_prices")
def update_all_prices():
    """全商品の価格を更新するタスク"""
    logger.info("Starting price update for all products...")
    
    # データベースセッションの作成
    db = SessionLocal()
    
    try:
        # 全商品を取得
        products = db.query(Product).all()
        logger.info(f"Found {len(products)} products to update")
        
        update_count = 0
        error_count = 0
        
        for product in products:
            try:
                # 商品のソースに基づいて適切なスクレイパーを選択
                if product.source == 'Amazon':
                    scraper = amazon_scraper
                elif product.source == '楽天市場':
                    scraper = rakuten_scraper
                elif product.source == 'Yahoo!ショッピング':
                    scraper = yahoo_scraper
                else:
                    logger.warning(f"Unknown source for product {product.id}: {product.source}")
                    continue
                
                # URLからページを取得
                soup = scraper.get_page(product.url)
                if not soup:
                    logger.error(f"Failed to fetch page for product {product.id}: {product.url}")
                    error_count += 1
                    continue
                
                # 商品情報の抽出方法はソースによって異なる
                # ここでは簡単なサンプルとして、直接product_infoを作成
                # 実際には、各スクレイパークラスのメソッドを追加する必要がある
                
                # 商品ページから詳細情報を抽出
                try:
                    if product.source == 'Amazon':
                        price_elem = soup.select_one('.a-price .a-offscreen')
                        price_text = price_elem.text.strip() if price_elem else None
                        price = float(price_text.replace('￥', '').replace(',', '')) if price_text else None
                        
                        shipping_elem = soup.select_one('#deliveryBlockMessage')
                        shipping_text = shipping_elem.text.strip() if shipping_elem else None
                        # 「無料配送」などのテキストから送料を解析
                        shipping_fee = 0 if shipping_text and '無料' in shipping_text else None
                    
                    elif product.source == '楽天市場':
                        price_elem = soup.select_one('.price')
                        price_text = price_elem.text.strip() if price_elem else None
                        price = float(price_text.replace('円', '').replace(',', '')) if price_text else None
                        
                        shipping_elem = soup.select_one('.shipping')
                        shipping_text = shipping_elem.text.strip() if shipping_elem else None
                        # 送料テキストから送料を解析
                        shipping_fee = 0 if shipping_text and '無料' in shipping_text else None
                    
                    elif product.source == 'Yahoo!ショッピング':
                        price_elem = soup.select_one('.elPriceNumber')
                        price_text = price_elem.text.strip() if price_elem else None
                        price = float(price_text.replace('円', '').replace(',', '')) if price_text else None
                        
                        shipping_elem = soup.select_one('.elShippingOptions')
                        shipping_text = shipping_elem.text.strip() if shipping_elem else None
                        # 送料テキストから送料を解析
                        shipping_fee = 0 if shipping_text and '無料' in shipping_text else None
                    
                    else:
                        logger.warning(f"No parsing logic for source: {product.source}")
                        continue
                    
                    # 価格情報が取得できなかった場合はスキップ
                    if price is None:
                        logger.warning(f"Could not extract price for product {product.id}: {product.url}")
                        continue
                    
                    # 総額の計算（送料が不明な場合は価格のみ）
                    total_price = price
                    if shipping_fee is not None:
                        total_price += shipping_fee
                    
                    # 新しい価格情報をデータベースに保存
                    new_price = Price(
                        product_id=product.id,
                        price=price,
                        shipping_fee=shipping_fee,
                        total_price=total_price,
                        timestamp=datetime.utcnow()
                    )
                    
                    db.add(new_price)
                    db.commit()
                    update_count += 1
                    
                    logger.info(f"Updated price for product {product.id}: {price} JPY (Total: {total_price} JPY)")
                    
                    # 負荷軽減のための短い待機
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error extracting price info for product {product.id}: {str(e)}")
                    error_count += 1
                    continue
                
            except Exception as e:
                logger.error(f"Error updating product {product.id}: {str(e)}")
                error_count += 1
                continue
        
        logger.info(f"Price update completed. Updated: {update_count}, Errors: {error_count}")
        
        return {
            "success": True,
            "updated_count": update_count,
            "error_count": error_count,
            "total_products": len(products)
        }
    
    except Exception as e:
        logger.error(f"Error in update_all_prices task: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()

@shared_task(name="app.tasks.price_update.update_product_price")
def update_product_price(product_id):
    """特定の商品の価格を更新するタスク"""
    logger.info(f"Starting price update for product {product_id}...")
    
    # データベースセッションの作成
    db = SessionLocal()
    
    try:
        # 商品を取得
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            logger.error(f"Product not found: {product_id}")
            return {"success": False, "error": "Product not found"}
        
        # ソースに基づいてスクレイパーを選択
        if product.source == 'Amazon':
            scraper = amazon_scraper
        elif product.source == '楽天市場':
            scraper = rakuten_scraper
        elif product.source == 'Yahoo!ショッピング':
            scraper = yahoo_scraper
        else:
            logger.warning(f"Unknown source for product {product.id}: {product.source}")
            return {"success": False, "error": "Unknown product source"}
        
        # 商品URLからページを取得
        soup = scraper.get_page(product.url)
        if not soup:
            logger.error(f"Failed to fetch page for product {product.id}: {product.url}")
            return {"success": False, "error": "Failed to fetch product page"}
        
        # 商品の価格情報を抽出（ソースに応じた処理）
        # 実際の実装では、各スクレイパークラスに専用のメソッドを追加するべき
        # この例では簡略化のため直接処理
        try:
            price = None
            shipping_fee = None
            
            if product.source == 'Amazon':
                price_elem = soup.select_one('.a-price .a-offscreen')
                price_text = price_elem.text.strip() if price_elem else None
                price = float(price_text.replace('￥', '').replace(',', '')) if price_text else None
                
                shipping_elem = soup.select_one('#deliveryBlockMessage')
                shipping_text = shipping_elem.text.strip() if shipping_elem else None
                shipping_fee = 0 if shipping_text and '無料' in shipping_text else None
            
            elif product.source == '楽天市場':
                price_elem = soup.select_one('.price')
                price_text = price_elem.text.strip() if price_elem else None
                price = float(price_text.replace('円', '').replace(',', '')) if price_text else None
                
                shipping_elem = soup.select_one('.shipping')
                shipping_text = shipping_elem.text.strip() if shipping_elem else None
                shipping_fee = 0 if shipping_text and '無料' in shipping_text else None
            
            elif product.source == 'Yahoo!ショッピング':
                price_elem = soup.select_one('.elPriceNumber')
                price_text = price_elem.text.strip() if price_elem else None
                price = float(price_text.replace('円', '').replace(',', '')) if price_text else None
                
                shipping_elem = soup.select_one('.elShippingOptions')
                shipping_text = shipping_elem.text.strip() if shipping_elem else None
                shipping_fee = 0 if shipping_text and '無料' in shipping_text else None
            
            # 価格情報が取得できなかった場合はエラー
            if price is None:
                logger.warning(f"Could not extract price for product {product.id}: {product.url}")
                return {"success": False, "error": "Could not extract price"}
            
            # 総額の計算
            total_price = price
            if shipping_fee is not None:
                total_price += shipping_fee
            
            # 新しい価格情報をデータベースに保存
            new_price = Price(
                product_id=product.id,
                price=price,
                shipping_fee=shipping_fee,
                total_price=total_price,
                timestamp=datetime.utcnow()
            )
            
            db.add(new_price)
            db.commit()
            
            logger.info(f"Updated price for product {product.id}: {price} JPY (Total: {total_price} JPY)")
            
            return {
                "success": True,
                "product_id": product.id,
                "price": price,
                "shipping_fee": shipping_fee,
                "total_price": total_price
            }
            
        except Exception as e:
            logger.error(f"Error extracting price info for product {product.id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    except Exception as e:
        logger.error(f"Error in update_product_price task: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()
