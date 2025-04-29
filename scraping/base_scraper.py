import requests
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import logging

class BaseScraper(ABC):
    """スクレイピングの基底クラス"""
    
    def __init__(self, user_agent=None, timeout=10):
        self.session = requests.Session()
        self.timeout = timeout
        self.headers = {
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
        }
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_page(self, url):
        """ページの取得と BeautifulSoup オブジェクトの作成"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    @abstractmethod
    def search(self, query, max_results=10, include_shipping=True, **kwargs):
        """商品検索の実装（サブクラスで実装必須）"""
        pass
    
    @abstractmethod
    def extract_product_info(self, item, include_shipping=True):
        """商品情報の抽出（サブクラスで実装必須）"""
        pass
        
    def search_by_barcode(self, barcode, max_results=10, include_shipping=True, **kwargs):
        """バーコードから商品を検索するデフォルト実装"""
        # デフォルトでは通常検索を使用、サブクラスで必要に応じてオーバーライド
        self.logger.info(f"バーコード検索にデフォルト実装を使用: {barcode}")
        return self.search(barcode, max_results, include_shipping, **kwargs)
