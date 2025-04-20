from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from services.product_service import ProductSearchService
from services.auth_service import AuthService

router = APIRouter(prefix="/price-alerts", tags=["価格アラート"])

@router.post("/")
def create_price_alert(
    product_id: str, 
    target_price: float
):
    """
    価格アラート作成エンドポイント
    """
    try:
        # モックユーザーID（実際の実装では認証から取得）
        user_id = 'user1'
        
        # 価格アラートの作成
        return ProductSearchService.create_price_alert(
            user_id, 
            product_id, 
            target_price
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )

@router.get("/")
def get_price_alerts():
    """
    ユーザーの価格アラート一覧取得
    """
    # この実装は簡易的なモック。実際のプロジェクトでは認証と実データ取得が必要
    return [
        {
            'alert_id': 'alert1',
            'product_id': 'product1',
            'target_price': 900,
            'status': 'active'
        }
    ]
