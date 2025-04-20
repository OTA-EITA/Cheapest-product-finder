import os
import pytest
import numpy as np
from datetime import datetime, timedelta
import shutil

from services.ml_price_prediction import AdvancedPricePredictionModel, comprehensive_price_prediction
from services.ml_model_manager import MLModelManager, model_performance_analysis

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

@pytest.fixture
def predictions_fixture(sample_price_history):
    """
    価格予測結果のフィクスチャ
    """
    return comprehensive_price_prediction(sample_price_history)

def test_model_saving_and_loading(sample_price_history):
    """
    モデルの保存と読み込みのテスト
    """
    # テスト用の一時ディレクトリ
    test_model_dir = 'test_ml_models'
    os.makedirs(test_model_dir, exist_ok=True)
    
    try:
        # モデルの初期化とトレーニング
        model = AdvancedPricePredictionModel(sample_price_history)
        model.train_models()
        
        # モデル管理クラスの初期化
        model_manager = MLModelManager(model_dir=test_model_dir)
        
        # モデルの保存
        model_manager.save_model(model, 'test_model')
        
        # 保存されたモデルファイルの確認
        model_files = os.listdir(test_model_dir)
        assert len(model_files) > 0
        
        # モデルの読み込み
        for model_name in model.models.keys():
            loaded_model = model_manager.load_model('test_model', model_name)
            assert loaded_model is not None
    
    finally:
        # テスト用ディレクトリの削除
        shutil.rmtree(test_model_dir)

def test_visualization(sample_price_history, predictions_fixture):
    """
    価格予測の可視化テスト
    """
    # テスト用の一時ディレクトリ
    test_viz_dir = 'test_visualizations'
    os.makedirs(test_viz_dir, exist_ok=True)
    
    try:
        model_manager = MLModelManager()
        model_manager.visualize_price_prediction(
            sample_price_history, 
            predictions_fixture,
            output_dir=test_viz_dir
        )
        
        # 生成された可視化ファイルの確認
        viz_files = os.listdir(test_viz_dir)
        assert 'price_prediction.png' in viz_files
    
    finally:
        # テスト用ディレクトリの削除
        shutil.rmtree(test_viz_dir)

def test_prediction_report(sample_price_history, predictions_fixture):
    """
    予測レポートの生成テスト
    """
    model_manager = MLModelManager()
    report = model_manager.generate_prediction_report(
        sample_price_history, 
        predictions_fixture
    )
    
    # レポートの構造確認
    assert 'historical_stats' in report
    assert 'prediction_summary' in report
    assert 'model_predictions' in report
    
    # 統計情報の検証
    assert 'mean_price' in report['historical_stats']
    assert 'ensemble_mean' in report['prediction_summary']

def test_model_performance_analysis(predictions_fixture):
    """
    モデルパフォーマンス分析のテスト
    """
    performance_analysis = model_performance_analysis(predictions_fixture)
    
    # 分析結果の構造確認
    assert 'best_model' in performance_analysis
    assert 'worst_model' in performance_analysis
    assert 'model_comparison' in performance_analysis
    
    # モデル比較の詳細
    for model_name, metrics in performance_analysis['model_comparison'].items():
        assert 'R2' in metrics
        assert 'MSE' in metrics
        assert 'MAE' in metrics
