import asyncio
import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_scraper import BaseScraper
from .amazon_scraper import AmazonScraper
from .rakuten_scraper import RakutenScraper
from core.exceptions import ScrapingError

class ScraperManager:
    """
    スクレイパーを管理し、複数のソースから情報を収集するクラス
    """
    def __init__(self, scrapers: Optional[List[BaseScraper]] = None):
        """
        スクレイパーマネージャーの初期化

        Args:
            scrapers (Optional[List[BaseScraper]], optional): 使用するスクレイパーのリスト
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # デフォルトスクレイパーの設定
        if scrapers is None:
            scrapers = [
                AmazonScraper(),
                RakutenScraper()
            ]
        
        self.scrapers = scrapers

    def search_products(
        self, 
        query: str, 
        max_sources: Optional[int] = None, 
        max_pages: int = 1
    ) -> List[Dict]:
        """
        複数のソースから商品を検索

        Args:
            query (str): 検索クエリ
            max_sources (Optional[int], optional): 最大検索ソース数
            max_pages (int, optional): 各ソースで検索するページ数

        Returns:
            List[Dict]: 検索結果の商品リスト
        """
        # 使用するスクレイパーの制限
        active_scrapers = self.scrapers[:max_sources] if max_sources else self.scrapers
        
        # スレッドプールを使用して並列検索
        all_products = []
        with ThreadPoolExecutor(max_workers=len(active_scrapers)) as executor:
            # 各スクレイパーの検索をフューチャーとして送信
            futures = [
                executor.submit(self._search_single_source, scraper, query, max_pages)
                for scraper in active_scrapers
            ]
            
            # 結果を収集
            for future in as_completed(futures):
                try:
                    products = future.result()
                    all_products.extend(products)
                except ScrapingError as e:
                    self.logger.warning(f"スクレイピング中のエラー: {e}")
        
        return all_products

    def _search_single_source(
        self, 
        scraper: BaseScraper, 
        query: str, 
        max_pages: int
    ) -> List[Dict]:
        """
        単一のソースから商品を検索

        Args:
            scraper (BaseScraper): 使用するスクレイパー
            query (str): 検索クエリ
            max_pages (int): 検索するページ数

        Returns:
            List[Dict]: 検索結果の商品リスト
        """
        products = []
        
        for page in range(1, max_pages + 1):
            try:
                page_products = scraper.search_products(query, page)
                products.extend(page_products)
            except ScrapingError as e:
                self.logger.warning(f"{scraper.__class__.__name__}でのスクレイピングエラー: {e}")
                break
        
        return products

    def get_product_details(self, product_url: str, source: Optional[str] = None) -> Dict:
        """
        特定のソースの商品詳細を取得

        Args:
            product_url (str): 商品のURL
            source (Optional[str], optional): 特定のソース名

        Returns:
            Dict: 商品の詳細情報
        """
        # ソースが指定されていない場合、URLからスクレイパーを選択
        if not source:
            source = self._detect_source(product_url)
        
        # 対応するスクレイパーを検索
        for scraper in self.scrapers:
            if scraper.__class__.__name__.lower().startswith(source.lower()):
                return scraper.parse_product_details(product_url)
        
        raise ScrapingError(f"指定されたソース {source} に対応するスクレイパーが見つかりません")

    def _detect_source(self, url: str) -> str:
        """
        URLからソースを検出

        Args:
            url (str): 商品URL

        Returns:
            str: 検出されたソース名
        """
        # 簡単なURL判定ロジック
        if 'amazon.co.jp' in url:
            return 'Amazon'
        elif 'rakuten.co.jp' in url:
            return '楽天市場'
        else:
            raise ScrapingError(f"サポートされていないソース: {url}")

    def compare_prices(
        self, 
        query: str, 
        max_sources: Optional[int] = None
    ) -> List[Dict]:
        """
        複数のソースの価格を比較

        Args:
            query (str): 検索クエリ
            max_sources (Optional[int], optional): 最大検索ソース数

        Returns:
            List[Dict]: 価格比較結果
        """
        products = self.search_products(query, max_sources)
        
        # 価格でソート
        sorted_products = sorted(products, key=lambda x: x.get('price', float('inf')))
        
        return sorted_products
