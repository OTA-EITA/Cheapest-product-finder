from typing import List, Optional, Dict
from datetime import datetime

from database.models import SearchHistory, Product
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository
from scraping.scraper_manager import ScraperManager
from core.cache import cache_manager
from core.utils import normalize_text

class SearchService:
    """
    商品検索サービス
    """
    def __init__(
        self, 
        user_repository: UserRepository, 
        product_repository: ProductRepository,
        scraper_manager: Optional[ScraperManager] = None
    ):
        """
        初期化メソッド

        Args:
            user_repository (UserRepository): ユーザーリポジトリ
            product_repository (ProductRepository): 商品リポジトリ
            scraper_manager (Optional[ScraperManager]): スクレイパーマネージャー
        """
        self.user_repository = user_repository
        self.product_repository = product_repository
        self.scraper_manager = scraper_manager or ScraperManager()
    
    def search_products(
        self, 
        query: str, 
        user_id: Optional[int] = None,
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None,
        categories: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        商品検索

        Args:
            query (str): 検索クエリ
            user_id (Optional[int]): ユーザーID
            min_price (Optional[float]): 最小価格
            max_price (Optional[float]): 最大価格
            categories (Optional[List[str]]): 商品カテゴリ

        Returns:
            List[Dict]: 検索結果の商品リスト
        """
        # クエリの正規化
        normalized_query = normalize_text(query)
        
        # キャッシュチェック
        cache_key = f"search:{normalized_query}:{min_price}:{max_price}"
        cached_results = cache_manager.get(cache_key)
        if cached_results:
            return cached_results
        
        # データベース内の検索
        db_results = self.product_repository.search_products(
            query=normalized_query, 
            min_price=min_price, 
            max_price=max_price
        )
        
        # スクレイピングによる追加検索
        scraper_results = self._scrape_products(normalized_query, min_price, max_price)
        
        # 結果のマージ
        results = self._merge_results(db_results, scraper_results)
        
        # 検索履歴の保存
        if user_id:
            self._save_search_history(user_id, normalized_query)
        
        # キャッシュに保存
        cache_manager.set(cache_key, results)
        
        return results
    
    def _scrape_products(
        self, 
        query: str, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None
    ) -> List[Product]:
        """
        スクレイピングによる商品検索

        Args:
            query (str): 検索クエリ
            min_price (Optional[float]): 最小価格
            max_price (Optional[float]): 最大価格

        Returns:
            List[Product]: スクレイピングによる検索結果
        """
        try:
            scraped_products = self.scraper_manager.search_products(
                query, 
                min_price=min_price, 
                max_price=max_price
            )
            
            # スクレイピングされた商品をデータベースに保存
            saved_products = []
            for product_data in scraped_products:
                existing_product = self.product_repository.get_by_external_id(
                    product_data['external_product_id'], 
                    product_data['source_site']
                )
                
                if not existing_product:
                    new_product = Product(
                        name=product_data['name'],
                        source_site=product_data['source_site'],
                        external_product_id=product_data['external_product_id'],
                        current_price=product_data['price'],
                        original_price=product_data.get('original_price'),
                        url=product_data.get('link')
                    )
                    saved_products.append(
                        self.product_repository.create(new_product)
                    )
                else:
                    # 既存の商品の価格を更新
                    existing_product.current_price = product_data['price']
                    existing_product.original_price = product_data.get('original_price')
                    saved_products.append(existing_product)
            
            return saved_products
        
        except Exception as e:
            # ログ出力やエラーハンドリング
            print(f"スクレイピング中のエラー: {e}")
            return []
    
    def _merge_results(
        self, 
        db_results: List[Product], 
        scraper_results: List[Product]
    ) -> List[Dict]:
        """
        データベースとスクレイピング結果のマージ

        Args:
            db_results (List[Product]): データベース検索結果
            scraper_results (List[Product]): スクレイピング検索結果

        Returns:
            List[Dict]: マージされた検索結果
        """
        # 結果のマップを作成（外部IDでユニーク）
        results_map = {}
        
        # データベース結果を追加
        for product in db_results:
            results_map[product.external_product_id] = {
                'id': product.id,
                'name': product.name,
                'price': product.current_price,
                'original_price': product.original_price,
                'source_site': product.source_site,
                'external_product_id': product.external_product_id,
                'url': product.url,
                'source': 'database'
            }
        
        # スクレイピング結果を追加（既存の結果を上書き）
        for product in scraper_results:
            results_map[product.external_product_id] = {
                'id': product.id,
                'name': product.name,
                'price': product.current_price,
                'original_price': product.original_price,
                'source_site': product.source_site,
                'external_product_id': product.external_product_id,
                'url': product.url,
                'source': 'scraping'
            }
        
        # 価格の安い順にソート
        return sorted(
            list(results_map.values()), 
            key=lambda x: x['price']
        )
    
    def _save_search_history(self, user_id: int, query: str):
        """
        検索履歴の保存

        Args:
            user_id (int): ユーザーID
            query (str): 検索クエリ
        """
        search_history = SearchHistory(
            user_id=user_id,
            query=query,
            searched_at=datetime.utcnow()
        )
        
        try:
            self.user_repository.db.add(search_history)
            self.user_repository.commit()
        except Exception as e:
            # ログ出力やエラーハンドリング
            print(f"検索履歴の保存中のエラー: {e}")
            self.user_repository.rollback()
    
    def get_user_search_history(self, user_id: int) -> List[SearchHistory]:
        """
        ユーザーの検索履歴を取得

        Args:
            user_id (int): ユーザーID

        Returns:
            List[SearchHistory]: 検索履歴のリスト
        """
        return self.user_repository.get_search_history(user_id)
