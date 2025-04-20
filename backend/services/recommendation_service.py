from typing import Dict, List, Any
from datetime import datetime, timedelta
from .price_utils import PriceUtils

class ProductSearchService:
    def __init__(self, data_source=None):
        """
        商品検索サービスの初期化

        Args:
            data_source: データソース (オプショナル)
        """
        self._data_source = data_source or {}
    
    def get_personalized_recommendations(
        self, 
        user_id: str, 
        search_history: List[Dict[str, Any]] = None, 
        recent_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        ユーザーに個別化された推奨商品を取得

        Args:
            user_id (str): ユーザーID
            search_history (List[Dict[str, Any]], optional): 検索履歴
            recent_days (int, optional): 過去何日間の履歴を参照するか. デフォルトは30日.

        Returns:
            List[Dict[str, Any]]: 推奨商品リスト
        """
        search_history = search_history or []
        
        if not search_history:
            return []
        
        # 最近の日付のみをフィルタリング
        cutoff_date = datetime.now() - timedelta(days=recent_days)
        recent_history = [
            item for item in search_history 
            if item.get('date', datetime.min) >= cutoff_date
        ]
        
        if not recent_history:
            return []
        
        # 最も頻繁に検索されたカテゴリやキーワードを抽出
        category_count = {}
        keyword_count = {}
        
        for item in recent_history:
            if 'category' in item:
                category_count[item['category']] = category_count.get(item['category'], 0) + 1
            
            if 'keywords' in item:
                for keyword in item['keywords']:
                    keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
        
        # 推奨項目の選択ロジック
        recommended_items = []
        
        # 最も頻繁に検索されたカテゴリから商品を推奨
        if category_count:
            top_category = max(category_count, key=category_count.get)
            # この部分は実際のデータソースに依存するため、簡単な実装
            # 本番環境では、より高度な推奨アルゴリズムを使用
            recommended_items.extend(
                self._get_items_by_category(top_category)
            )
        
        return recommended_items
    
    def _get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        カテゴリに基づいて商品を取得する内部メソッド

        Args:
            category (str): 商品カテゴリ

        Returns:
            List[Dict[str, Any]]: 推奨商品リスト
        """
        # これは単純な実装。本番環境では、データベースや外部APIと連携
        mock_recommendations = [
            {
                'id': 'mock_item_1',
                'name': f'{category}の推奨商品1',
                'price': 1000,
                'source': 'Amazon'
            },
            {
                'id': 'mock_item_2', 
                'name': f'{category}の推奨商品2',
                'price': 1500,
                'source': '楽天市場'
            }
        ]
        return mock_recommendations
