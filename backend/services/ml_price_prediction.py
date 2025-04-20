import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

class AdvancedPricePredictionModel:
    def __init__(self, historical_data: List[Dict]):
        """
        高度な価格予測モデル
        
        Args:
            historical_data (List[Dict]): 価格履歴データ
        """
        self.df = self._preprocess_data(historical_data)
        self.models = {}
    
    def _preprocess_data(self, historical_data: List[Dict]) -> pd.DataFrame:
        """
        データの前処理と特徴量エンジニアリング
        
        Returns:
            pd.DataFrame: 前処理されたデータフレーム
        """
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values('date', inplace=True)
        
        # 追加の特徴量
        df['days_since_start'] = (df['date'] - df['date'].min()).dt.days
        
        # 時系列特徴量
        df['price_7d_ma'] = df['price'].rolling(window=7).mean()
        df['price_30d_ma'] = df['price'].rolling(window=30).mean()
        
        # トレンド特徴量
        df['price_change'] = df['price'].diff()
        df['price_change_pct'] = df['price'].pct_change() * 100
        
        # 季節性特徴量
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        
        # ラグ特徴量
        for lag in [1, 7, 14, 30]:
            df[f'price_lag_{lag}'] = df['price'].shift(lag)
        
        # 外部要因をシミュレート（インフレ率など）
        np.random.seed(42)
        df['external_factor'] = np.random.normal(1, 0.1, len(df))
        
        return df.dropna()
    
    def _prepare_features_and_target(self):
        """
        モデルトレーニング用の特徴量とターゲットを準備
        
        Returns:
            tuple: X_train, X_test, y_train, y_test
        """
        # 特徴量の選択
        feature_columns = [
            'days_since_start', 'price_7d_ma', 'price_30d_ma', 
            'price_change', 'price_change_pct', 
            'month', 'day_of_week', 
            'price_lag_1', 'price_lag_7', 'price_lag_14', 'price_lag_30',
            'external_factor'
        ]
        
        X = self.df[feature_columns]
        y = self.df['price']
        
        return train_test_split(X, y, test_size=0.2, random_state=42)
    
    def train_models(self):
        """
        複数の機械学習モデルをトレーニング
        """
        X_train, X_test, y_train, y_test = self._prepare_features_and_target()
        
        # モデル定義
        models = {
            'ridge_regression': Pipeline([
                ('scaler', StandardScaler()),
                ('poly', PolynomialFeatures(degree=2)),
                ('regressor', Ridge(alpha=1.0))
            ]),
            'lasso_regression': Pipeline([
                ('scaler', StandardScaler()),
                ('poly', PolynomialFeatures(degree=2)),
                ('regressor', Lasso(alpha=1.0))
            ]),
            'random_forest': RandomForestRegressor(
                n_estimators=100, 
                random_state=42
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100, 
                random_state=42
            )
        }
        
        # モデルのトレーニングと評価
        results = {}
        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            results[name] = {
                'mse': mean_squared_error(y_test, y_pred),
                'mae': mean_absolute_error(y_test, y_pred),
                'r2': r2_score(y_test, y_pred)
            }
            
            # 最適なモデルを保存
            self.models[name] = model
        
        return results
    
    def predict_price(self, days_ahead: int = 30, model_name: str = 'gradient_boosting'):
        """
        指定されたモデルで将来の価格を予測
        
        Args:
            days_ahead (int): 予測する日数
            model_name (str): 使用するモデル名
        
        Returns:
            Dict: 価格予測結果
        """
        if model_name not in self.models:
            raise ValueError(f"モデル {model_name} が見つかりません")
        
        # 最新のデータポイントを基準に将来の特徴量を生成
        last_row = self.df.iloc[-1]
        future_dates = pd.date_range(
            start=last_row['date'] + timedelta(days=1), 
            periods=days_ahead
        )
        
        future_features = []
        for i, date in enumerate(future_dates):
            future_feature = {
                'days_since_start': (date - self.df['date'].min()).days,
                'price_7d_ma': last_row['price_7d_ma'],
                'price_30d_ma': last_row['price_30d_ma'],
                'price_change': last_row['price_change'],
                'price_change_pct': last_row['price_change_pct'],
                'month': date.month,
                'day_of_week': date.dayofweek,
                'price_lag_1': last_row['price'],
                'price_lag_7': last_row['price_lag_7'],
                'price_lag_14': last_row['price_lag_14'],
                'price_lag_30': last_row['price_lag_30'],
                'external_factor': np.random.normal(1, 0.1)
            }
            future_features.append(future_feature)
        
        future_df = pd.DataFrame(future_features)
        
        # モデルによる予測
        predictions = self.models[model_name].predict(future_df)
        
        return {
            'model': model_name,
            'dates': future_dates.tolist(),
            'predicted_prices': predictions.tolist()
        }
    
    def ensemble_prediction(self):
        """
        アンサンブル予測
        
        Returns:
            Dict: アンサンブル予測結果
        """
        ensemble_predictions = {}
        for model_name in self.models.keys():
            ensemble_predictions[model_name] = self.predict_price(model_name=model_name)
        
        # 各モデルの予測を平均化
        averaged_predictions = np.mean([
            pred['predicted_prices'] for pred in ensemble_predictions.values()
        ], axis=0)
        
        return {
            'ensemble_prediction': averaged_predictions.tolist(),
            'individual_predictions': ensemble_predictions
        }

def comprehensive_price_prediction(historical_data: List[Dict]) -> Dict:
    """
    価格予測の包括的な分析
    
    Args:
        historical_data (List[Dict]): 価格履歴データ
    
    Returns:
        Dict: 価格予測結果
    """
    model = AdvancedPricePredictionModel(historical_data)
    
    # モデルのトレーニング
    model_performance = model.train_models()
    
    # 価格予測
    predictions = model.ensemble_prediction()
    
    return {
        'model_performance': model_performance,
        'predictions': predictions
    }
