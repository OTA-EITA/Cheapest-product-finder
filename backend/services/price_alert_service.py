from typing import List, Optional
from datetime import datetime

from database.models import PriceAlert, Product, User
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository
from core.exceptions import PriceValidationError
from core.config import settings

class PriceAlertService:
    """
    価格アラート管理サービス
    """
    def __init__(
        self, 
        user_repository: UserRepository, 
        product_repository: ProductRepository
    ):
        """
        初期化メソッド

        Args:
            user_repository (UserRepository): ユーザーリポジトリ
            product_repository (ProductRepository): 商品リポジトリ
        """
        self.user_repository = user_repository
        self.product_repository = product_repository
    
    def create_price_alert(
        self, 
        user_id: int, 
        product_id: int, 
        target_price: float
    ) -> PriceAlert:
        """
        価格アラートの作成

        Args:
            user_id (int): ユーザーID
            product_id (int): 商品ID
            target_price (float): 目標価格

        Returns:
            PriceAlert: 作成された価格アラート

        Raises:
            PriceValidationError: 価格が無効な場合
        """
        # ユーザーの検証
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise PriceValidationError("ユーザーが見つかりません")

        # 商品の検証
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise PriceValidationError("商品が見つかりません")

        # 価格アラート数の制限
        active_alerts = self.user_repository.get_price_alerts(user_id)
        if len(active_alerts) >= settings.MAX_PRICE_ALERTS_PER_USER:
            raise PriceValidationError(
                f"価格アラートは{settings.MAX_PRICE_ALERTS_PER_USER}件まで設定できます"
            )

        # 価格のバリデーション
        if target_price <= 0:
            raise PriceValidationError("目標価格は0より大きい必要があります")
        
        if target_price >= product.current_price:
            raise PriceValidationError("目標価格は現在の価格より低い必要があります")

        # 価格アラートの作成
        price_alert = PriceAlert(
            user_id=user_id,
            product_id=product_id,
            target_price=target_price,
            is_active=True,
            created_at=datetime.utcnow()
        )

        # データベースに保存
        self.user_repository.db.add(price_alert)
        self.user_repository.commit()

        return price_alert
    
    def get_user_price_alerts(self, user_id: int) -> List[PriceAlert]:
        """
        ユーザーの価格アラート一覧を取得

        Args:
            user_id (int): ユーザーID

        Returns:
            List[PriceAlert]: 価格アラートのリスト
        """
        return self.user_repository.get_price_alerts(user_id)
    
    def update_price_alert(
        self, 
        alert_id: int, 
        target_price: Optional[float] = None, 
        is_active: Optional[bool] = None
    ) -> PriceAlert:
        """
        価格アラートの更新

        Args:
            alert_id (int): 価格アラートID
            target_price (Optional[float]): 新しい目標価格
            is_active (Optional[bool]): アラートの有効/無効状態

        Returns:
            PriceAlert: 更新された価格アラート

        Raises:
            PriceValidationError: 価格が無効な場合
        """
        # 価格アラートの取得
        price_alert = self.user_repository.db.query(PriceAlert).filter(
            PriceAlert.id == alert_id
        ).first()

        if not price_alert:
            raise PriceValidationError("価格アラートが見つかりません")

        # 目標価格の更新
        if target_price is not None:
            # 価格のバリデーション
            if target_price <= 0:
                raise PriceValidationError("目標価格は0より大きい必要があります")
            
            product = self.product_repository.get_by_id(price_alert.product_id)
            if target_price >= product.current_price:
                raise PriceValidationError("目標価格は現在の価格より低い必要があります")
            
            price_alert.target_price = target_price

        # アラートの有効/無効状態の更新
        if is_active is not None:
            price_alert.is_active = is_active

        # データベースに保存
        self.user_repository.commit()

        return price_alert
    
    def delete_price_alert(self, alert_id: int) -> bool:
        """
        価格アラートの削除

        Args:
            alert_id (int): 価格アラートID

        Returns:
            bool: 削除の成功/失敗
        """
        # 価格アラートの取得
        price_alert = self.user_repository.db.query(PriceAlert).filter(
            PriceAlert.id == alert_id
        ).first()

        if not price_alert:
            return False

        # データベースから削除
        self.user_repository.db.delete(price_alert)
        self.user_repository.commit()

        return True
    
    def check_price_alerts(self) -> List[PriceAlert]:
        """
        全アクティブな価格アラートをチェック

        Returns:
            List[PriceAlert]: トリガーされた価格アラート
        """
        # アクティブな価格アラートを取得
        active_alerts = self.user_repository.db.query(PriceAlert).filter(
            PriceAlert.is_active == True
        ).all()

        triggered_alerts = []

        for alert in active_alerts:
            product = self.product_repository.get_by_id(alert.product_id)
            
            # 価格がターゲット価格以下の場合
            if product.current_price <= alert.target_price:
                alert.triggered_at = datetime.utcnow()
                triggered_alerts.append(alert)
        
        # データベースに保存
        self.user_repository.commit()

        return triggered_alerts
