from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from core.config import settings
import time
from sqlalchemy.exc import SQLAlchemyError

def create_engine_with_retry(url, max_retries=5, delay=5):
    """
    データベース接続を再試行する関数
    
    Args:
        url (str): データベース接続URL
        max_retries (int): 最大再試行回数
        delay (int): 再試行間の待機時間（秒）
    
    Returns:
        Engine: SQLAlchemyエンジン
    """
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                url,
                pool_pre_ping=True,          # 接続プールの健全性をチェック
                pool_size=10,                # コネクションプールのサイズ
                max_overflow=20,             # 追加のコネクション許容数
                pool_timeout=30,             # 接続タイムアウト
            )
            # 接続テストを修正
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return engine
        except SQLAlchemyError as e:
            if attempt < max_retries - 1:
                print(f"データベース接続エラー、再試行します（{attempt + 1}/{max_retries}）: {e}")
                time.sleep(delay)
            else:
                print(f"データベース接続に失敗しました: {e}")
                raise

# データベースエンジンの作成
engine = create_engine_with_retry(str(settings.DATABASE_URL))

# セッションファクトリーの作成
SessionLocal = sessionmaker(
    autocommit=False,  # 自動コミットを無効化
    autoflush=False,   # 自動フラッシュを無効化
    bind=engine
)

# スレッドローカルセッションの作成
db_session = scoped_session(SessionLocal)

# ベースモデルの作成
Base = declarative_base()

def get_db():
    """
    データベースセッションを取得するジェネレータ関数

    Yields:
        Session: データベースセッション
    """
    db = db_session()
    try:
        yield db
    finally:
        db.close()
