import re
from typing import List, Dict
from bs4 import BeautifulSoup
from urllib.parse import quote

from .base_scraper import BaseScraper
from core.exceptions import ScrapingError

class AmazonScraper(BaseScraper):
    """
    Amazon用スクレイパー
    """
    def __init__(self):
        super().__init__('https://www.amazon.co.jp')

    def _build_search_url(self, query: str, page: int = 1) -> str:
        """
        Amazon検索URLを構築

        Args:
            query (str): 検索クエリ
            page (int): ページ番号

        Returns:
            str: 構築された検索URL
        """
        encoded_query = quote(query)
        return f'https://www.amazon.co.jp/s?k={encoded_query}&page={page}'

    def parse_search_results(self, html_content: str) -> List[Dict]:
        """
        検索結果からデータを抽出

        Args:
            html_content (str): スクレイピングするHTMLコンテンツ

        Returns:
            List[Dict]: 抽出された商品情報
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []

        for item in soup.select('.s-result-item'):
            try:
                # 商品名の抽出
                name_elem = item.select_one('h2 a span')
                name = name_elem.text.strip() if name_elem else 'Unknown'

                # 価格の抽出
                price_elem = item.select_one('.a-price-whole')
                price_str = price_elem.text.replace(',', '').strip() if price_elem else None
                
                # 価格が数値に変換可能か確認
                try:
                    price = float(price_str) if price_str else None
                except ValueError:
                    price = None

                # 元の価格（割引前）の抽出
                original_price_elem = item.select_one('.a-text-price')
                original_price_str = original_price_elem.text.replace(',', '').strip() if original_price_elem else None
                
                try:
                    original_price = float(original_price_str) if original_price_str else None
                except ValueError:
                    original_price = None

                # 商品URL
                url_elem = item.select_one('h2 a')
                product_url = f"https://www.amazon.co.jp{url_elem['href']}" if url_elem else None

                # 商品が有効な情報を持っている場合のみ追加
                if price and product_url:
                    products.append({
                        'name': name,
                        'price': price,
                        'original_price': original_price,
                        'url': product_url,
                        'source': 'Amazon'
                    })

            except Exception as e:
                self.logger.warning(f"Amazon商品の解析中にエラー: {e}")

        return products

    def parse_product_details(self, product_url: str) -> Dict:
        """
        商品詳細ページからデータを抽出

        Args:
            product_url (str): 商品詳細ページのURL

        Returns:
            Dict: 商品の詳細情報
        """
        try:
            html_content = self.fetch_page(product_url)
            soup = BeautifulSoup(html_content, 'html.parser')

            # 商品名の抽出
            name_elem = soup.select_one('#productTitle')
            name = name_elem.text.strip() if name_elem else 'Unknown'

            # 価格の抽出
            price_elem = soup.select_one('.a-price-whole')
            price_str = price_elem.text.replace(',', '').strip() if price_elem else None

            # 価格が数値に変換可能か確認
            try:
                price = float(price_str) if price_str else None
            except ValueError:
                price = None

            # その他の詳細情報
            details = {
                'name': name,
                'price': price,
                'url': product_url,
                'source': 'Amazon'
            }

            return details

        except Exception as e:
            raise ScrapingError(f"Amazon商品詳細の解析エラー: {e}")
