import pytest
from fastapi.testclient import TestClient
from main import app
from core.config import settings

client = TestClient(app)

def test_search_endpoint():
    # 正常な検索
    response = client.get("/search", params={"query": "スマートフォン"})
    assert response.status_code == 200
    
    results = response.json()
    assert isinstance(results, list)
    assert len(results) > 0
    assert all('id' in product and 'price' in product for product in results)

def test_invalid_search():
    # 空のクエリ
    response = client.get("/search", params={"query": ""})
    assert response.status_code == 422  # バリデーションエラー

def test_price_history_endpoint():
    # 価格履歴取得
    response = client.get("/price-history/product1")
    assert response.status_code == 200
    
    history = response.json()
    assert isinstance(history, list)
    assert all('date' in entry and 'price' in entry for entry in history)

def test_price_alert_endpoint():
    # 価格アラート作成 (モック認証)
    response = client.post(
        "/price-alerts/", 
        json={
            "product_id": "product1", 
            "target_price": 900
        }
    )
    assert response.status_code == 200
    
    alert = response.json()
    assert 'alert_id' in alert
    assert alert['target_price'] == 900

def test_recommendations_endpoint():
    # レコメンデーション取得
    response = client.get("/recommendations")
    assert response.status_code == 200
    
    recommendations = response.json()
    assert isinstance(recommendations, list)
    assert all('recommendation_score' in rec for rec in recommendations)
