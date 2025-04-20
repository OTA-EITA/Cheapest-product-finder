import pytest
import sys
import os
from typing import Generator

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.utils.test_helpers import (
    generate_mock_product, 
    generate_mock_price_history,
    generate_random_string
)

@pytest.fixture(scope='function')
def mock_product():
    """
    モック商品データを提供するフィクスチャ
    """
    return generate_mock_product()

@pytest.fixture(scope='function')
def mock_price_history(mock_product):
    """
    モック価格履歴を提供するフィクスチャ
    """
    return generate_mock_price_history(mock_product['id'])

@pytest.fixture(scope='session')
def database_url() -> str:
    """
    テスト用データベースURL
    """
    return 'sqlite:///:memory:'

@pytest.fixture(scope='function')
def mock_user():
    """
    モックユーザーデータを提供するフィクスチャ
    """
    return {
        'id': generate_random_string(),
        'username': generate_random_string(),
        'email': f'{generate_random_string()}@example.com'
    }

@pytest.fixture(scope='function')
def mock_scraping_context():
    """
    スクレイピングテスト用のモックコンテキスト
    """
    return {
        'query': 'テスト商品',
        'max_sources': 2,
        'timeout': 10
    }

@pytest.fixture(scope='session')
def temp_db_connection():
    """
    一時的なデータベース接続を提供
    
    Yields:
        データベース接続オブジェクト
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from database.base import Base

    # インメモリSQLiteデータベースエンジンの作成
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False})
    
    # テーブルの作成
    Base.metadata.create_all(engine)
    
    # セッションの作成
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=engine
    )
    
    try:
        session = TestingSessionLocal()
        yield session
    finally:
        session.close()
        engine.dispose()
