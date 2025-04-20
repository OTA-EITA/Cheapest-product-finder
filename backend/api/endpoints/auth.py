from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from api.schemas import (
    UserCreateRequest, 
    UserLoginRequest, 
    UserResponse, 
    ErrorResponse
)
from database.base import get_db
from services.auth_service import AuthService
from repositories.user_repository import UserRepository
from database.models import User

router = APIRouter(prefix="/auth", tags=["認証"])

@router.post(
    "/signup", 
    response_model=UserResponse, 
    responses={400: {"model": ErrorResponse}}
)
def signup(
    user_data: UserCreateRequest, 
    db: Session = Depends(get_db)
):
    """
    ユーザー新規登録エンドポイント
    
    Args:
        user_data (UserCreateRequest): ユーザー登録情報
        db (Session): データベースセッション
    
    Returns:
        UserResponse: 作成されたユーザー情報
    """
    try:
        user_repo = UserRepository(db)
        
        # パスワードのハッシュ化
        hashed_password = AuthService.get_password_hash(user_data.password)
        
        # ユーザーの作成
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        # ユーザーリポジトリを通じてユーザーを保存
        created_user = user_repo.create(new_user)
        
        return UserResponse(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email
        )
    
    except ValueError as ve:
        # バリデーションエラー
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        # 予期せぬエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ユーザー登録中にエラーが発生しました"
        )

@router.post(
    "/login", 
    response_model=Dict[str, str], 
    responses={401: {"model": ErrorResponse}}
)
def login(
    login_data: UserLoginRequest, 
    db: Session = Depends(get_db)
):
    """
    ユーザーログインエンドポイント
    
    Args:
        login_data (UserLoginRequest): ログイン情報
        db (Session): データベースセッション
    
    Returns:
        Dict[str, str]: アクセストークン
    """
    user_repo = UserRepository(db)
    
    # ユーザー認証
    user = AuthService.authenticate_user(
        user_repository=user_repo, 
        username=login_data.username, 
        password=login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが間違っています",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # アクセストークンの生成
    access_token = AuthService.create_access_token(
        data={"sub": user.username}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
