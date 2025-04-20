from .base_scraper import BaseScraper
import re
from urllib.parse import quote_plus

class AmazonScraper(BaseScraper):
    """Amazon用スクレイパー"""
    
    def __init__(self, user_agent=None, timeout=10):
        super().__init__(user_agent, timeout)
        self.base_url = "https://www.amazon.co.jp"
        self.search_url = f"{self.base_url}/s?k="
    
    def search(self, query, max_results=10):
        """Amazonでの商品検索"""
        search_url = self.search_url + quote_plus(query)
        soup = self.get_page(search_url)
        if not soup:
            return []
        
        results = []
        product_divs = soup.select('div[data-component-type="s-search-result"]')
        
        for div in product_divs[:max_results]:
            product_info = self.extract_product_info(div)
            if product_info:
                product_info['source'] = 'Amazon'
                results.append(product_info)
        
        return results
    
    def extract_product_info(self, item):
        """商品情報の抽出"""
        try:
            # 商品名
            name_elem = item.select_one('h2 a span')
            if not name_elem:
                return None
            
            name = name_elem.text.strip()
            
            # 商品URL
            url_elem = item.select_one('h2 a')
            url = self.base_url + url_elem['href'] if url_elem else None
            
            # 価格
            price_elem = item.select_one('.a-price .a-offscreen')
            price_text = price_elem.text.strip() if price_elem else None
            
            # 価格をテキストから数値に変換
            price = None
            if price_text:
                price_match = re.search(r'￥([\d,]+)', price_text)
                if price_match:
                    price = int(price_match.group(1).replace(',', ''))
            
            # 画像URL
            img_elem = item.select_one('img.s-image')
            img_url = img_elem['src'] if img_elem else None
            
            return {
                'name': name,
                'url': url,
                'price': price,
                'price_text': price_text,
                'img_url': img_url,
                'shipping': None,  # 送料情報は詳細ページの取得が必要
            }
        except Exception as e:
            self.logger.error(f"Error extracting product info: {str(e)}")
            return None
