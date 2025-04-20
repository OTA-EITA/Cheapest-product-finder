from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    """
    汎用的なリポジトリの抽象基底クラス
    """
    def __init__(self, db: Session):
        """
        データベースセッションの初期化

        Args:
            db (Session): SQLAlchemyのセッション
        """
        self.db = db

    @abstractmethod
    def create(self, obj: T) -> T:
        """
        オブジェクトの作成

        Args:
            obj (T): 作成するオブジェクト

        Returns:
            T: 作成されたオブジェクト
        """
        pass

    @abstractmethod
    def get_by_id(self, obj_id: int) -> Optional[T]:
        """
        IDによるオブジェクトの取得

        Args:
            obj_id (int): 取得するオブジェクトのID

        Returns:
            Optional[T]: 見つかったオブジェクト、存在しない場合はNone
        """
        pass

    @abstractmethod
    def update(self, obj: T) -> T:
        """
        オブジェクトの更新

        Args:
            obj (T): 更新するオブジェクト

        Returns:
            T: 更新されたオブジェクト
        """
        pass

    @abstractmethod
    def delete(self, obj_id: int) -> bool:
        """
        オブジェクトの削除

        Args:
            obj_id (int): 削除するオブジェクトのID

        Returns:
            bool: 削除の成功/失敗
        """
        pass

    def commit(self):
        """
        データベースへの変更をコミット
        """
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def rollback(self):
        """
        データベースの変更をロールバック
        """
        self.db.rollback()
