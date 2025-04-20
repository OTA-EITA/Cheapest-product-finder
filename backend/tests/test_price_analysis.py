import pytest
from services.price_utils import PriceUtils
from core.exceptions import PriceAnalysisError, ValidationError

def test_calculate_discount():
    # 通常のケース
    assert PriceUtils.calculate_discount(1000, 800) == 20.0
    
    # 価格が同じ場合
    assert PriceUtils.calculate_discount(1000, 1000) == 0.0
    
    # 元の価格が0の場合
    assert PriceUtils.calculate_discount(0, 100) == 0.0

def test_process_price_data():
    prices = [100, 200, 300, 400, 500]
    result = PriceUtils.process_price_data(prices)
    
    assert result['min_price'] == 100.0
    assert result['max_price'] == 500.0
    assert result['average_price'] == 300.0

def test_process_price_data_empty_list():
    with pytest.raises(PriceAnalysisError):
        PriceUtils.process_price_data([])

def test_validate_price_input():
    # 正常な入力
    assert PriceUtils.validate_price_input('1000') == 1000.0
    assert PriceUtils.validate_price_input('1,000円') == 1000.0
    
    # 無効な入力
    with pytest.raises(ValidationError):
        PriceUtils.validate_price_input('abc')
    
    with pytest.raises(ValidationError):
        PriceUtils.validate_price_input('')

def test_round_price():
    assert PriceUtils.round_price(10.456) == 10.46
    assert PriceUtils.round_price(10.454) == 10.45
    assert PriceUtils.round_price(-10.456) == -10.46
