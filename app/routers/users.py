from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from passlib.context import CryptContext
from ..models import get_db, User, SearchHistory
from ..schemas import UserCreate, UserResponse, SearchHistoryResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# ロガーの設定
logger = logging.getLogger(__name__)

# パスワードハッシュ化のためのコンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    新しいユーザーを作成
    """
    # メールアドレスの重複チェック
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="このメールアドレスは既に使用されています")
    
    # パスワードのハッシュ化
    hashed_password = pwd_context.hash(user.password)
    
    # ユーザーの作成
    db_user = User(
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int = Path(..., description="ユーザーID"),
    db: Session = Depends(get_db)
):
    """
    ユーザー情報を取得
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりませんでした")
    return user

@router.get("/{user_id}/search-history", response_model=List[SearchHistoryResponse])
async def get_search_history(
    user_id: int = Path(..., description="ユーザーID"),
    limit: int = Query(10, description="取得する履歴の数"),
    db: Session = Depends(get_db)
):
    """
    ユーザーの検索履歴を取得
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりませんでした")
    
    # 最新の検索履歴を取得
    histories = db.query(SearchHistory).filter(
        SearchHistory.user_id == user_id
    ).order_by(SearchHistory.timestamp.desc()).limit(limit).all()
    
    return histories

@router.delete("/{user_id}")
async def delete_user(
    user_id: int = Path(..., description="ユーザーID"),
    db: Session = Depends(get_db)
):
    """
    ユーザーを削除（非アクティブ化）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりませんでした")
    
    # 論理削除（非アクティブ化）
    user.is_active = False
    db.commit()
    
    return {"message": "ユーザーが非アクティブ化されました", "user_id": user_id}

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int = Path(..., description="ユーザーID"),
    user: Optional[UserCreate] = None,
    is_active: Optional[bool] = Query(None, description="アクティブ状態の変更"),
    db: Session = Depends(get_db)
):
    """
    ユーザー情報を更新
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりませんでした")
    
    # 引数が提供されていれば更新
    if user:
        # メールアドレスが変更される場合は重複チェック
        if user.email != db_user.email:
            existing_user = db.query(User).filter(User.email == user.email).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="このメールアドレスは既に使用されています")
            db_user.email = user.email
        
        # パスワードが提供されていれば更新
        if user.password:
            db_user.hashed_password = pwd_context.hash(user.password)
    
    # アクティブ状態が指定されていれば更新
    if is_active is not None:
        db_user.is_active = is_active
    
    db.commit()
    db.refresh(db_user)
    
    return db_user
