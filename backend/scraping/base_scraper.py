import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from urllib3.exceptions import MaxRetryError, NewConnectionError

from core.exceptions import ScrapingError

class BaseScraper(ABC):
    """
    スクレイピングの抽象基本クラス
    """
    def __init__(
        self, 
        base_url: str, 
        timeout: int = 10, 
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        スクレイパーの初期化

        Args:
            base_url (str): スクレイピング対象のベースURL
            timeout (int): リクエストのタイムアウト時間（秒）
            max_retries (int): リクエストの最大リトライ回数
            retry_delay (int): リトライ間の遅延時間（秒）
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # ロガーの設定
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # ヘッダーの設定
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br'
        }

    def fetch_page(self, url: str) -> str:
        """
        指定されたURLからHTMLコンテンツを取得

        Args:
            url (str): 取得するページのURL

        Returns:
            str: ページのHTMLコンテンツ

        Raises:
            ScrapingError: ページ取得に失敗した場合
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.text
            
            except (RequestException, Timeout, ConnectionError, 
                    MaxRetryError, NewConnectionError) as e:
                self.logger.warning(
                    f"ページ取得エラー (試行 {attempt + 1}/{self.max_retries}): {e}"
                )
                
                # リトライ間の遅延
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    # 最終的な失敗
                    raise ScrapingError(f"ページ取得に完全に失敗: {e}")

    @abstractmethod
    def parse_search_results(self, html_content: str) -> List[Dict]:
        """
        検索結果からデータを抽出する抽象メソッド

        Args:
            html_content (str): スクレイピングするHTMLコンテンツ

        Returns:
            List[Dict]: 抽出された商品情報
        """
        pass

    @abstractmethod
    def parse_product_details(self, product_url: str) -> Dict:
        """
        商品詳細ページからデータを抽出する抽象メソッド

        Args:
            product_url (str): 商品詳細ページのURL

        Returns:
            Dict: 商品の詳細情報
        """
        pass

    def search_products(
        self, 
        query: str, 
        page: int = 1,
        validate_results: bool = True
    ) -> List[Dict]:
        """
        商品を検索し、結果を取得

        Args:
            query (str): 検索クエリ
            page (int, optional): ページ番号. デフォルトは1.
            validate_results (bool, optional): 結果の検証を行うかどうか

        Returns:
            List[Dict]: 検索結果の商品リスト
        """
        search_url = self._build_search_url(query, page)
        html_content = self.fetch_page(search_url)
        results = self.parse_search_results(html_content)
        
        if validate_results:
            results = self._validate_search_results(results)
        
        return results

    def _validate_search_results(self, results: List[Dict]) -> List[Dict]:
        """
        検索結果の検証と不正なデータの除外

        Args:
            results (List[Dict]): 検索結果

        Returns:
            List[Dict]: 検証後の検索結果
        """
        valid_results = []
        for result in results:
            try:
                # 必須フィールドの確認
                if not all(key in result for key in ['name', 'price', 'url']):
                    continue
                
                # 価格が数値で0より大きいことを確認
                if not isinstance(result['price'], (int, float)) or result['price'] <= 0:
                    continue
                
                valid_results.append(result)
            
            except Exception as e:
                self.logger.warning(f"結果の検証中にエラー: {e}")
        
        return valid_results

    @abstractmethod
    def _build_search_url(self, query: str, page: int) -> str:
        """
        検索URLを構築する抽象メソッド

        Args:
            query (str): 検索クエリ
            page (int): ページ番号

        Returns:
            str: 構築された検索URL
        """
        pass
