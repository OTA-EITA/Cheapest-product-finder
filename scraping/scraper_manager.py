import concurrent.futures
import logging
from .amazon_scraper import AmazonScraper
from .rakuten_scraper import RakutenScraper
from .yahoo_shopping_scraper import YahooShoppingScraper

class ScraperManager:
    """複数のスクレイパーを管理するクラス"""
    
    def __init__(self, max_workers=3, timeout=10):
        self.max_workers = max_workers
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # スクレイパーの初期化
        self.scrapers = {
            'amazon': AmazonScraper(timeout=timeout),
            'rakuten': RakutenScraper(timeout=timeout),
            'yahoo': YahooShoppingScraper(timeout=timeout),
        }
    
    def search_all(self, query, max_results_per_site=10):
        """すべてのサイトで並列に検索を実行"""
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_site = {
                executor.submit(scraper.search, query, max_results_per_site): site_name
                for site_name, scraper in self.scrapers.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_site):
                site_name = future_to_site[future]
                try:
                    results = future.result()
                    self.logger.info(f"Got {len(results)} results from {site_name}")
                    all_results.extend(results)
                except Exception as e:
                    self.logger.error(f"Error searching {site_name}: {str(e)}")
        
        # 価格の安い順にソート（価格情報がない商品は最後に）
        all_results.sort(key=lambda x: x.get('price', float('inf')) or float('inf'))
        
        return all_results
    
    def search_site(self, site_name, query, max_results=10):
        """特定のサイトのみで検索を実行"""
        if site_name not in self.scrapers:
            self.logger.error(f"Unknown site: {site_name}")
            return []
        
        try:
            return self.scrapers[site_name].search(query, max_results)
        except Exception as e:
            self.logger.error(f"Error searching {site_name}: {str(e)}")
            return []
