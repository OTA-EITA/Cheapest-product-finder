from typing import List, Dict, Optional
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from core.exceptions import ValidationError, PriceAnalysisError

class PriceUtils:
    @staticmethod
    def calculate_discount(original_price: float, current_price: float) -> float:
        """
        割引率を計算

        Args:
            original_price (float): 元の価格
            current_price (float): 現在の価格

        Returns:
            float: 割引率（%）
        """
        try:
            if original_price <= 0:
                return 0.0
            
            discount = ((original_price - current_price) / original_price) * 100
            return round(discount, 2)
        except (TypeError, ZeroDivisionError):
            return 0.0

    @staticmethod
    def process_price_data(prices: List[float]) -> Dict[str, float]:
        """
        価格データの統計分析

        Args:
            prices (List[float]): 価格のリスト

        Returns:
            Dict[str, float]: 価格分析結果
        
        Raises:
            PriceAnalysisError: 価格データの処理に失敗した場合
        """
        if not prices:
            raise PriceAnalysisError("価格データが空です")

        try:
            # 最小・最大・平均価格の計算
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)

            # 標準偏差の計算
            variance = sum((x - avg_price) ** 2 for x in prices) / len(prices)
            std_dev = variance ** 0.5

            return {
                'min_price': round(min_price, 2),
                'max_price': round(max_price, 2),
                'average_price': round(avg_price, 2),
                'price_variance': round(variance, 2),
                'price_standard_deviation': round(std_dev, 2)
            }
        except (TypeError, ValueError) as e:
            raise PriceAnalysisError(f"価格データの処理中にエラーが発生しました: {str(e)}")

    @staticmethod
    def validate_price_input(price: str) -> float:
        """
        価格入力の検証と数値変換

        Args:
            price (str): 価格文字列

        Returns:
            float: 変換された価格

        Raises:
            ValidationError: 価格が無効な場合
        """
        try:
            # 数値以外の文字を除去 (カンマ、円記号など)
            cleaned_price = ''.join(char for char in price if char.isdigit())
            
            if not cleaned_price:
                raise ValidationError("無効な価格入力")
            
            return float(cleaned_price)
        except (ValueError, InvalidOperation):
            raise ValidationError("価格の解析に失敗しました")

    @staticmethod
    def round_price(price: float, decimal_places: int = 2) -> float:
        """
        価格を指定された小数点以下の桁数で四捨五入

        Args:
            price (float): 丸める価格
            decimal_places (int, optional): 小数点以下の桁数. デフォルトは2.

        Returns:
            float: 丸めた価格
        """
        try:
            return float(Decimal(str(price)).quantize(
                Decimal(f'1.{"0" * decimal_places}'), 
                rounding=ROUND_HALF_UP
            ))
        except (TypeError, InvalidOperation):
            return 0.0
