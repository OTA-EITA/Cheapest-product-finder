import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.base import Base
from database.models import User, Product, PriceHistory, PriceAlert
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository

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

def test_user_repository_create(test_session):
    """ユーザーリポジトリのユーザー作成テスト"""
    user_repo = UserRepository(test_session)
    
    # 有効なユーザーの作成
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    
    created_user = user_repo.create(user)
    
    assert created_user.id is not None
    assert created_user.username == "testuser"
    assert created_user.email == "test@example.com"

def test_user_repository_duplicate_username(test_session):
    """重複ユーザー名のテスト"""
    user_repo = UserRepository(test_session)
    
    # 最初のユーザー作成
    user1 = User(
        username="testuser",
        email="test1@example.com",
        hashed_password="hashed_password"
    )
    user_repo.create(user1)
    
    # 同じユーザー名での作成は例外を投げるべき
    with pytest.raises(ValueError):
        user2 = User(
            username="testuser",
            email="test2@example.com",
            hashed_password="another_password"
        )
        user_repo.create(user2)

def test_user_repository_get_by_username(test_session):
    """ユーザー名による検索テスト"""
    user_repo = UserRepository(test_session)
    
    # ユーザー作成
    user = User(
        username="searchuser",
        email="search@example.com",
        hashed_password="hashed_password"
    )
    user_repo.create(user)
    
    # ユーザー名による検索
    found_user = user_repo.get_by_username("searchuser")
    
    assert found_user is not None
    assert found_user.username == "searchuser"

def test_product_repository_create(test_session):
    """商品リポジトリの商品作成テスト"""
    product_repo = ProductRepository(test_session)
    
    # 有効な商品の作成
    product = Product(
        name="テスト商品",
        source_site="Amazon",
        external_product_id="PROD123",
        current_price=1000.0,
        original_price=1500.0
    )
    
    created_product = product_repo.create(product)
    
    assert created_product.id is not None
    assert created_product.name == "テスト商品"
    assert created_product.current_price == 1000.0

def test_product_repository_search(test_session):
    """商品検索のテスト"""
    product_repo = ProductRepository(test_session)
    
    # テスト用の商品を複数作成
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
            current_price=40000.0
        ),
        Product(
            name="ノートパソコン Z",
            source_site="Yahoo",
            external_product_id="LAPTOP1",
            current_price=80000.0
        )
    ]
    
    for product in products:
        product_repo.create(product)
    
    # キーワード検索
    keyword_results = product_repo.search_products(query="スマートフォン")
    assert len(keyword_results) == 2
    
    # 価格範囲検索
    price_results = product_repo.search_products(min_price=45000.0, max_price=55000.0)
    assert len(price_results) == 1
    assert price_results[0].name == "スマートフォン X"

def test_product_repository_price_history(test_session):
    """価格履歴のテスト"""
    product_repo = ProductRepository(test_session)
    
    # 商品の作成
    product = Product(
        name="テスト商品",
        source_site="Amazon",
        external_product_id="PROD123",
        current_price=1000.0
    )
    created_product = product_repo.create(product)
    
    # 価格履歴の追加
    price_histories = [
        PriceHistory(product_id=created_product.id, price=900.0),
        PriceHistory(product_id=created_product.id, price=950.0),
        PriceHistory(product_id=created_product.id, price=1000.0)
    ]
    
    for history in price_histories:
        test_session.add(history)
    test_session.commit()
    
    # 価格履歴の取得
    history = product_repo.get_price_history(created_product.id)
    
    assert len(history) == 3
    assert history[0].price == 1000.0  # 最新の価格が先頭
    assert history[-1].price == 900.0  # 最も古い価格が最後

def test_repository_error_handling(test_session):
    """エラーハンドリングのテスト"""
    user_repo = UserRepository(test_session)
    
    # 無効なメールアドレスでの作成は例外を投げるべき
    with pytest.raises(ValueError):
        invalid_user = User(
            username="invaliduser",
            email="invalid-email",
            hashed_password="hashed_password"
        )
        user_repo.create(invalid_user)

def test_user_repository_price_alerts(test_session):
    """ユーザーの価格アラート取得テスト"""
    user_repo = UserRepository(test_session)
    product_repo = ProductRepository(test_session)
    
    # ユーザーと商品の作成
    user = User(
        username="alertuser",
        email="alert@example.com",
        hashed_password="hashed_password"
    )
    test_session.add(user)
    test_session.commit()
    
    products = [
        Product(
            name="商品1",
            source_site="Amazon",
            external_product_id="PROD1",
            current_price=1000.0
        ),
        Product(
            name="商品2",
            source_site="楽天市場",
            external_product_id="PROD2",
            current_price=2000.0
        )
    ]
    
    for product in products:
        product_repo.create(product)
    
    # 価格アラートの作成
    price_alerts = [
        PriceAlert(
            user_id=user.id, 
            product_id=products[0].id, 
            target_price=900.0
        ),
        PriceAlert(
            user_id=user.id, 
            product_id=products[1].id, 
            target_price=1800.0
        )
    ]
    
    for alert in price_alerts:
        test_session.add(alert)
    test_session.commit()
    
    # ユーザーの価格アラート取得
    user_alerts = user_repo.get_price_alerts(user.id)
    
    assert len(user_alerts) == 2
    assert user_alerts[0].product.name in ["商品1", "商品2"]
