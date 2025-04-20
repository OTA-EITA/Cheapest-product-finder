from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.schemas import (
    PriceComparisonRequest, 
    PricePredictionRequest,
    PriceComparisonResponse,
    PricePredictionResponse,
    ErrorResponse
)
from database.base import get_db
from repositories.product_repository import ProductRepository
from services.price_comparison_service import PriceComparisonService

router = APIRouter(prefix="/price-comparison", tags=["価格比較"])

@router.post(
    "/compare", 
    response_model=PriceComparisonResponse, 
    responses={400: {"model": ErrorResponse}}
)
def compare_products(
    comparison_request: PriceComparisonRequest, 
    db: Session = Depends(get_db)
):
    """
    商品価格比較エンドポイント
    
    Args:
        comparison_request (PriceComparisonRequest): 比較する商品ID
        db (Session): データベースセッション
    
    Returns:
        PriceComparisonResponse: 価格比較結果
    """
    try:
        product_repo = ProductRepository(db)
        price_comparison_service = PriceComparisonService(product_repo)
        
        comparison_results = price_comparison_service.compare_product_prices(
            comparison_request.product_ids
        )
        
        return PriceComparisonResponse(products=comparison_results)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/predict", 
    response_model=PricePredictionResponse, 
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
def predict_product_price(
    prediction_request: PricePredictionRequest, 
    db: Session = Depends(get_db)
):
    """
    商品価格予測エンドポイント
    
    Args:
        prediction_request (PricePredictionRequest): 価格予測リクエスト
        db (Session): データベースセッション
    
    Returns:
        PricePredictionResponse: 価格予測結果
    """
    try:
        product_repo = ProductRepository(db)
        price_comparison_service = PriceComparisonService(product_repo)
        
        prediction_result = price_comparison_service.predict_future_price(
            product_id=prediction_request.product_id,
            prediction_days=prediction_request.prediction_days
        )
        
        if 'error' in prediction_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=prediction_result['error']
            )
        
        return PricePredictionResponse(
            current_price=prediction_result['current_price'],
            predicted_price=prediction_result.get('predicted_price'),
            prediction_days=prediction_result['prediction_days']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
