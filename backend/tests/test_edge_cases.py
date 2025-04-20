import pytest
from services.price_analysis import PriceComparator, PricePredictor
from services.product_service import ProductSearchService

def test_empty_product_list():
    """
    空の商品リストに対するテスト
    """
    # 空のリストでのPriceComparatorの動作
    comparator = PriceComparator([])
    assert comparator.get_best_deals() == []
    assert comparator.price_trend_analysis() == {
        'average_price': 0,
        'median_price': 0,
        'price_range': {'min': 0, 'max': 0},
        'price_variance': 0,
        'total_products': 0
    }

def test_single_product_analysis():
    """
    単一の商品に対する分析テスト
    """
    single_product = [{
        'name': '単一商品',
        'price': 1000,
        'original_price': 1200
    }]
    
    comparator = PriceComparator(single_product)
    
    # 最安値取得
    best_deals = comparator.get_best_deals()
    assert len(best_deals) == 1
    assert best_deals[0]['price'] == 1000
    
    # トレンド分析
    trend = comparator.price_trend_analysis()
    assert trend['average_price'] == 1000
    assert trend['median_price'] == 1000

def test_price_predictor_edge_cases():
    """
    価格予測の境界条件テスト
    """
    # 空の履歴
    empty_predictor = PricePredictor([])
    assert empty_predictor.predict_future_price() is None
    
    # 単一の価格
    single_price_predictor = PricePredictor([{'price': 1000}])
    prediction = single_price_predictor.predict_future_price()
    assert prediction == 1000

def test_extreme_price_scenarios():
    """
    極端な価格シナリオのテスト
    """
    extreme_products = [
        {'name': '非常に高価な商品', 'price': 1000000, 'original_price': 1200000},
        {'name': '非常に安い商品', 'price': 10, 'original_price': 100}
    ]
    
    comparator = PriceComparator(extreme_products)
    
    # 最安値取得
    best_deals = comparator.get_best_deals()
    assert len(best_deals) == 2
    assert best_deals[0]['price'] == 10  # 最も安い商品が先頭
    
    # 割引分析
    discounts = comparator.identify_significant_discounts()
    assert len(discounts) == 2

def test_product_search_error_handling():
    """
    商品検索のエラーハンドリングテスト
    """
    # 空のクエリ
    with pytest.raises(ValueError):
        ProductSearchService.search_products("")
    
    # 不正な価格範囲
    with pytest.raises(ValueError):
        ProductSearchService.search_products(
            "テスト商品", 
            min_price=-100, 
            max_price=50
        )

def test_price_alert_validation():
    """
    価格アラートのバリデーションテスト
    """
    # 不正なユーザーID
    with pytest.raises(ValueError):
        ProductSearchService.create_price_alert(
            user_id="", 
            product_id="test_product", 
            target_price=1000
        )
    
    # 不正な価格
    with pytest.raises(ValueError):
        ProductSearchService.create_price_alert(
            user_id="test_user", 
            product_id="test_product", 
            target_price=-100
        )

def test_recommendation_edge_cases():
    """
    レコメンデーションの境界条件テスト
    """
    # 存在しないユーザー
    recommendations = ProductSearchService.get_personalized_recommendations("non_existent_user")
    assert len(recommendations) > 0  # デフォルトの推奨商品が返されること
