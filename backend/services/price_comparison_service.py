from typing import List, Dict, Optional
from datetime import datetime, timedelta

from database.models import Product, PriceHistory
from repositories.product_repository import ProductRepository
from ml_models.price_predictor import PricePredictor
from core.utils import sanitize_price

class PriceComparisonService:
    """
    価格比較サービス
    """
    def __init__(
        self, 
        product_repository: ProductRepository,
        price_predictor: Optional[PricePredictor] = None
    ):
        """
        初期化メソッド

        Args:
            product_repository (ProductRepository): 商品リポジトリ
            price_predictor (Optional[PricePredictor]): 価格予測モデル
        """
        self.product_repository = product_repository
        self.price_predictor = price_predictor or PricePredictor()
    
    def compare_product_prices(
        self, 
        product_ids: List[int]
    ) -> List[Dict]:
        """
        複数の商品の価格を比較

        Args:
            product_ids (List[int]): 比較する商品のID

        Returns:
            List[Dict]: 価格比較結果
        """
        comparison_results = []
        
        for product_id in product_ids:
            product = self.product_repository.get_by_id(product_id)
            
            if not product:
                continue
            
            # 価格履歴の取得
            price_history = self.product_repository.get_price_history(product_id)
            
            # 価格分析
            price_analysis = self._analyze_price_history(price_history)
            
            comparison_results.append({
                'product_id': product.id,
                'name': product.name,
                'current_price': product.current_price,
                'original_price': product.original_price,
                'source_site': product.source_site,
                'price_analysis': price_analysis
            })
        
        return comparison_results
    
    def _analyze_price_history(
        self, 
        price_history: List[PriceHistory]
    ) -> Dict:
        """
        価格履歴の分析

        Args:
            price_history (List[PriceHistory]): 価格履歴

        Returns:
            Dict: 価格分析結果
        """
        if not price_history:
            return {
                'lowest_price': None,
                'highest_price': None,
                'average_price': None,
                'price_trend': 'no_data'
            }
        
        # 価格の抽出
        prices = [history.price for history in price_history]
        
        # 基本的な統計情報
        lowest_price = min(prices)
        highest_price = max(prices)
        average_price = sum(prices) / len(prices)
        
        # 価格トレンドの判定
        price_trend = self._determine_price_trend(price_history)
        
        return {
            'lowest_price': lowest_price,
            'highest_price': highest_price,
            'average_price': average_price,
            'price_trend': price_trend
        }
    
    def _determine_price_trend(
        self, 
        price_history: List[PriceHistory]
    ) -> str:
        """
        価格トレンドの判定

        Args:
            price_history (List[PriceHistory]): 価格履歴

        Returns:
            str: 価格トレンド ('rising', 'falling', 'stable', 'no_data')
        """
        if len(price_history) < 2:
            return 'no_data'
        
        # 最新の価格と1週間前の価格を比較
        recent_prices = price_history[:min(7, len(price_history))]
        
        first_price = recent_prices[-1].price
        last_price = recent_prices[0].price
        price_change_percentage = (last_price - first_price) / first_price * 100
        
        if price_change_percentage > 5:
            return 'rising'
        elif price_change_percentage < -5:
            return 'falling'
        else:
            return 'stable'
    
    def predict_future_price(
        self, 
        product_id: int, 
        prediction_days: int = 30
    ) -> Dict:
        """
        将来の価格予測

        Args:
            product_id (int): 商品ID
            prediction_days (int, optional): 予測日数

        Returns:
            Dict: 価格予測結果
        """
        product = self.product_repository.get_by_id(product_id)
        
        if not product:
            return {'error': '商品が見つかりません'}
        
        # 価格履歴の取得
        price_history = self.product_repository.get_price_history(product_id)
        
        # 予測のための特徴量の準備
        features = {
            'original_price': product.original_price or product.current_price,
            'current_price': product.current_price,
            'days_since_last_sale': (datetime.utcnow() - price_history[0].recorded_at).days if price_history else 0,
            'seasonal_factor': self._calculate_seasonal_factor()
        }
        
        # 価格予測の実行
        predicted_price = self.price_predictor.predict(features)
        
        return {
            'current_price': product.current_price,
            'predicted_price': predicted_price,
            'prediction_days': prediction_days
        }
    
    def _calculate_seasonal_factor(self) -> float:
        """
        季節性係数の計算

        Returns:
            float: 季節性係数
        """
        current_month = datetime.utcnow().month
        
        # 季節ごとの係数
        seasonal_factors = {
            # 冬（12,1,2）
            12: 0.9, 1: 0.8, 2: 0.85,
            # 春（3,4,5）
            3: 1.1, 4: 1.2, 5: 1.15,
            # 夏（6,7,8）
            6: 1.3, 7: 1.4, 8: 1.35,
            # 秋（9,10,11）
            9: 1.0, 10: 0.95, 11: 0.9
        }
        
        return seasonal_factors.get(current_month, 1.0)
