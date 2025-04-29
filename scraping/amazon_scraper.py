from .base_scraper import BaseScraper
import re
from urllib.parse import quote_plus

class AmazonScraper(BaseScraper):
    """Amazon用スクレイパー"""
    
    def __init__(self, user_agent=None, timeout=10):
        super().__init__(user_agent, timeout)
        self.base_url = "https://www.amazon.co.jp"
        self.search_url = f"{self.base_url}/s?k="
    
    def search(self, query, max_results=10, include_shipping=True, **kwargs):
        """Amazonでの商品検索"""
        search_url = self.search_url + quote_plus(query)
        soup = self.get_page(search_url)
        if not soup:
            return []
        
        results = []
        product_divs = soup.select('div[data-component-type="s-search-result"]')
        
        for div in product_divs[:max_results]:
            product_info = self.extract_product_info(div, include_shipping)
            if product_info:
                product_info['source'] = 'Amazon'
                results.append(product_info)
        
        return results
    
    def extract_product_info(self, item, include_shipping=True):
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
            
            # 送料情報の取得を試みる
            shipping_info = None
            if include_shipping:
                shipping_elem = item.select_one('.a-color-secondary:contains("配送料")')
                if shipping_elem:
                    shipping_info = shipping_elem.text.strip()
                else:
                    prime_elem = item.select_one('.a-icon-prime')
                    shipping_info = "Prime対象" if prime_elem else "送料情報なし"
            
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
        """バーコードで商品を検索するアマゾン専用実装"""
        # JANコード/ASINでの検索を最適化
        # ASINは10桁、JANコードは通常13桁
        if len(barcode) == 10 and barcode[0].isalpha():  # ASINらしい場合
            search_url = f"{self.base_url}/dp/{barcode}"
            soup = self.get_page(search_url)
            if soup and soup.select_one('#productTitle'):
                # 商品ページが取得できた場合、商品情報を抽出
                try:
                    name = soup.select_one('#productTitle').text.strip()
                    price_elem = soup.select_one('.a-price .a-offscreen') or soup.select_one('#price_inside_buybox')
                    price_text = price_elem.text.strip() if price_elem else None
                    
                    price = None
                    if price_text:
                        price_match = re.search(r'￥([\d,]+)', price_text)
                        if price_match:
                            price = int(price_match.group(1).replace(',', ''))
                    
                    img_url = None
                    img_elem = soup.select_one('#landingImage') or soup.select_one('#imgBlkFront')
                    if img_elem and 'src' in img_elem.attrs:
                        img_url = img_elem['src']
                    
                    shipping_info = None
                    if include_shipping:
                        shipping_elem = soup.select_one('#price-shipping-message')
                        if shipping_elem:
                            shipping_info = shipping_elem.text.strip()
                        else:
                            prime_elem = soup.select_one('.a-icon-prime')
                            shipping_info = "Prime対象" if prime_elem else "送料情報なし"
                    
                    return [{
                        'name': name,
                        'url': search_url,
                        'price': price,
                        'price_text': price_text,
                        'img_url': img_url,
                        'shipping': shipping_info,
                        'source': 'Amazon'
                    }]
                except Exception as e:
                    self.logger.error(f"Error extracting product data from ASIN page: {str(e)}")
        
        # 通常検索パターンにフォールバック
        return super().search_by_barcode(barcode, max_results, include_shipping, **kwargs)
