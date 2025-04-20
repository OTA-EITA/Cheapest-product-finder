from functools import lru_cache
from pydantic import PostgresDsn, RedisDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

class Settings(BaseSettings):
    # データベース設定
    DATABASE_URL: PostgresDsn = 'postgresql://user:password@postgres:5432/cheapest_price_finder'
    
    # Redis設定
    REDIS_URL: RedisDsn = 'redis://redis:6379/0'
    
    # セキュリティ設定
    SECRET_KEY: str = 'your_default_secret_key'
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # スクレイピング設定
    SCRAPING_TIMEOUT: int = 10
    MAX_SCRAPING_RETRIES: int = 3
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    # ロギング設定
    LOG_LEVEL: str = "INFO"

    # サードパーティAPI設定
    EXTERNAL_API_BASE_URL: str = ""
    EXTERNAL_API_KEY: str = ""

    # Pydantic v2の設定
    model_config = SettingsConfigDict(
        # 追加のフィールドを許可
        extra='allow',
        # 環境変数からの読み込み
        env_file = ".env",
        env_file_encoding = "utf-8",
        # 大文字小文字を区別しない
        case_sensitive = False
    )

    @validator('DATABASE_URL', 'REDIS_URL', pre=True)
    def validate_url(cls, v):
        """接続URLのバリデーション"""
        if not v:
            raise ValueError("接続URLが設定されていません")
        return v

@lru_cache()
def get_settings():
    """
    設定をキャッシュし、環境変数の変更を反映
    
    Returns:
        Settings: アプリケーション設定
    """
    return Settings()

# グローバル設定インスタンス
settings = get_settings()
