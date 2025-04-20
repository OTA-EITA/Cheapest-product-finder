import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from typing import Dict, Any, Optional

class PricePredictor:
    """
    価格予測モデルのクラス
    """
    def __init__(self, model_path: str = None):
        """
        モデルの初期化
        
        Args:
            model_path (str, optional): 既存のモデルパス
        """
        self.model = None
        self.scaler = StandardScaler()
        
        # モデルパスが指定されている場合、モデルをロード
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.model = RandomForestRegressor(
                n_estimators=100, 
                random_state=42
            )
    
    def prepare_data(self, data: pd.DataFrame) -> tuple:
        """
        モデル学習のためのデータ準備
        
        Args:
            data (pd.DataFrame): 学習用データ
        
        Returns:
            tuple: 特徴量とターゲット変数
        """
        # 特徴量の選択
        features = [
            'original_price', 
            'discount_rate', 
            'days_since_last_sale', 
            'seasonal_factor'
        ]
        
        # 欠損値の処理
        data = data.dropna(subset=features + ['price'])
        
        X = data[features]
        y = data['price']
        
        return X, y
    
    def train(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        モデルの学習
        
        Args:
            data (pd.DataFrame): 学習用データ
        
        Returns:
            Dict[str, float]: モデルの性能指標
        """
        X, y = self.prepare_data(data)
        
        # データの分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 特徴量のスケーリング
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # モデルの学習
        self.model.fit(X_train_scaled, y_train)
        
        # 予測と評価
        y_pred = self.model.predict(X_test_scaled)
        
        return {
            'mae': mean_absolute_error(y_test, y_pred),
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred)
        }
    
    def predict(self, features: Dict[str, Any]) -> Optional[float]:
        """
        価格予測
        
        Args:
            features (Dict[str, Any]): 予測に使用する特徴量
        
        Returns:
            Optional[float]: 予測価格、予測不能な場合はNone
        """
        try:
            # 必要な特徴量の確認
            required_features = [
                'original_price', 
                'discount_rate', 
                'days_since_last_sale', 
                'seasonal_factor'
            ]
            
            # 特徴量の欠損チェック
            if not all(f in features for f in required_features):
                return None
            
            # 特徴量の抽出とスケーリング
            X = pd.DataFrame([features])
            X_scaled = self.scaler.transform(X)
            
            # 予測
            prediction = self.model.predict(X_scaled)[0]
            
            return float(prediction)
        
        except Exception as e:
            print(f"価格予測中のエラー: {e}")
            return None
    
    def save_model(self, path: str = 'price_predictor_model.joblib'):
        """
        モデルの保存
        
        Args:
            path (str, optional): モデル保存パス
        """
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, path)
    
    def load_model(self, path: str):
        """
        モデルのロード
        
        Args:
            path (str): モデル読み込みパス
        """
        try:
            loaded_data = joblib.load(path)
            self.model = loaded_data['model']
            self.scaler = loaded_data['scaler']
        except Exception as e:
            print(f"モデルのロードに失敗: {e}")
            # フォールバックとして新しいモデルを作成
            self.model = RandomForestRegressor(
                n_estimators=100, 
                random_state=42
            )

# モデルの使用例
def generate_sample_data() -> pd.DataFrame:
    """
    サンプルデータの生成
    
    Returns:
        pd.DataFrame: 学習用サンプルデータ
    """
    np.random.seed(42)
    n_samples = 1000
    
    return pd.DataFrame({
        'original_price': np.random.uniform(1000, 50000, n_samples),
        'discount_rate': np.random.uniform(0, 50, n_samples),
        'days_since_last_sale': np.random.randint(0, 365, n_samples),
        'seasonal_factor': np.random.uniform(0.5, 2, n_samples),
        'price': np.random.uniform(500, 45000, n_samples)
    })

# モデルの初期化と学習の実行
def initialize_price_predictor(model_path: str = None) -> PricePredictor:
    """
    価格予測モデルの初期化と学習
    
    Args:
        model_path (str, optional): 既存のモデルパス
    
    Returns:
        PricePredictor: 学習済みの価格予測モデル
    """
    # モデルの初期化
    predictor = PricePredictor(model_path)
    
    # サンプルデータの生成と学習
    sample_data = generate_sample_data()
    performance = predictor.train(sample_data)
    
    print("モデル学習結果:")
    for metric, value in performance.items():
        print(f"{metric}: {value}")
    
    # モデルの保存
    predictor.save_model('price_predictor_model.joblib')
    
    return predictor

# モデルの初期実行
if __name__ == "__main__":
    price_predictor = initialize_price_predictor()
    
    # 予測のテスト
    test_features = {
        'original_price': 30000,
        'discount_rate': 20,
        'days_since_last_sale': 60,
        'seasonal_factor': 1.2
    }
    prediction = price_predictor.predict(test_features)
    print(f"予測価格: {prediction}")
