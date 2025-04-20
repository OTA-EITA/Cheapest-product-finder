import pytest
from services.price_utils import PriceUtils
from core.exceptions import ValidationError, PriceAnalysisError

class TestPriceUtils:
    def test_calculate_discount(self):
        # 通常の割引計算
        assert PriceUtils.calculate_discount(1000, 800) == 20.0
        
        # 価格が同じ場合
        assert PriceUtils.calculate_discount(1000, 1000) == 0.0
        
        # 元の価格が0の場合
        assert PriceUtils.calculate_discount(0, 0) == 0.0
    
    def test_process_price_data(self):
        # 正常なデータ処理
        prices = [100, 200, 300, 400, 500]
        result = PriceUtils.process_price_data(prices)
        
        assert result['min_price'] == 100
        assert result['max_price'] == 500
        assert result['average_price'] == 300
        
        # 空のリストでエラー
        with pytest.raises(PriceAnalysisError):
            PriceUtils.process_price_data([])
    
    def test_validate_price_input(self):
        # 正常な価格入力
        assert PriceUtils.validate_price_input("1000") == 1000
        assert PriceUtils.validate_price_input("1,000円") == 1000
        
        # 無効な価格入力
        with pytest.raises(ValidationError):
            PriceUtils.validate_price_input("無効な価格")
        
        with pytest.raises(ValidationError):
            PriceUtils.validate_price_input("")
    
    def test_round_price(self):
        # 価格の丸め込み
        assert PriceUtils.round_price(10.456) == 10.46
        assert PriceUtils.round_price(10.454) == 10.45
        
        # 異常な入力
        assert PriceUtils.round_price(None) == 0.0
