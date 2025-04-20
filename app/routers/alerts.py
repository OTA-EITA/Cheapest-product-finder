from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from ..models import get_db, Product, PriceAlert, User
from ..schemas import PriceAlertCreate, PriceAlertResponse

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    responses={404: {"description": "Not found"}},
)

# ロガーの設定
logger = logging.getLogger(__name__)

@router.post("/", response_model=PriceAlertResponse)
async def create_price_alert(
    alert: PriceAlertCreate,
    user_id: int = Query(..., description="ユーザーID"),
    db: Session = Depends(get_db)
):
    """
    価格アラートを作成
    """
    # ユーザーと商品の存在チェック
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりませんでした")
    
    product = db.query(Product).filter(Product.id == alert.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品が見つかりませんでした")
    
    # 既存のアラートがあるか確認
    existing_alert = db.query(PriceAlert).filter(
        PriceAlert.user_id == user_id,
        PriceAlert.product_id == alert.product_id,
        PriceAlert.is_active == True
    ).first()
    
    # 既存のアラートがある場合は更新
    if existing_alert:
        existing_alert.target_price = alert.target_price
        db.commit()
        db.refresh(existing_alert)
        return existing_alert
    
    # 新しいアラートを作成
    db_alert = PriceAlert(
        user_id=user_id,
        product_id=alert.product_id,
        target_price=alert.target_price,
        is_active=True
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return db_alert

@router.get("/", response_model=List[PriceAlertResponse])
async def get_user_alerts(
    user_id: int = Query(..., description="ユーザーID"),
    active_only: bool = Query(True, description="アクティブなアラートのみ取得"),
    db: Session = Depends(get_db)
):
    """
    ユーザーの価格アラート一覧を取得
    """
    query = db.query(PriceAlert).filter(PriceAlert.user_id == user_id)
    
    if active_only:
        query = query.filter(PriceAlert.is_active == True)
    
    alerts = query.all()
    return alerts

@router.delete("/{alert_id}")
async def delete_price_alert(
    alert_id: int = Path(..., description="アラートID"),
    user_id: int = Query(..., description="ユーザーID"),
    db: Session = Depends(get_db)
):
    """
    価格アラートを削除（非アクティブ化）
    """
    alert = db.query(PriceAlert).filter(
        PriceAlert.id == alert_id,
        PriceAlert.user_id == user_id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="指定されたアラートが見つかりませんでした")
    
    # 論理削除（非アクティブ化）
    alert.is_active = False
    db.commit()
    
    return {"message": "アラートが非アクティブ化されました", "alert_id": alert_id}

@router.put("/{alert_id}", response_model=PriceAlertResponse)
async def update_price_alert(
    alert_id: int = Path(..., description="アラートID"),
    alert: PriceAlertCreate = None,
    user_id: int = Query(..., description="ユーザーID"),
    is_active: Optional[bool] = Query(None, description="アクティブ状態の変更"),
    db: Session = Depends(get_db)
):
    """
    価格アラートを更新
    """
    db_alert = db.query(PriceAlert).filter(
        PriceAlert.id == alert_id,
        PriceAlert.user_id == user_id
    ).first()
    
    if not db_alert:
        raise HTTPException(status_code=404, detail="指定されたアラートが見つかりませんでした")
    
    # 引数が提供されていれば更新
    if alert:
        # 商品IDが変更された場合は商品の存在チェック
        if alert.product_id != db_alert.product_id:
            product = db.query(Product).filter(Product.id == alert.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail="商品が見つかりませんでした")
            db_alert.product_id = alert.product_id
        
        db_alert.target_price = alert.target_price
    
    # アクティブ状態が指定されていれば更新
    if is_active is not None:
        db_alert.is_active = is_active
    
    db.commit()
    db.refresh(db_alert)
    
    return db_alert
