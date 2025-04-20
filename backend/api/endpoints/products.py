from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.base import get_db
from api.schemas import (
    ProductCreateRequest, 
    ProductResponse, 
    ProductSearchRequest,
    ExternalSourceCreate,
    ErrorResponse
)
from services.product_registration_service import ProductRegistrationService
from services.product_service import ProductSearchService

router = APIRouter(prefix="/products", tags=["商品"])

@router.post(
    "/", 
    response_model=ProductResponse, 
    responses={400: {"model": ErrorResponse}}
)
def create_product(
    product_data: ProductCreateRequest, 
    external_source: ExternalSourceCreate,
    db: Session = Depends(get_db)
):
    """
    新規商品の登録
    """
    try:
        # 商品データの統合
        full_product_data = {
            **product_data.dict(),
            **external_source.dict()
        }
        
        registered_product = ProductRegistrationService.register_product(
            db, 
            full_product_data
        )
        
        return registered_product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/search", 
    response_model=List[ProductResponse], 
    responses={400: {"model": ErrorResponse}}
)
def search_products(
    query: ProductSearchRequest = Depends(),
    db: Session = Depends(get_db)
):
    """
    商品検索
    """
    try:
        results = ProductSearchService.search_products(
            db,
            query.query,
            min_price=query.min_price,
            max_price=query.max_price,
            category=query.category
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
