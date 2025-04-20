import re
from typing import List, Dict
from bs4 import BeautifulSoup
from urllib.parse import quote

from .base_scraper import BaseScraper
from core.exceptions import ScrapingError

class RakutenScraper(BaseScraper):
    """
    楽天市場用スクレイパー
    """
    def __init__(self):
        super().__init__('https://www.rakuten.co.jp')

    def _build_search_url(self, query: str, page: int = 1) -> str:
        """
        楽天市場検索URLを構築

        Args:
            query (str): 検索クエリ
            page (int): ページ番号

        Returns:
            str: 構築された検索URL
        """
        encoded_query = quote(query)
        return f'https://search.rakuten.co.jp/search/mall/{encoded_query}/?p={page}'

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

        for item in soup.select('.item_box'):
            try:
                # 商品名の抽出
                name_elem = item.select_one('.item_name')
                name = name_elem.text.strip() if name_elem else 'Unknown'

                # 価格の抽出
                price_elem = item.select_one('.price')
                price_str = price_elem.text.replace(',', '').replace('円', '').strip() if price_elem else None
                
                # 価格が数値に変換可能か確認
                try:
                    price = float(price_str) if price_str else None
                except ValueError:
                    price = None

                # 商品URL
                url_elem = item.select_one('.item_name a')
                product_url = url_elem['href'] if url_elem else None

                # 商品が有効な情報を持っている場合のみ追加
                if price and product_url:
                    products.append({
                        'name': name,
                        'price': price,
                        'url': product_url,
                        'source': '楽天市場'
                    })

            except Exception as e:
                self.logger.warning(f"楽天市場商品の解析中にエラー: {e}")

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
            name_elem = soup.select_one('#itemName')
            name = name_elem.text.strip() if name_elem else 'Unknown'

            # 価格の抽出
            price_elem = soup.select_one('.price')
            price_str = price_elem.text.replace(',', '').replace('円', '').strip() if price_elem else None

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
                'source': '楽天市場'
            }

            return details

        except Exception as e:
            raise ScrapingError(f"楽天市場商品詳細の解析エラー: {e}")
