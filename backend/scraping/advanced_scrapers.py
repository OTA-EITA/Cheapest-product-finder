import scrapy
from scrapy.crawler import CrawlerProcess
from typing import List, Dict, Optional
import logging
import re
import json
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup

class AdvancedWebScraper:
    """
    高度なウェブスクレイピングのための基底クラス
    """
    def __init__(self, site_name: str, base_url: str):
        self.site_name = site_name
        self.base_url = base_url
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7'
        })
    
    def _clean_price(self, price_str: str) -> Optional[float]:
        """
        価格文字列のクリーニング
        """
        if not price_str:
            return None
        
        # 数字と小数点以外を削除
        cleaned = re.sub(r'[^\d.]', '', price_str)
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _extract_product_details(self, product_element) -> Optional[Dict]:
        """
        サブクラスでオーバーライドする必要がある抽象メソッド
        """
        raise NotImplementedError("サブクラスで実装してください")
    
    def search(self, query: str) -> List[Dict]:
        """
        検索を実行し、結果を取得
        サブクラスでオーバーライドする
        """
        raise NotImplementedError("サブクラスで実装してください")

class AmazonAdvancedScraper(AdvancedWebScraper):
    def __init__(self):
        super().__init__(
            site_name='Amazon',
            base_url='https://www.amazon.co.jp'
        )
    
    def _extract_product_details(self, product_element):
        try:
            name_element = product_element.select_one('h2 a span')
            price_element = product_element.select_one('.a-price-whole')
            link_element = product_element.select_one('h2 a')
            image_element = product_element.select_one('img.s-image')
            
            if not (name_element and price_element and link_element):
                return None
            
            name = name_element.get_text(strip=True)
            price = self._clean_price(price_element.get_text())
            link = self.base_url + link_element.get('href', '')
            image_url = image_element.get('src', '') if image_element else ''
            
            return {
                'name': name,
                'price': price,
                'link': link,
                'image_url': image_url,
                'site': self.site_name
            }
        except Exception as e:
            logging.error(f"Amazon商品抽出エラー: {e}")
            return None
    
    def search(self, query: str) -> List[Dict]:
        """
        Amazon商品検索
        """
        encoded_query = quote_plus(query)
        search_url = f"{self.base_url}/s?k={encoded_query}"
        
        try:
            response = self.session.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            product_elements = soup.select('.s-result-item')
            
            products = []
            for element in product_elements[:10]:  # 上位10件
                product = self._extract_product_details(element)
                if product:
                    products.append(product)
            
            return products
        
        except Exception as e:
            logging.error(f"Amazon検索エラー: {e}")
            return []

class RakutenAdvancedScraper(AdvancedWebScraper):
    def __init__(self):
        super().__init__(
            site_name='Rakuten',
            base_url='https://www.rakuten.co.jp'
        )
    
    def _extract_product_details(self, product_element):
        try:
            name_element = product_element.select_one('.title')
            price_element = product_element.select_one('.price')
            link_element = product_element.select_one('a.product-image')
            image_element = product_element.select_one('img.product-image')
            
            if not (name_element and price_element and link_element):
                return None
            
            name = name_element.get_text(strip=True)
            price = self._clean_price(price_element.get_text())
            link = link_element.get('href', '')
            image_url = image_element.get('src', '') if image_element else ''
            
            return {
                'name': name,
                'price': price,
                'link': link,
                'image_url': image_url,
                'site': self.site_name
            }
        except Exception as e:
            logging.error(f"楽天商品抽出エラー: {e}")
            return None
    
    def search(self, query: str) -> List[Dict]:
        """
        楽天市場商品検索
        """
        encoded_query = quote_plus(query)
        search_url = f"https://search.rakuten.co.jp/search/mall/{encoded_query}"
        
        try:
            response = self.session.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            product_elements = soup.select('.item-grid')
            
            products = []
            for element in product_elements[:10]:  # 上位10件
                product = self._extract_product_details(element)
                if product:
                    products.append(product)
            
            return products
        
        except Exception as e:
            logging.error(f"楽天検索エラー: {e}")
            return []

def multi_site_product_search(query: str) -> List[Dict]:
    """
    複数サイトを横断した商品検索
    """
    scrapers = [
        AmazonAdvancedScraper(),
        RakutenAdvancedScraper()
    ]
    
    all_products = []
    for scraper in scrapers:
        try:
            products = scraper.search(query)
            all_products.extend(products)
        except Exception as e:
            logging.error(f"{scraper.site_name}検索エラー: {e}")
    
    return all_products
