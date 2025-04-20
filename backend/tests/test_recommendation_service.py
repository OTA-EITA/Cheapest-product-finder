from services.product_service import ProductRecommendationService
from datetime import datetime, timedelta

def test_recommendation_service():
    # パーソナライズされた推奨のテスト
    user_id = "test_user"
    search_history = [
        {
            'query': 'スマートフォン',
            'date': datetime.now() - timedelta(days=10),
            'category': 'エレクトロニクス'
        }
    ]
    
    # 推奨を取得
    recommendations = ProductRecommendationService.get_personalized_recommendations(
        user_id, 
        search_history
    )
    
    # 推奨の基本的な検証
    assert len(recommendations) > 0
    
    # 各推奨商品の必須フィールドを確認
    for rec in recommendations:
        assert 'id' in rec
        assert 'name' in rec
        assert 'price' in rec
        assert 'recommendation_score' in rec
        assert rec['recommendation_score'] > 0
    
    # 推奨スコアが降順であることを確認
    assert recommendations == sorted(recommendations, key=lambda x: x['recommendation_score'], reverse=True)
