import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.base import Base
from database.models import User, Product, PriceHistory
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository
from services.auth_service import AuthService
from services.price_alert_service import PriceAlertService
from services.search_service import SearchService
from services.price_comparison_service import PriceComparisonService

# テスト用のインメモリSQLiteデータベース
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_engine():
    """テスト用のデータベースエンジンを作成"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_session(test_engine):
    """テスト用のデータベースセッションを作成"""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def user_repository(test_session):
    """ユーザーリポジトリのフィクスチャ"""
    return UserRepository(test_session)

@pytest.fixture
def product_repository(test_session):
    """商品リポジトリのフィクスチャ"""
    return ProductRepository(test_session)

def test_auth_service_password_hashing():
    """パスワードハッシュ化のテスト"""
    password = "test_password"
    
    # パスワードのハッシュ化
    hashed_password = AuthService.get_password_hash(password)
    
    # 検証
    assert AuthService.verify_password(password, hashed_password) is True
    assert AuthService.verify_password("wrong_password", hashed_password) is False

def test_price_alert_service(test_session, user_repository, product_repository):
    """価格アラートサービスのテスト"""
    # ユーザーと商品の作成
    user = User(username="test_user", email="test@example.com", hashed_password="hashed_password")
    test_session.add(user)
    
    product = Product(
        name="テスト商品", 
        source_site="Amazon", 
        external_product_id="PROD123", 
        current_price=1000.0
    )
    test_session.add(product)
    test_session.commit()
    
    # 価格アラートサービスの初期化
    price_alert_service = PriceAlertService(user_repository, product_repository)
    
    # 価格アラートの作成
    price_alert = price_alert_service.create_price_alert(
        user_id=user.id, 
        product_id=product.id, 
        target_price=900.0
    )
    
    assert price_alert.id is not None
    assert price_alert.user_id == user.id
    assert price_alert.product_id == product.id
    assert price_alert.target_price == 900.0
    assert price_alert.is_active is True

def test_search_service(test_session, user_repository, product_repository):
    """検索サービスのテスト"""
    # テスト用の商品の作成
    products = [
        Product(
            name="スマートフォン X", 
            source_site="Amazon", 
            external_product_id="PHONE1", 
            current_price=50000.0
        ),
        Product(
            name="スマートフォン Y", 
            source_site="楽天市場", 
            external_product_id="PHONE2", 
            current_price=45000.0
        )
    ]
    
    for product in products:
        test_session.add(product)
    test_session.commit()
    
    # ユーザーの作成
    user = User(username="search_user", email="search@example.com", hashed_password="hashed_password")
    test_session.add(user)
    test_session.commit()
    
    # 検索サービスの初期化
    # Note: モックのスクレイパーマネージャーを使用する必要がある
    search_service = SearchService(user_repository, product_repository)
    
    # 検索の実行
    results = search_service.search_products(
        query="スマートフォン", 
        user_id=user.id
    )
    
    assert len(results) == 2
    assert results[0]['price'] == 45000.0  # 価格の安い順にソートされているはず
    
    # 検索履歴の確認
    search_history = search_service.get_user_search_history(user.id)
    assert len(search_history) == 1
    assert search_history[0].query == "スマートフォン"

def test_price_comparison_service(test_session, product_repository):
    """価格比較サービスのテスト"""
    # テスト用の商品と価格履歴の作成
    product = Product(
        name="テスト商品", 
        source_site="Amazon", 
        external_product_id="PROD123", 
        current_price=1000.0,
        original_price=1500.0
    )
    test_session.add(product)
    test_session.commit()
    
    # 価格履歴の追加
    price_histories = [
        PriceHistory(product_id=product.id, price=1200.0, recorded_at=datetime.utcnow() - timedelta(days=7)),
        PriceHistory(product_id=product.id, price=1100.0, recorded_at=datetime.utcnow() - timedelta(days=3)),
        PriceHistory(product_id=product.id, price=1000.0, recorded_at=datetime.utcnow())
    ]
    
    for history in price_histories:
        test_session.add(history)
    test_session.commit()
    
    # 価格比較サービスの初期化
    price_comparison_service = PriceComparisonService(product_repository)
    
    # 比較の実行
    comparison_results = price_comparison_service.compare_product_prices([product.id])
    
    assert len(comparison_results) == 1
    result = comparison_results[0]
    
    assert result['product_id'] == product.id
    assert result['current_price'] == 1000.0
    assert result['original_price'] == 1500.0
    
    # 価格分析の確認
    price_analysis = result['price_analysis']
    assert price_analysis['lowest_price'] == 1000.0
    assert price_analysis['highest_price'] == 1200.0
    assert price_analysis['price_trend'] == 'falling'

def test_price_prediction(test_session, product_repository):
    """価格予測のテスト"""
    # テスト用の商品と価格履歴の作成
    product = Product(
        name="テスト商品", 
        source_site="Amazon", 
        external_product_id="PROD123", 
        current_price=1000.0,
        original_price=1500.0
    )
    test_session.add(product)
    test_session.commit()
    
    # 価格履歴の追加
    price_histories = [
        PriceHistory(product_id=product.id, price=1200.0, recorded_at=datetime.utcnow() - timedelta(days=7)),
        PriceHistory(product_id=product.id, price=1100.0, recorded_at=datetime.utcnow() - timedelta(days=3)),
        PriceHistory(product_id=product.id, price=1000.0, recorded_at=datetime.utcnow())
    ]
    
    for history in price_histories:
        test_session.add(history)
    test_session.commit()
    
    # 価格比較サービスの初期化
    price_comparison_service = PriceComparisonService(product_repository)
    
    # 価格予測の実行
    prediction_result = price_comparison_service.predict_future_price(product.id)
    
    assert 'current_price' in prediction_result
    assert 'predicted_price' in prediction_result
    assert 'prediction_days' in prediction_result
    assert prediction_result['current_price'] == 1000.0
