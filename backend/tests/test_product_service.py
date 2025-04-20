import pytest
from services.product_service import ProductSearchService, ProductRecommendationService
from core.exceptions import ValidationError

def test_search_products():
    # 通常の検索
    results = ProductSearchService.search_products('スマートフォン')
    assert len(results) > 0
    assert all('price' in product for product in results)
    
    # 価格フィルター付き検索
    filtered_results = ProductSearchService.search_products(
        'スマートフォン', 
        min_price=900, 
        max_price=1100
    )
    assert all(900 <= product['price'] <= 1100 for product in filtered_results)

def test_search_products_empty_query():
    with pytest.raises(ValidationError):
        ProductSearchService.search_products('')
    with pytest.raises(ValidationError):
        ProductSearchService.search_products('   ')

def test_get_price_history():
    history = ProductSearchService.get_price_history('product1')
    assert len(history) > 0
    assert all('date' in item and 'price' in item and 'source' in item for item in history)

def test_create_price_alert():
    # 正常なアラート作成
    alert = ProductSearchService.create_price_alert(
        user_id='user1', 
        product_id='product1', 
        target_price=900
    )
    assert 'alert_id' in alert
    assert alert['target_price'] == 900
    
    # 不正な価格でのアラート作成
    with pytest.raises(ValidationError):
        ProductSearchService.create_price_alert(
            user_id='user1', 
            product_id='product1', 
            target_price=-100
        )

def test_recommendation_service():
    # パーソナライズされた推奨
    recommendations = ProductRecommendationService.get_personalized_recommendations('user1')
    assert len(recommendations) > 0
    assert all('recommendation_score' in rec for rec in recommendations)

def test_product_similarity():
    product1 = {
        'id': 'prod1',
        'name': 'スマートフォン',
        'price': 1000,
        'category': 'エレクトロニクス'
    }
    product2 = {
        'id': 'prod2',
        'name': '別のスマートフォン',
        'price': 1200,
        'category': 'エレクトロニクス'
    }
    
    similarity = ProductRecommendationService.calculate_similarity(product1, product2)
    assert 0 <= similarity <= 1  # 類似度は0-1の範囲
