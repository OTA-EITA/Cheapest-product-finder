from typing import Optional, List
from sqlalchemy.orm import Session
from core.exceptions import UserNotFoundError, ProductNotFoundError

class UserRepository:
    def __init__(self, db_session: Session):
        """
        データベースセッションの初期化

        Args:
            db_session (Session): SQLAlchemyデータベースセッション
        """
        self._db = db_session

    def get_by_username(self, username: str) -> Optional[dict]:
        """
        ユーザー名からユーザーを取得

        Args:
            username (str): ユーザー名

        Returns:
            Optional[dict]: ユーザー情報、見つからない場合はNone
        """
        # モック実装
        if username == 'test_user':
            return {
                'id': 'user1',
                'username': username,
                'email': 'test@example.com'
            }
        return None

    def get_price_alerts(self, user_id: str) -> List[dict]:
        """
        ユーザーの価格アラート一覧を取得

        Args:
            user_id (str): ユーザーID

        Returns:
            List[dict]: 価格アラートのリスト
        """
        # モック実装
        return [
            {
                'id': 'alert1',
                'user_id': user_id,
                'product_id': 'product1',
                'target_price': 900,
                'is_active': True,
                'created_at': '2024-01-01T00:00:00'
            }
        ]

    def create_price_alert(
        self, 
        user_id: str, 
        product_id: str, 
        target_price: float
    ) -> dict:
        """
        価格アラートを作成

        Args:
            user_id (str): ユーザーID
            product_id (str): 商品ID
            target_price (float): 目標価格

        Returns:
            dict: 作成された価格アラート
        """
        # モック実装
        return {
            'id': f'alert_{user_id}_{product_id}',
            'user_id': user_id,
            'product_id': product_id,
            'target_price': target_price,
            'is_active': True,
            'created_at': '2024-01-01T00:00:00'
        }
