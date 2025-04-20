from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import Product, PriceHistory
from repositories.base import BaseRepository
from core.exceptions import ProductNotFoundError

class ProductRepository(BaseRepository[Product]):
    """
    商品に関するデータベース操作を管理するリポジトリ
    """
    def create(self, product: Product) -> Product:
        """
        新しい商品を作成

        Args:
            product (Product): 作成する商品オブジェクト

        Returns:
            Product: 作成された商品
        """
        try:
            self.db.add(product)
            self.commit()
            return product
        except Exception as e:
            self.rollback()
            raise e

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        IDによる商品の取得

        Args:
            product_id (int): 取得する商品のID

        Returns:
            Optional[Product]: 見つかった商品、存在しない場合はNone
        """
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_external_id(self, external_id: str, source_site: str) -> Optional[Product]:
        """
        外部IDとソースサイトによる商品の取得

        Args:
            external_id (str): 外部商品ID
            source_site (str): ソースサイト名

        Returns:
            Optional[Product]: 見つかった商品、存在しない場合はNone
        """
        return (
            self.db.query(Product)
            .filter(
                Product.external_product_id == external_id, 
                Product.source_site == source_site
            )
            .first()
        )

    def update(self, product: Product) -> Product:
        """
        商品情報の更新

        Args:
            product (Product): 更新する商品オブジェクト

        Returns:
            Product: 更新された商品
        """
        try:
            existing_product = self.get_by_id(product.id)
            if not existing_product:
                raise ProductNotFoundError(f"ID {product.id}の商品が見つかりません")

            for key, value in product.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_product, key, value)

            self.commit()
            return existing_product
        except Exception as e:
            self.rollback()
            raise e

    def delete(self, product_id: int) -> bool:
        """
        商品の削除

        Args:
            product_id (int): 削除する商品のID

        Returns:
            bool: 削除の成功/失敗
        """
        try:
            product = self.get_by_id(product_id)
            if not product:
                raise ProductNotFoundError(f"ID {product_id}の商品が見つかりません")

            self.db.delete(product)
            self.commit()
            return True
        except Exception as e:
            self.rollback()
            return False

    def search_products(
        self, 
        query: Optional[str] = None, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None
    ) -> List[Product]:
        """
        複合的な検索条件による商品検索

        Args:
            query (Optional[str]): 検索クエリ
            min_price (Optional[float]): 最小価格
            max_price (Optional[float]): 最大価格

        Returns:
            List[Product]: 検索結果の商品リスト
        """
        search_query = self.db.query(Product)

        # 名前での検索
        if query:
            search_query = search_query.filter(
                func.lower(Product.name).like(f"%{query.lower()}%")
            )

        # 価格範囲での検索
        if min_price is not None:
            search_query = search_query.filter(Product.current_price >= min_price)
        
        if max_price is not None:
            search_query = search_query.filter(Product.current_price <= max_price)

        return search_query.all()

    def get_price_history(self, product_id: int) -> List[PriceHistory]:
        """
        特定の商品の価格履歴を取得

        Args:
            product_id (int): 価格履歴を取得する商品のID

        Returns:
            List[PriceHistory]: 価格履歴のリスト
        """
        return (
            self.db.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.recorded_at.desc())
            .all()
        )
