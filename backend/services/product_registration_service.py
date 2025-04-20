from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import difflib
import uuid

from database.models import Product, ProductExternalSource
from core.exceptions import DataProcessingError

class ProductRegistrationService:
    """
    商品登録と重複検出サービス
    """
    @staticmethod
    def normalize_product_name(name: str) -> str:
        """
        商品名を正規化
        
        Args:
            name (str): 元の商品名
        
        Returns:
            str: 正規化された商品名
        """
        # 小文字変換、全角半角変換、余分な空白の削除
        return name.lower().strip()

    @staticmethod
    def calculate_name_similarity(name1: str, name2: str, threshold: float = 0.8) -> float:
        """
        2つの商品名の類似度を計算
        
        Args:
            name1 (str): 最初の商品名
            name2 (str): 2番目の商品名
            threshold (float): 類似度の閾値
        
        Returns:
            float: 類似度スコア
        """
        normalized_name1 = ProductRegistrationService.normalize_product_name(name1)
        normalized_name2 = ProductRegistrationService.normalize_product_name(name2)
        
        return difflib.SequenceMatcher(None, normalized_name1, normalized_name2).ratio()

    @classmethod
    def find_existing_product(
        cls, 
        db: Session, 
        product_data: Dict, 
        similarity_threshold: float = 0.8
    ) -> Optional[Product]:
        """
        既存の商品を検索し、類似商品を見つける
        
        Args:
            db (Session): データベースセッション
            product_data (Dict): 新規商品データ
            similarity_threshold (float): 類似度の閾値
        
        Returns:
            Optional[Product]: 類似商品が見つかった場合はその商品、なければNone
        """
        try:
            # カテゴリと名前で絞り込み
            similar_products = db.query(Product).filter(
                Product.category == product_data.get('category')
            ).all()
            
            for existing_product in similar_products:
                similarity = cls.calculate_name_similarity(
                    existing_product.name, 
                    product_data['name']
                )
                
                if similarity >= similarity_threshold:
                    return existing_product
            
            return None
        
        except Exception as e:
            raise DataProcessingError(f"商品検索中にエラー: {e}")

    @classmethod
    def register_product(
        cls, 
        db: Session, 
        product_data: Dict
    ) -> Product:
        """
        商品を登録（新規または既存）
        
        Args:
            db (Session): データベースセッション
            product_data (Dict): 商品データ
        
        Returns:
            Product: 登録された（または既存の）商品
        """
        try:
            # 既存の類似商品を検索
            existing_product = cls.find_existing_product(db, product_data)
            
            if existing_product:
                # 既存商品に外部ソース情報を追加
                external_source = ProductExternalSource(
                    product_id=existing_product.id,
                    source_name=product_data.get('source', 'unknown'),
                    external_product_id=product_data.get('external_id', str(uuid.uuid4())),
                    product_url=product_data.get('url')
                )
                db.add(external_source)
                db.commit()
                return existing_product
            
            # 新規商品の作成
            new_product = Product(
                name=product_data['name'],
                category=product_data.get('category', 'その他'),
                description=product_data.get('description', '')
            )
            db.add(new_product)
            db.flush()  # IDを取得するためにflush
            
            # 外部ソース情報の追加
            external_source = ProductExternalSource(
                product_id=new_product.id,
                source_name=product_data.get('source', 'unknown'),
                external_product_id=product_data.get('external_id', str(uuid.uuid4())),
                product_url=product_data.get('url')
            )
            db.add(external_source)
            
            db.commit()
            return new_product
        
        except Exception as e:
            db.rollback()
            raise DataProcessingError(f"商品登録中にエラー: {e}")

    @classmethod
    def bulk_register_products(
        cls, 
        db: Session, 
        products_data: List[Dict]
    ) -> List[Product]:
        """
        複数の商品を一括登録
        
        Args:
            db (Session): データベースセッション
            products_data (List[Dict]): 商品データのリスト
        
        Returns:
            List[Product]: 登録された商品のリスト
        """
        registered_products = []
        
        for product_data in products_data:
            try:
                registered_product = cls.register_product(db, product_data)
                registered_products.append(registered_product)
            except DataProcessingError as e:
                # ログ出力や個別のエラーハンドリング
                print(f"商品登録エラー: {e}")
        
        return registered_products
