import pytest
import numpy as np
from datetime import datetime, timedelta
from services.ml_price_prediction import AdvancedPricePredictionModel, comprehensive_price_prediction

@pytest.fixture
def sample_price_history():
    """
    サンプルの価格履歴データを生成
    """
    base_date = datetime.now()
    prices = []
    for i in range(100):  # より多くのデータポイント
        date = base_date - timedelta(days=100-i)
        # より複雑な価格パターンをシミュレート
        price = 1000 + i * 5 + np.sin(i/10) * 50 + np.random.normal(0, 10)
        prices.append({
            'date': date.strftime('%Y-%m-%d'),
            'price': price
        })
    return prices

def test_model_training(sample_price_history):
    """
    モデルのトレーニングテスト
    """
    model = AdvancedPricePredictionModel(sample_price_history)
    performance = model.train_models()
    
    # 各モデルの性能指標を確認
    for model_name, metrics in performance.items():
        assert 'mse' in metrics
        assert 'mae' in metrics
        assert 'r2' in metrics
        assert metrics['r2'] >= -1  # R2スコアの範囲チェック
        assert metrics['mse'] >= 0  # MSEは非負

def test_price_prediction(sample_price_history):
    """
    価格予測のテスト
    """
    model = AdvancedPricePredictionModel(sample_price_history)
    model.train_models()
    
    # 30日先の予測
    prediction = model.predict_price(days_ahead=30)
    
    assert 'model' in prediction
    assert 'dates' in prediction
    assert 'predicted_prices' in prediction
    assert len(prediction['predicted_prices']) == 30
    assert len(prediction['dates']) == 30

def test_ensemble_prediction(sample_price_history):
    """
    アンサンブル予測のテスト
    """
    model = AdvancedPricePredictionModel(sample_price_history)
    model.train_models()
    
    ensemble_result = model.ensemble_prediction()
    
    assert 'ensemble_prediction' in ensemble_result
    assert 'individual_predictions' in ensemble_result
    assert len(ensemble_result['ensemble_prediction']) > 0
    
    # 個別モデルの予測を確認
    for model_name, prediction in ensemble_result['individual_predictions'].items():
        assert 'dates' in prediction
        assert 'predicted_prices' in prediction

def test_comprehensive_prediction(sample_price_history):
    """
    包括的な価格予測のテスト
    """
    result = comprehensive_price_prediction(sample_price_history)
    
    # 結果の構造チェック
    assert 'model_performance' in result
    assert 'predictions' in result
    
    # モデル性能の確認
    for model_name, metrics in result['model_performance'].items():
        assert 'mse' in metrics
        assert 'mae' in metrics
        assert 'r2' in metrics

def test_error_handling():
    """
    エラーハンドリングのテスト
    """
    # 不十分なデータでのモデル作成
    with pytest.raises(ValueError):
        AdvancedPricePredictionModel([])
    
    # 存在しないモデルでの予測
    model = AdvancedPricePredictionModel([
        {'date': '2023-01-01', 'price': 1000},
        {'date': '2023-01-02', 'price': 1100}
    ])
    
    with pytest.raises(ValueError):
        model.predict_price(model_name='non_existent_model')
