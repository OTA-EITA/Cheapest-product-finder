import pytest
import requests_mock
from scraping.amazon_scraper import AmazonScraper
from scraping.rakuten_scraper import RakutenScraper
from core.exceptions import ScrapingError

@pytest.mark.unit
class TestAmazonScraper:
    def setup_method(self):
        self.scraper = AmazonScraper()

    def test_build_search_url(self):
        url = self.scraper._build_search_url('スマートフォン', page=1)
        assert 'https://www.amazon.co.jp/s?k=' in url
        assert 'スマートフォン' in url
        assert 'page=1' in url

    def test_parse_search_results_with_mock_data(self):
        # モックHTMLデータ
        mock_html = """
        <html>
            <body>
                <div class="s-result-item">
                    <h2><a><span>テスト商品</span></a></h2>
                    <div class="a-price">
                        <span class="a-price-whole">1000</span>
                    </div>
                </div>
            </body>
        </html>
        """
        
        results = self.scraper.parse_search_results(mock_html)
        
        assert len(results) > 0
        assert all('name' in product for product in results)
        assert all('price' in product for product in results)

    @pytest.mark.parametrize("query", ['スマートフォン', 'ノートPC'])
    def test_search_products_integration(self, query):
        # 実際のウェブサイトへの統合テスト
        # 注意: これは実際のウェブサイトへのリクエストを伴うため、注意が必要
        results = self.scraper.search_products(query)
        
        assert len(results) > 0
        for product in results:
            assert 'name' in product
            assert 'price' in product
            assert product['price'] > 0

@pytest.mark.unit
class TestRakutenScraper:
    def setup_method(self):
        self.scraper = RakutenScraper()

    def test_build_search_url(self):
        url = self.scraper._build_search_url('テレビ', page=2)
        assert 'https://search.rakuten.co.jp/search/mall/' in url
        assert 'テレビ' in url
        assert 'p=2' in url

    def test_parse_search_results_with_mock_data(self):
        # モックHTMLデータ
        mock_html = """
        <html>
            <body>
                <div class="item_box">
                    <div class="item_name">テスト商品</div>
                    <div class="price">1500円</div>
                </div>
            </body>
        </html>
        """
        
        results = self.scraper.parse_search_results(mock_html)
        
        assert len(results) > 0
        assert all('name' in product for product in results)
        assert all('price' in product for product in results)

@pytest.mark.parametrize("ScraperClass", [AmazonScraper, RakutenScraper])
def test_scraper_error_handling(ScraperClass):
    """
    スクレイパーのエラーハンドリングをテスト
    """
    scraper = ScraperClass()
    
    with requests_mock.Mocker() as m:
        # 接続エラーをシミュレート
        m.get(scraper._build_search_url('テスト'), exc=requests_mock.exceptions.ConnectTimeout)
        
        with pytest.raises(ScrapingError):
            scraper.search_products('テスト')
