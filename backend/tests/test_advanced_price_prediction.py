import pytest
import numpy as np
from services.advanced_price_prediction import (
    AdvancedPricePredictionModel, 
    comprehensive_price_analysis
)
from datetime import datetime, timedelta

@pytest.fixture
def sample_price_history():
    """
    サンプルの価格履歴データを生成
    """
    base_date = datetime.now()
    prices = []
    for i in range(30):
        date = base_date - timedelta(days=30-i)
        # 季節性とトレンドを模倣したサンプル価格
        price = 1000 + i * 10 + np.sin(i/5) * 50
        prices.append({
            'date': date.strftime('%Y-%m-%d'),
            'price': price
        })
    return prices

def test_linear_regression_prediction(sample_price_history):
    """
    線形回帰による価格予測のテスト
    """
    model = AdvancedPricePredictionModel(sample_price_history)
    prediction = model.linear_regression_prediction()
    
    assert 'predicted_prices' in prediction
    assert len(prediction['predicted_prices']) == 30
    assert prediction['model_type'] == 'linear_regression'

def test_polynomial_regression_prediction(sample_price_history):
    """
    多項式回帰による価格予測のテスト
    """
    model = AdvancedPricePredictionModel(sample_price_history)
    prediction = model.polynomial_regression_prediction(degree=2)
    
    assert 'predicted_prices' in prediction
    assert len(prediction['predicted_prices']) == 30
    assert prediction['model_type'] == 'polynomial_regression'
    assert prediction['degree'] == 2

def test_price_volatility_analysis(sample_price_history):
    """
    価格変動分析のテスト
    """
    model = AdvancedPricePredictionModel(sample_price_history)
    volatility = model.price_volatility_analysis()
    
    assert 'mean_price' in volatility
    assert 'median_price' in volatility
    assert 'price_std' in volatility
    assert 'coefficient_of_variation' in volatility
    assert 'max_daily_change_pct' in volatility

def test_seasonal_price_pattern(sample_price_history):
    """
    季節性価格パターンのテスト
    """
    model = AdvancedPricePredictionModel(sample_price_history)
    seasonal_pattern = model.seasonal_price_pattern()
    
    assert 'monthly_average_prices' in seasonal_pattern
    assert 'lowest_price_month' in seasonal_pattern
    assert 'highest_price_month' in seasonal_pattern

def test_purchase_recommendation(sample_price_history):
    """
    購入推奨のテスト
    """
    model = AdvancedPricePredictionModel(sample_price_history)
    recommendation = model.recommend_purchase_timing()
    
    assert 'recommended_action' in recommendation
    assert 'reasons' in recommendation
    assert recommendation['recommended_action'] in ['wait', 'buy']
    assert isinstance(recommendation['reasons'], list)

def test_comprehensive_price_analysis(sample_price_history):
    """
    総合的な価格分析のテスト
    """
    analysis = comprehensive_price_analysis(sample_price_history)
    
    # 必要なキーの存在確認
    assert 'linear_prediction' in analysis
    assert 'polynomial_prediction' in analysis
    assert 'volatility_analysis' in analysis
    assert 'seasonal_pattern' in analysis
    assert 'purchase_recommendation' in analysis
