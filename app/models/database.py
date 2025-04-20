from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# AzureのCosmosDB接続文字列を取得する（ローカル開発環境ではSQLiteを使用）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cheapest_price_finder.db")

# SQLAlchemyエンジンの作成
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデル定義の基底クラス
Base = declarative_base()

# DBセッションを提供する依存関係用の関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
