from datetime import datetime, timedelta
from typing import Optional, Dict

from passlib.context import CryptContext
from jose import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from core.config import settings
from database.models import User
from repositories.user_repository import UserRepository
from database.base import get_db
from sqlalchemy.orm import Session

class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        パスワードの検証
        """
        return AuthService.pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        パスワードのハッシュ化
        """
        return AuthService.pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(
        data: Dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        JWTアクセストークンの生成
        """
        to_encode = data.copy()
        
        # トークンの有効期限を設定
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        
        # トークンの生成
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm="HS256"
        )
        
        return encoded_jwt
    
    @classmethod
    def authenticate_user(
        cls, 
        db: Session,
        username: str, 
        password: str
    ) -> Optional[User]:
        """
        ユーザー認証
        """
        user_repo = UserRepository(db)
        user = user_repo.get_by_username(username)
        
        if not user:
            return None
        
        if not cls.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def get_current_user(
        token: str = Depends(oauth2_scheme), 
        db: Session = Depends(get_db)
    ) -> User:
        """
        トークンから現在のユーザーを取得
        """
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=["HS256"]
            )
            username: str = payload.get("sub")
            
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="トークンからユーザーを特定できません",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            user_repo = UserRepository(db)
            user = user_repo.get_by_username(username)
            
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="ユーザーが見つかりません",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            return user
        
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="トークンが無効です",
                headers={"WWW-Authenticate": "Bearer"}
            )
