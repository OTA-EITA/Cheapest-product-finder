import pytest
from typing import Dict, Any
import random
import string

def generate_random_string(length: int = 10) -> str:
    """
    ランダムな文字列を生成

    Args:
        length (int, optional): 文字列の長さ. デフォルトは10.

    Returns:
        str: ランダムな文字列
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_mock_product(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    モック商品データを生成

    Args:
        overrides (Dict[str, Any], optional): デフォルト値のオーバーライド

    Returns:
        Dict[str, Any]: モック商品データ
    """
    default_product = {
        'id': generate_random_string(),
        'name': f'テスト商品 {generate_random_string()}',
        'price': round(random.uniform(100, 10000), 2),
        'source': random.choice(['Amazon', '楽天市場', 'Yahoo!ショッピング']),
        'category': random.choice(['エレクトロニクス', '家電', '衣類', '本']),
        'url': f'https://example.com/product/{generate_random_string()}'
    }
    
    if overrides:
        default_product.update(overrides)
    
    return default_product

def generate_mock_price_history(product_id: str, num_entries: int = 5) -> list:
    """
    価格履歴のモックデータを生成

    Args:
        product_id (str): 商品ID
        num_entries (int, optional): 生成する履歴エントリー数. デフォルトは5.

    Returns:
        list: 価格履歴エントリーのリスト
    """
    from datetime import datetime, timedelta
    
    history = []
    base_price = random.uniform(1000, 50000)
    
    for i in range(num_entries):
        history.append({
            'product_id': product_id,
            'price': round(base_price * (1 + random.uniform(-0.2, 0.2)), 2),
            'date': (datetime.now() - timedelta(days=i)).isoformat(),
            'source': random.choice(['Amazon', '楽天市場', 'Yahoo!ショッピング'])
        })
    
    return history

def assert_valid_product(product: Dict[str, Any]):
    """
    商品データの妥当性を検証

    Args:
        product (Dict[str, Any]): 検証する商品データ

    Raises:
        AssertionError: 商品データが不正な場合
    """
    assert 'id' in product, "商品IDが必要です"
    assert 'name' in product, "商品名が必要です"
    assert 'price' in product, "価格が必要です"
    assert product['price'] > 0, "価格は0より大きい必要があります"
    assert 'source' in product, "商品ソースが必要です"

def generate_test_config():
    """
    テスト用の設定を生成

    Returns:
        Dict[str, Any]: テスト設定
    """
    return {
        'database': {
            'url': 'sqlite:///:memory:',  # インメモリデータベース
            'echo': False
        },
        'logging': {
            'level': 'ERROR'
        }
    }

def pytest_generate_tests(metafunc):
    """
    パラメータ化テストのカスタム生成

    Args:
        metafunc: テストメタ関数
    """
    if 'mock_product' in metafunc.fixturenames:
        metafunc.parametrize('mock_product', [generate_mock_product() for _ in range(3)])
