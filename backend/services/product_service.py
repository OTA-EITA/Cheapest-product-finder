from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import String

from database.models import Product, ProductExternalSource
from api.schemas import ProductResponse

class ProductSearchService:
    @staticmethod
    def search_products(
        db: Session,
        query: str, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None, 
        category: Optional[str] = None
    ) -> List[ProductResponse]:
        """
        商品検索メソッド
        
        Args:
            db (Session): データベースセッション
            query (str): 検索クエリ
            min_price (Optional[float]): 最小価格
            max_price (Optional[float]): 最大価格
            category (Optional[str]): 商品カテゴリ
        
        Returns:
            List[ProductResponse]: 検索結果の商品リスト
        """
        # ベースクエリの構築
        base_query = db.query(Product)
        
        # 名前・カテゴリによる検索
        base_query = base_query.filter(
            or_(
                Product.name.ilike(f'%{query}%'),
                Product.category.ilike(f'%{query}%')
            )
        )
        
        # カテゴリフィルター
        if category:
            if isinstance(category, list):
                # リストの場合、最初の要素を使用
                if len(category) > 0:
                    base_query = base_query.filter(Product.category == category[0])
            else:
                # 文字列の場合
                base_query = base_query.filter(Product.category == category)
        
        # 価格が設定されている場合、価格履歴との結合が必要
        # (実際の実装では価格履歴テーブルとのJOINが必要)
        
        # 商品を取得
        products = base_query.all()
        
        # レスポンスモデルに変換
        return [
            ProductResponse(
                id=product.id,
                name=product.name,
                category=product.category,
                description=product.description,
                external_sources=[
                    {
                        'source_name': source.source_name,
                        'external_product_id': source.external_product_id,
                        'product_url': source.product_url if source.product_url and source.product_url.startswith('http') else None
                    } for source in product.external_sources
                ]
            ) for product in products
        ]
        
    @staticmethod
    def get_price_history(db: Session, product_id: str):
        """
        商品の価格履歴を取得する
        
        Args:
            db (Session): データベースセッション
            product_id (str): 商品ID
            
        Returns:
            List: 価格履歴データのリスト
        """
        # 実際の実装では、データベースから価格履歴を取得する
        # 現時点ではダミーデータを返す
        return [
            {"date": "2025-04-01", "price": 120000, "source": "Amazon"},
            {"date": "2025-04-05", "price": 118000, "source": "Amazon"},
            {"date": "2025-04-10", "price": 115000, "source": "Amazon"},
            {"date": "2025-04-15", "price": 119000, "source": "Amazon"},
            {"date": "2025-04-19", "price": 117000, "source": "Amazon"}
        ]

class ProductRecommendationService:
    @staticmethod
    def get_personalized_recommendations(db: Session, user_id: str):
        """
        ユーザー向けの商品レコメンデーションを取得する
        
        Args:
            db (Session): データベースセッション
            user_id (str): ユーザーID
            
        Returns:
            List: レコメンド商品のリスト
        """
        # 実際の実装では、ユーザーの購入履歴や閲覧履歴からレコメンドを生成
        # 現時点ではダミーデータを返す
        
        # データベースからトップの商品を取得
        products = db.query(Product).limit(3).all()
        
        return [
            {
                "id": str(product.id),
                "name": product.name,
                "category": product.category,
                "match_score": 0.85,  # マッチングスコア（ダミー）
                "reason": "過去に閲覧した商品と類似しています"
            } for product in products
        ]

def initialize_test_data(db: Session):
    """
    テスト用の商品データを初期化
    
    Args:
        db (Session): データベースセッション
    """
    # すでにデータが存在する場合は追加しない
    existing_products_count = db.query(Product).count()
    if existing_products_count > 0:
        return

    # テスト用の商品データ
    test_products = [
        {
            'name': 'iPhone 14 Pro',
            'category': 'エレクトロニクス',
            'description': '最新のiPhoneモデル',
            'external_sources': [
                {
                    'source_name': 'Amazon',
                    'external_product_id': 'B00AMAZON001',
                    'product_url': 'https://www.amazon.co.jp/dp/B00AMAZON001'
                },
                {
                    'source_name': '楽天市場',
                    'external_product_id': 'RAKUTEN001',
                    'product_url': 'https://item.rakuten.co.jp/shop/RAKUTEN001'
                }
            ]
        },
        {
            'name': 'Galaxy S23 Ultra',
            'category': 'エレクトロニクス',
            'description': '高性能Androidスマートフォン',
            'external_sources': [
                {
                    'source_name': 'Amazon',
                    'external_product_id': 'B00AMAZON002',
                    'product_url': 'https://www.amazon.co.jp/dp/B00AMAZON002'
                }
            ]
        },
        {
            'name': 'MacBook Pro 14インチ',
            'category': 'コンピューター',
            'description': '高性能ノートパソコン',
            'external_sources': [
                {
                    'source_name': 'Apple Store',
                    'external_product_id': 'APPLE001',
                    'product_url': 'https://www.apple.com/jp/shop/buy-mac/macbook-pro'
                }
            ]
        }
    ]

    from services.product_registration_service import ProductRegistrationService

    # 商品の一括登録
    ProductRegistrationService.bulk_register_products(db, test_products)
    db.commit()
