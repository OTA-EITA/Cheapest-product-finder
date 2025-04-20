import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# モックデータとモデルのインポート
from sklearn.linear_model import LinearRegression

class MLModelManager:
    def __init__(self):
        """
        機械学習モデル管理クラスの初期化
        """
        self.model = None
        self.model_type = None

    def prepare_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        モデル学習のためのデータ準備

        Args:
            data (pd.DataFrame): 入力データ

        Returns:
            Dict[str, Any]: 前処理されたデータ情報
        """
        try:
            # 特徴量と目的変数の分離（モックデータ）
            X = data[['price', 'category']]
            y = data['discount_rate']

            # データの分割
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            return {
                'X_train': X_train,
                'X_test': X_test,
                'y_train': y_train,
                'y_test': y_test
            }
        except Exception as e:
            raise ValueError(f"データ準備エラー: {str(e)}")

    def train_model(self, prepared_data: Dict[str, Any], model_type: str = 'linear'):
        """
        モデルの学習

        Args:
            prepared_data (Dict[str, Any]): 準備されたデータ
            model_type (str): モデルの種類
        """
        try:
            self.model_type = model_type

            if model_type == 'linear':
                self.model = LinearRegression()
                self.model.fit(
                    prepared_data['X_train'], 
                    prepared_data['y_train']
                )
            else:
                raise ValueError(f"サポートされていないモデルタイプ: {model_type}")
        except Exception as e:
            raise ValueError(f"モデル学習エラー: {str(e)}")

def model_performance_analysis(model: MLModelManager, prepared_data: Dict[str, Any]) -> Dict[str, float]:
    """
    モデルのパフォーマンス分析

    Args:
        model (MLModelManager): モデル管理オブジェクト
        prepared_data (Dict[str, Any]): 準備されたデータ

    Returns:
        Dict[str, float]: モデルのパフォーマンス指標
    """
    try:
        y_pred = model.model.predict(prepared_data['X_test'])
        
        mse = mean_squared_error(prepared_data['y_test'], y_pred)
        r2 = r2_score(prepared_data['y_test'], y_pred)

        return {
            'mean_squared_error': mse,
            'r2_score': r2
        }
    except Exception as e:
        raise ValueError(f"モデル性能分析エラー: {str(e)}")
