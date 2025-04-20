import scrapy
from scrapy.crawler import CrawlerProcess
from typing import List, Dict
import logging

class AmazonScraper(scrapy.Spider):
    name = 'amazon_scraper'
    
    def __init__(self, search_query: str, *args, **kwargs):
        super(AmazonScraper, self).__init__(*args, **kwargs)
        self.search_query = search_query
        self.results = []
    
    def start_requests(self):
        search_url = f"https://www.amazon.co.jp/s?k={self.search_query}"
        yield scrapy.Request(url=search_url, callback=self.parse)
    
    def parse(self, response):
        for product in response.css('.s-result-item'):
            try:
                product_data = {
                    'name': product.css('h2 a span::text').get('').strip(),
                    'price': self._parse_price(product.css('.a-price-whole::text').get('')),
                    'link': response.urljoin(product.css('h2 a::attr(href)').get(''))
                }
                
                if product_data['name'] and product_data['price']:
                    self.results.append(product_data)
            except Exception as e:
                logging.error(f"Amazon scraping error: {e}")
    
    def _parse_price(self, price_str: str) -> float:
        try:
            return float(price_str.replace(',', ''))
        except (ValueError, TypeError):
            return 0.0

class RakutenScraper(scrapy.Spider):
    name = 'rakuten_scraper'
    
    def __init__(self, search_query: str, *args, **kwargs):
        super(RakutenScraper, self).__init__(*args, **kwargs)
        self.search_query = search_query
        self.results = []
    
    def start_requests(self):
        search_url = f"https://search.rakuten.co.jp/search/mall/{self.search_query}"
        yield scrapy.Request(url=search_url, callback=self.parse)
    
    def parse(self, response):
        for product in response.css('.dui-card'):
            try:
                product_data = {
                    'name': product.css('.title::text').get('').strip(),
                    'price': self._parse_price(product.css('.price__text::text').get('')),
                    'link': product.css('a::attr(href)').get('')
                }
                
                if product_data['name'] and product_data['price']:
                    self.results.append(product_data)
            except Exception as e:
                logging.error(f"Rakuten scraping error: {e}")
    
    def _parse_price(self, price_str: str) -> float:
        try:
            return float(price_str.replace(',', '').replace('円', ''))
        except (ValueError, TypeError):
            return 0.0

def scrape_products(query: str) -> List[Dict]:
    """
    複数のスクレイピングサービスを並列で実行
    """
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    amazon_spider = process.create_crawler(AmazonScraper)
    rakuten_spider = process.create_crawler(RakutenScraper)
    
    # スパイダーを設定して実行
    process.crawl(amazon_spider, search_query=query)
    process.crawl(rakuten_spider, search_query=query)
    
    process.start()
    
    # 結果を統合
    combined_results = []
    combined_results.extend(amazon_spider.spider.results)
    combined_results.extend(rakuten_spider.spider.results)
    
    return combined_results
