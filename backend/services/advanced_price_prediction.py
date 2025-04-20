import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import statistics
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

class AdvancedPricePredictionModel:
    def __init__(self, historical_prices: List[Dict]):
        """
        高度な価格予測モデル
        
        Args:
            historical_prices (List[Dict]): 価格履歴データ
                各エントリは {'date': str, 'price': float} の形式
        """
        self.historical_prices = self._preprocess_data(historical_prices)
    
    def _preprocess_data(self, historical_prices: List[Dict]) -> pd.DataFrame:
        """
        データの前処理と特徴量エンジニアリング
        
        Args:
            historical_prices (List[Dict]): 生の価格履歴
        
        Returns:
            pd.DataFrame: 前処理されたデータフレーム
        """
        df = pd.DataFrame(historical_prices)
        
        # 日付の変換
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values('date', inplace=True)
        
        # 追加の特徴量
        df['days_since_start'] = (df['date'] - df['date'].min()).dt.days
        df['price_change'] = df['price'].diff()
        df['price_change_pct'] = df['price'].pct_change() * 100
        
        return df
    
    def linear_regression_prediction(self, days_ahead: int = 30) -> Dict:
        """
        線形回帰による価格予測
        
        Args:
            days_ahead (int): 予測する日数
        
        Returns:
            Dict: 予測結果の詳細
        """
        X = self.historical_prices['days_since_start'].values.reshape(-1, 1)
        y = self.historical_prices['price'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # 将来の日付での予測
        last_day = self.historical_prices['days_since_start'].max()
        future_days = np.array(range(last_day + 1, last_day + days_ahead + 1)).reshape(-1, 1)
        predicted_prices = model.predict(future_days)
        
        return {
            'model_type': 'linear_regression',
            'prediction_days': days_ahead,
            'predicted_prices': predicted_prices.tolist(),
            'coefficient': model.coef_[0],
            'intercept': model.intercept_
        }
    
    def polynomial_regression_prediction(self, days_ahead: int = 30, degree: int = 2) -> Dict:
        """
        多項式回帰による価格予測
        
        Args:
            days_ahead (int): 予測する日数
            degree (int): 多項式の次数
        
        Returns:
            Dict: 予測結果の詳細
        """
        X = self.historical_prices['days_since_start'].values.reshape(-1, 1)
        y = self.historical_prices['price'].values
        
        # 多項式特徴量の生成
        poly = PolynomialFeatures(degree=degree)
        X_poly = poly.fit_transform(X)
        
        model = LinearRegression()
        model.fit(X_poly, y)
        
        # 将来の日付での予測
        last_day = self.historical_prices['days_since_start'].max()
        future_days = np.array(range(last_day + 1, last_day + days_ahead + 1)).reshape(-1, 1)
        future_days_poly = poly.transform(future_days)
        predicted_prices = model.predict(future_days_poly)
        
        return {
            'model_type': 'polynomial_regression',
            'prediction_days': days_ahead,
            'degree': degree,
            'predicted_prices': predicted_prices.tolist()
        }
    
    def price_volatility_analysis(self) -> Dict:
        """
        価格の変動性分析
        
        Returns:
            Dict: 価格変動に関する統計情報
        """
        return {
            'mean_price': self.historical_prices['price'].mean(),
            'median_price': self.historical_prices['price'].median(),
            'price_std': self.historical_prices['price'].std(),
            'price_variance': self.historical_prices['price'].var(),
            'coefficient_of_variation': (
                self.historical_prices['price'].std() / 
                self.historical_prices['price'].mean() * 100
            ),
            'max_daily_change_pct': self.historical_prices['price_change_pct'].abs().max()
        }
    
    def seasonal_price_pattern(self) -> Dict:
        """
        季節性価格パターンの検出
        
        Returns:
            Dict: 季節性に関する分析結果
        """
        # 月ごとの平均価格
        monthly_avg = self.historical_prices.groupby(
            self.historical_prices['date'].dt.month
        )['price'].mean()
        
        return {
            'monthly_average_prices': monthly_avg.to_dict(),
            'lowest_price_month': monthly_avg.idxmin(),
            'highest_price_month': monthly_avg.idxmax()
        }
    
    def recommend_purchase_timing(self) -> Dict:
        """
        購入のタイミングを推奨
        
        Returns:
            Dict: 購入推奨に関する分析
        """
        volatility = self.price_volatility_analysis()
        seasonal_pattern = self.seasonal_price_pattern()
        
        # 複合的な購入推奨ロジック
        recommendation = {
            'recommended_action': 'wait',
            'reasons': []
        }
        
        # 価格変動が大きい場合は慎重な対応を推奨
        if volatility['coefficient_of_variation'] > 20:
            recommendation['reasons'].append('価格変動が大きいため、購入を慎重に')
        
        # 最も価格が低い月であれば購入を推奨
        current_month = datetime.now().month
        if current_month == seasonal_pattern['lowest_price_month']:
            recommendation['recommended_action'] = 'buy'
            recommendation['reasons'].append('最も価格が低い月です')
        
        # 価格が平均を下回っている場合
        if (volatility['mean_price'] - self.historical_prices['price'].iloc[-1]) > 0:
            recommendation['recommended_action'] = 'buy'
            recommendation['reasons'].append('現在の価格が平均を下回っています')
        
        return recommendation

def comprehensive_price_analysis(historical_prices: List[Dict]) -> Dict:
    """
    総合的な価格分析
    
    Args:
        historical_prices (List[Dict]): 価格履歴データ
    
    Returns:
        Dict: 包括的な価格分析結果
    """
    model = AdvancedPricePredictionModel(historical_prices)
    
    return {
        'linear_prediction': model.linear_regression_prediction(),
        'polynomial_prediction': model.polynomial_regression_prediction(),
        'volatility_analysis': model.price_volatility_analysis(),
        'seasonal_pattern': model.seasonal_price_pattern(),
        'purchase_recommendation': model.recommend_purchase_timing()
    }
