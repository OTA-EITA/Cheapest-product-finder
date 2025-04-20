import pytest
import asyncio
from datetime import datetime, timedelta
import numpy as np

from services.external_data_integration import (
    ExternalDataIntegrator, 
    ExternalDataFeatureEngineer,
    comprehensive_external_data_integration
)

@pytest.fixture
def sample_price_history():
    """
    サンプルの価格履歴データを生成
    """
    base_date = datetime.now()
    prices = []
    for i in range(100):
        date = base_date - timedelta(days=100-i)
        price = 1000 + i * 5 + np.sin(i/10) * 50 + np.random.normal(0, 10)
        prices.append({
            'date': date.strftime('%Y-%m-%d'),
            'price': price
        })
    return prices

@pytest.mark.asyncio
async def test_external_data_integrator():
    """
    外部データ統合機能のテスト
    """
    integrator = ExternalDataIntegrator()
    
    # 全ての外部データを取得
    external_data = await integrator.fetch_all_external_data()
    
    # データの構造確認
    assert 'economic_indicators' in external_data
    assert 'market_data' in external_data
    
    # 経済指標の確認
    indicators = external_data['economic_indicators']
    assert 'inflation' in indicators
    assert 'exchange_rates' in indicators
    assert 'consumer_confidence' in indicators
    
    # 市場データの確認
    market_data = external_data['market_data']
    assert 'stock_market' in market_data
    assert 'commodity_prices' in market_data

def test_external_data_feature_engineering(sample_price_history):
    """
    外部データからの特徴量生成テスト
    """
    # モックの外部データ
    mock_external_data = {
        'economic_indicators': {
            'inflation': {'inflation_rate': 2.0},
            'exchange_rates': {'usd_jpy': 135},
            'consumer_confidence': {'index': 105}
        },
        'market_data': {
            'stock_market': {'nikkei_225': 29000},
            'commodity_prices': {'crude_oil': 85}
        }
    }
    
    # 特徴量生成
    enhanced_prices = ExternalDataFeatureEngineer.generate_external_features(
        sample_price_history, 
        mock_external_data
    )
    
    # 拡張された価格履歴の確認
    assert len(enhanced_prices) == len(sample_price_history)
    
    # 追加された特徴量の確認
    for price_data in enhanced_prices:
        assert 'inflation_rate' in price_data
        assert 'usd_jpy_rate' in price_data
        assert 'consumer_confidence' in price_data
        assert 'nikkei_225' in price_data
        assert 'external_price_impact' in price_data
        assert 'adjusted_price' in price_data

@pytest.mark.asyncio
async def test_comprehensive_external_data_integration(sample_price_history):
    """
    包括的な外部データ統合のテスト
    """
    result = await comprehensive_external_data_integration(sample_price_history)
    
    # 結果の構造確認
    assert 'external_data' in result
    assert 'enhanced_prices' in result
    
    # 外部データの確認
    external_data = result['external_data']
    assert 'economic_indicators' in external_data
    assert 'market_data' in external_data
    
    # 拡張された価格履歴の確認
    enhanced_prices = result['enhanced_prices']
    assert len(enhanced_prices) == len(sample_price_history)
    
    # 追加された特徴量の確認
    for price_data in enhanced_prices:
        assert 'adjusted_price' in price_data
        assert 'external_price_impact' in price_data

def test_feature_engineering_edge_cases():
    """
    特徴量生成の境界条件テスト
    """
    # 空のデータセット
    empty_prices = []
    empty_external_data = {}
    
    enhanced_prices = ExternalDataFeatureEngineer.generate_external_features(
        empty_prices, 
        empty_external_data
    )
    
    assert len(enhanced_prices) == 0

def test_external_data_edge_cases():
    """
    外部データの境界条件テスト
    """
    integrator = ExternalDataIntegrator()
    
    # 不完全な外部データのハンドリング
    incomplete_external_data = {
        'economic_indicators': {},
        'market_data': {}
    }
    
    enhanced_prices = ExternalDataFeatureEngineer.generate_external_features(
        [{'date': '2023-01-01', 'price': 1000}], 
        incomplete_external_data
    )
    
    assert len(enhanced_prices) == 1
    assert 'adjusted_price' in enhanced_prices[0]

@pytest.mark.asyncio
async def test_error_handling_in_data_integration():
    """
    外部データ統合のエラーハンドリングテスト
    """
    # APIキーを与えない場合のテスト
    integrator = ExternalDataIntegrator()
    
    try:
        external_data = await integrator.fetch_all_external_data()
        
        # フォールバックデータが生成されることを確認
        assert 'economic_indicators' in external_data
        assert 'market_data' in external_data
    except Exception as e:
        pytest.fail(f"外部データ取得中に予期しないエラーが発生: {e}")

def test_feature_impact_calculation(sample_price_history):
    """
    外部データによる価格への影響計算のテスト
    """
    mock_external_data = {
        'economic_indicators': {
            'inflation': {'inflation_rate': 5.0},  # 高インフレ
            'exchange_rates': {'usd_jpy': 150},    # 円安
            'consumer_confidence': {'index': 90}   # 低い消費者信頼感
        },
        'market_data': {
            'stock_market': {'nikkei_225': 25000},  # 株価下落
            'commodity_prices': {'crude_oil': 100}
        }
    }
    
    enhanced_prices = ExternalDataFeatureEngineer.generate_external_features(
        sample_price_history, 
        mock_external_data
    )
    
    # 外部要因の価格への影響を検証
    for original, enhanced in zip(sample_price_history, enhanced_prices):
        # 元の価格と調整後の価格に有意な差があることを確認
        assert abs(enhanced['adjusted_price'] - original['price']) > 0
        assert 'external_price_impact' in enhanced
