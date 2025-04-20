import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from database.base import Base
from database.models import (
    User, Product, PriceHistory, 
    PriceAlert, SearchHistory, ScrapingLog
)

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

def test_create_user(test_session):
    """ユーザーモデルの作成テスト"""
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    test_session.add(user)
    test_session.commit()

    assert user.id is not None
    assert user.username == "test_user"
    assert user.is_active is True
    assert isinstance(user.created_at, datetime)

def test_create_product(test_session):
    """商品モデルの作成テスト"""
    product = Product(
        name="テスト商品",
        source_site="Amazon",
        external_product_id="PROD123",
        current_price=1000.0,
        original_price=1500.0,
        url="https://example.com/product"
    )
    test_session.add(product)
    test_session.commit()

    assert product.id is not None
    assert product.name == "テスト商品"
    assert product.current_price == 1000.0

def test_price_history(test_session):
    """価格履歴モデルのテスト"""
    product = Product(
        name="テスト商品",
        source_site="Amazon",
        external_product_id="PROD123",
        current_price=1000.0
    )
    test_session.add(product)
    test_session.commit()

    price_history = PriceHistory(
        product_id=product.id,
        price=1000.0
    )
    test_session.add(price_history)
    test_session.commit()

    assert price_history.id is not None
    assert price_history.product == product
    assert isinstance(price_history.recorded_at, datetime)

def test_price_alert(test_session):
    """価格アラートモデルのテスト"""
    user = User(
        username="alert_user",
        email="alert@example.com",
        hashed_password="hashed_password"
    )
    product = Product(
        name="テスト商品",
        source_site="Amazon",
        external_product_id="PROD123",
        current_price=1000.0
    )
    test_session.add(user)
    test_session.add(product)
    test_session.commit()

    price_alert = PriceAlert(
        user_id=user.id,
        product_id=product.id,
        target_price=900.0
    )
    test_session.add(price_alert)
    test_session.commit()

    assert price_alert.id is not None
    assert price_alert.user == user
    assert price_alert.product == product
    assert price_alert.is_active is True

def test_search_history(test_session):
    """検索履歴モデルのテスト"""
    user = User(
        username="search_user",
        email="search@example.com",
        hashed_password="hashed_password"
    )
    test_session.add(user)
    test_session.commit()

    search_history = SearchHistory(
        user_id=user.id,
        query="スマートフォン"
    )
    test_session.add(search_history)
    test_session.commit()

    assert search_history.id is not None
    assert search_history.user == user
    assert search_history.query == "スマートフォン"

def test_scraping_log(test_session):
    """スクレイピングログモデルのテスト"""
    scraping_log = ScrapingLog(
        site_name="Amazon",
        query="テストクエリ",
        total_products=10,
        success=True
    )
    test_session.add(scraping_log)
    test_session.commit()

    assert scraping_log.id is not None
    assert scraping_log.site_name == "Amazon"
    assert scraping_log.total_products == 10
    assert scraping_log.success is True

def test_product_duplicate_constraint(test_session):
    """商品の一意性制約のテスト"""
    product1 = Product(
        name="テスト商品1",
        source_site="Amazon",
        external_product_id="PROD123",
        current_price=1000.0
    )
    product2 = Product(
        name="テスト商品2",
        source_site="Amazon",
        external_product_id="PROD123",
        current_price=1500.0
    )
    test_session.add(product1)
    test_session.commit()

    with pytest.raises(Exception):
        test_session.add(product2)
        test_session.commit()
