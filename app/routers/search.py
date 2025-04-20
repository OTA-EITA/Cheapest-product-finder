from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from ..models import get_db, SearchHistory, User
from ..schemas import SearchResponse, SearchResultItem, SearchHistoryCreate
from ...scraping import ScraperManager

router = APIRouter(
    prefix="/search",
    tags=["search"],
    responses={404: {"description": "Not found"}},
)

# ロガーの設定
logger = logging.getLogger(__name__)

# スクレイパーマネージャーのインスタンス
scraper_manager = ScraperManager()

@router.get("/", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., description="検索クエリ"),
    site: Optional[str] = Query(None, description="特定のサイトに絞り込み (amazon, rakuten, yahoo)"),
    max_results: int = Query(10, description="1サイトあたりの最大結果数"),
    user_id: Optional[int] = Query(None, description="ユーザーID（ログイン時）"),
    db: Session = Depends(get_db)
):
    """
    商品を検索し、複数サイトからの結果を返す
    """
    try:
        # ユーザーIDが提供された場合、検索履歴を保存
        if user_id:
            search_history = SearchHistoryCreate(query=q)
            db_search_history = SearchHistory(user_id=user_id, query=q)
            db.add(db_search_history)
            db.commit()
        
        # 特定のサイトが指定された場合はそのサイトのみ検索
        if site:
            results = scraper_manager.search_site(site, q, max_results)
        else:
            results = scraper_manager.search_all(q, max_results)
        
        # 結果を適切な形式に変換
        search_results = [
            SearchResultItem(
                name=result.get('name', ''),
                url=result.get('url', ''),
                price=result.get('price'),
                price_text=result.get('price_text', ''),
                img_url=result.get('img_url'),
                shipping=result.get('shipping'),
                source=result.get('source', '')
            )
            for result in results
        ]
        
        return SearchResponse(
            query=q,
            results=search_results,
            total_results=len(search_results)
        )
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"検索中にエラーが発生しました: {str(e)}")
