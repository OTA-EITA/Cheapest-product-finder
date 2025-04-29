from .base_scraper import BaseScraper
import re
from urllib.parse import quote_plus

class RakutenScraper(BaseScraper):
    """楽天市場用スクレイパー"""
    
    def __init__(self, user_agent=None, timeout=10):
        super().__init__(user_agent, timeout)
        self.base_url = "https://search.rakuten.co.jp/search/mall/"
    
    def search(self, query, max_results=10, include_shipping=True, **kwargs):
        """楽天市場での商品検索"""
        search_url = self.base_url + quote_plus(query)
        soup = self.get_page(search_url)
        if not soup:
            return []
        
        results = []
        product_divs = soup.select('div.searchresultitem')
        
        for div in product_divs[:max_results]:
            product_info = self.extract_product_info(div, include_shipping)
            if product_info:
                product_info['source'] = '楽天市場'
                results.append(product_info)
        
        return results
    
    def extract_product_info(self, item, include_shipping=True):
        """商品情報の抽出"""
        try:
            # 商品名
            name_elem = item.select_one('h2.title a')
            if not name_elem:
                return None
            
            name = name_elem.text.strip()
            
            # 商品URL
            url = name_elem['href'] if name_elem else None
            
            # 価格
            price_elem = item.select_one('.important')
            price_text = price_elem.text.strip() if price_elem else None
            
            # 価格をテキストから数値に変換
            price = None
            if price_text:
                price_match = re.search(r'(\d+,?\d*)', price_text)
                if price_match:
                    price = int(price_match.group(1).replace(',', ''))
            
            # 画像URL
            img_elem = item.select_one('.image img')
            img_url = img_elem['src'] if img_elem else None
            
            # 送料情報
            shipping_info = None
            if include_shipping:
                shipping_elem = item.select_one('.shipping')
                shipping_info = shipping_elem.text.strip() if shipping_elem else "送料情報なし"
            
            return {
                'name': name,
                'url': url,
                'price': price,
                'price_text': price_text,
                'img_url': img_url,
                'shipping': shipping_info,
            }
        except Exception as e:
            self.logger.error(f"Error extracting product info: {str(e)}")
            return None
    
    def search_by_barcode(self, barcode, max_results=10, include_shipping=True, **kwargs):
        """バーコードで商品を検索する楽天市場専用実装"""
        # JANコードでの検索をサポート
        if len(barcode) == 13 and barcode.isdigit():  # JANらしい場合
            # JANコード専用の検索クエリ
            search_url = f"{self.base_url}{barcode}?jan={barcode}"
            soup = self.get_page(search_url)
            
            if soup:
                results = []
                product_divs = soup.select('div.searchresultitem')
                
                for div in product_divs[:max_results]:
                    product_info = self.extract_product_info(div, include_shipping)
                    if product_info:
                        product_info['source'] = '楽天市場'
                        results.append(product_info)
                
                if results:
                    return results
        
        # 通常検索にフォールバック
        return super().search_by_barcode(barcode, max_results, include_shipping, **kwargs)
