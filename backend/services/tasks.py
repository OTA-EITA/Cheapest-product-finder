from celery import Celery
from scraping.scrapers import scrape_products
from typing import List, Dict
import redis
import json

# Celeryアプリケーションの初期化
app = Celery('cheapest_price_finder', 
             broker='redis://redis:6379/0', 
             backend='redis://redis:6379/0')

# Redisクライアントの初期化
redis_client = redis.Redis(host='redis', port=6379, db=1)

@app.task(name='scrape_and_cache_products')
def scrape_and_cache_products(query: str) -> List[Dict]:
    """
    商品を検索しスクレイピングした結果をRedisにキャッシュ
    """
    try:
        # スクレイピングを実行
        results = scrape_products(query)
        
        # 結果をキャッシュ (30分間)
        cache_key = f"product_search:{query}"
        redis_client.setex(
            cache_key, 
            1800,  # 30分
            json.dumps(results)
        )
        
        return results
    except Exception as e:
        # エラーハンドリング
        print(f"Scraping error: {e}")
        return []

@app.task(name='get_cached_products')
def get_cached_products(query: str) -> List[Dict]:
    """
    キャッシュされた商品情報を取得
    """
    cache_key = f"product_search:{query}"
    cached_results = redis_client.get(cache_key)
    
    if cached_results:
        return json.loads(cached_results)
    
    return []

# Celeryの設定
app.conf.beat_schedule = {
    'cleanup-cache': {
        'task': 'clean_expired_cache',
        'schedule': 3600.0,  # 1時間ごと
    },
}

@app.task(name='clean_expired_cache')
def clean_expired_cache():
    """
    期限切れのキャッシュを削除
    """
    # Redisの自動キャッシュ管理に委ねるため、特別な処理は不要
    pass
