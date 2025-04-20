from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base, DATABASE_URL
from .models import User, Product, PriceHistory, PriceAlert, SearchHistory, ScrapingLog

def create_tables():
    """
    全テーブルを作成する関数
    """
    # エンジンの作成
    engine = create_engine(DATABASE_URL)
    
    # すべてのテーブルを作成
    Base.metadata.create_all(bind=engine)
    print("データベーステーブルを作成しました。")

def drop_tables():
    """
    全テーブルを削除する関数
    """
    # エンジンの作成
    engine = create_engine(DATABASE_URL)
    
    # すべてのテーブルを削除
    Base.metadata.drop_all(bind=engine)
    print("データベーステーブルを削除しました。")

def reset_database():
    """
    データベースを完全にリセット
    """
    drop_tables()
    create_tables()

if __name__ == "__main__":
    # スクリプトとして実行された場合
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "create":
            create_tables()
        elif command == "drop":
            drop_tables()
        elif command == "reset":
            reset_database()
        else:
            print("使用法: python migrations.py [create|drop|reset]")
    else:
        print("使用法: python migrations.py [create|drop|reset]")
