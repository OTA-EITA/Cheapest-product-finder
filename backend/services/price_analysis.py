from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import statistics
import math

@dataclass
class PriceInfo:
    site_name: str
    current_price: float
    original_price: float
    discount_percentage: float
    url: str
    timestamp: datetime

class PriceComparator:
    def __init__(self, products: List[Dict]):
        self.products = [self._normalize_product(product) for product in products]
    
    def _normalize_product(self, product: Dict) -> PriceInfo:
        """
        商品情報を標準化
        """
        try:
            original_price = product.get('original_price', product['price'])
            current_price = product.get('price', original_price)
            
            # 割引率計算
            discount_percentage = self._calculate_discount(original_price, current_price)
            
            return PriceInfo(
                site_name=product.get('site', 'Unknown'),
                current_price=float(current_price),
                original_price=float(original_price),
                discount_percentage=discount_percentage,
                url=product.get('link', ''),
                timestamp=datetime.now()
            )
        except Exception as e:
            print(f"商品情報の標準化エラー: {e}")
            return None
    
    def _calculate_discount(self, original_price: float, current_price: float) -> float:
        """
        割引率を計算
        """
        try:
            if original_price <= 0 or current_price > original_price:
                return 0.0
            
            discount = (original_price - current_price) / original_price * 100
            return round(discount, 2)
        except Exception:
            return 0.0
    
    def get_best_deals(self, top_n: int = 5) -> List[Dict]:
        """
        最安値の商品を取得
        """
        # Noneを除外
        valid_products = [p for p in self.products if p is not None]
        
        if not valid_products:
            return []
        
        # 価格でソート
        sorted_products = sorted(valid_products, key=lambda x: x.current_price)
        
        # 上位N件を返却
        return [asdict(product) for product in sorted_products[:top_n]]
    
    def price_trend_analysis(self) -> Dict:
        """
        価格トレンド分析
        """
        if not self.products:
            return {}
        
        # 価格関連の統計
        prices = [p.current_price for p in self.products if p is not None]
        
        return {
            'average_price': round(statistics.mean(prices), 2),
            'median_price': round(statistics.median(prices), 2),
            'price_range': {
                'min': min(prices),
                'max': max(prices)
            },
            'price_variance': round(statistics.variance(prices), 2) if len(prices) > 1 else 0,
            'total_products': len(self.products)
        }
    
    def identify_significant_discounts(self, min_discount_threshold: float = 20.0) -> List[Dict]:
        """
        significant discountsを特定
        """
        significant_discounts = [
            asdict(product) for product in self.products 
            if product is not None and product.discount_percentage >= min_discount_threshold
        ]
        
        return sorted(
            significant_discounts, 
            key=lambda x: x['discount_percentage'], 
            reverse=True
        )
    
    def price_recommendation(self) -> Dict:
        """
        購入推奨に関する分析
        """
        trend_analysis = self.price_trend_analysis()
        best_deals = self.get_best_deals(3)
        significant_discounts = self.identify_significant_discounts()
        
        recommendation = {
            'buy_recommendation': False,
            'reason': '',
            'best_deals': best_deals[:3],
            'significant_discounts': significant_discounts
        }
        
        # 購入推奨のロジック
        if best_deals:
            lowest_price = best_deals[0]['current_price']
            average_price = trend_analysis['average_price']
            
            # 平均価格より20%以上安い場合に推奨
            if lowest_price < (average_price * 0.8):
                recommendation['buy_recommendation'] = True
                recommendation['reason'] = f'平均価格({average_price})より{lowest_price}で大幅に安くなっています'
        
        return recommendation

class PricePredictor:
    def __init__(self, historical_prices: List[Dict]):
        self.historical_prices = historical_prices
    
    def predict_future_price(self, days_ahead: int = 30) -> float:
        """
        単純な移動平均による価格予測
        """
        if not self.historical_prices:
            return None
        
        # 過去の価格データから予測
        prices = [p['price'] for p in self.historical_prices]
        
        # 移動平均
        window_size = min(len(prices), 7)  # 直近7日分
        moving_average = sum(prices[-window_size:]) / window_size
        
        # 季節性や変動の簡易的な考慮
        price_volatility = statistics.stdev(prices) if len(prices) > 1 else 0
        
        # 予測価格
        predicted_price = moving_average * (1 + (price_volatility / moving_average))
        
        return round(predicted_price, 2)

def process_price_data(products: List[Dict]) -> Dict:
    """
    価格データの総合的な処理
    """
    comparator = PriceComparator(products)
    
    return {
        'best_deals': comparator.get_best_deals(),
        'price_trend': comparator.price_trend_analysis(),
        'significant_discounts': comparator.identify_significant_discounts(),
        'recommendation': comparator.price_recommendation()
    }
