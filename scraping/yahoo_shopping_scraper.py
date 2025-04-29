from .base_scraper import BaseScraper
import re
from urllib.parse import quote_plus

class YahooShoppingScraper(BaseScraper):
    """Yahoo!ショッピング用スクレイパー"""
    
    def __init__(self, user_agent=None, timeout=10):
        super().__init__(user_agent, timeout)
        self.base_url = "https://shopping.yahoo.co.jp/search"
    
    def search(self, query, max_results=10, include_shipping=True, **kwargs):
        """Yahoo!ショッピングでの商品検索"""
        search_url = f"{self.base_url}?p={quote_plus(query)}"
        soup = self.get_page(search_url)
        if not soup:
            return []
        
        results = []
        product_divs = soup.select('div.LoopList__item')
        
        for div in product_divs[:max_results]:
            product_info = self.extract_product_info(div, include_shipping)
            if product_info:
                product_info['source'] = 'Yahoo!ショッピング'
                results.append(product_info)
        
        return results
    
    def extract_product_info(self, item, include_shipping=True):
        """商品情報の抽出"""
        try:
            # 商品名
            name_elem = item.select_one('a._2EW-04-9Eayr')
            if not name_elem:
                return None
            
            name = name_elem.text.strip()
            
            # 商品URL
            url = name_elem['href'] if name_elem else None
            
            # 価格
            price_elem = item.select_one('span._3-CgJZLU91dR')
            price_text = price_elem.text.strip() if price_elem else None
            
            # 価格をテキストから数値に変換
            price = None
            if price_text:
                price_match = re.search(r'(\d+,?\d*)', price_text)
                if price_match:
                    price = int(price_match.group(1).replace(',', ''))
            
            # 画像URL
            img_elem = item.select_one('img._2Qs-G5Q0')
            img_url = img_elem['src'] if img_elem else None
            
            # 送料情報
            shipping_info = None
            if include_shipping:
                shipping_elem = item.select_one('span._3izCJ6Kc-TF4')
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
        """バーコードで商品を検索するYahoo!ショッピング専用実装"""
        # JANコード/ISBNでの検索
        if barcode.isdigit() and (len(barcode) == 13 or len(barcode) == 10):
            search_url = f"{self.base_url}?p={barcode}&jan={barcode}"
            soup = self.get_page(search_url)
            if soup:
                results = []
                product_divs = soup.select('div.LoopList__item')
                
                for div in product_divs[:max_results]:
                    product_info = self.extract_product_info(div, include_shipping)
                    if product_info:
                        product_info['source'] = 'Yahoo!ショッピング'
                        results.append(product_info)
                
                if results:
                    return results
        
        # 通常検索にフォールバック
        return super().search_by_barcode(barcode, max_results, include_shipping, **kwargs)
