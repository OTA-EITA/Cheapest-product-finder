from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
import uuid

class ProductCreateRequest(BaseModel):
    """
    商品作成リクエストのスキーマ
    """
    name: str = Field(..., example="スマートフォンX", description="商品名")
    category: Optional[str] = Field(default="エレクトロニクス", example="エレクトロニクス", description="商品カテゴリ")
    description: Optional[str] = Field(default=None, example="最新のスマートフォン", description="商品説明")

class ExternalSourceCreate(BaseModel):
    """
    外部ソース情報作成のスキーマ
    """
    source_name: str = Field(..., example="Amazon", description="販売元サイト名")
    external_product_id: str = Field(..., example="B00XXXXXXX", description="外部サイトの商品ID")
    product_url: Optional[HttpUrl] = Field(default=None, example="https://amazon.co.jp/product/B00XXXXXXX", description="商品URL")

class ProductResponse(BaseModel):
    """
    商品レスポンスのスキーマ
    """
    id: uuid.UUID
    name: str
    category: Optional[str]
    description: Optional[str]
    external_sources: List[ExternalSourceCreate]

class ProductSearchRequest(BaseModel):
    """
    商品検索リクエストのスキーマ
    """
    query: str = Field(..., example="スマートフォン", description="検索クエリ")
    category: Optional[str] = Field(default=None, example="エレクトロニクス", description="商品カテゴリ")
    min_price: Optional[float] = Field(default=None, example=10000, description="最小価格")
    max_price: Optional[float] = Field(default=None, example=100000, description="最大価格")

class PriceHistoryEntry(BaseModel):
    """
    価格履歴エントリーのスキーマ
    """
    price: float = Field(..., example=89800, description="価格")
    date: datetime = Field(..., description="価格記録日時")
    source: str = Field(..., example="Amazon", description="価格情報の情報源")

class PriceAlertCreate(BaseModel):
    """
    価格アラート作成のスキーマ
    """
    product_id: uuid.UUID = Field(..., description="商品のID")
    target_price: float = Field(..., example=79800, description="アラートを設定する目標価格")

class PriceAlertResponse(BaseModel):
    """
    価格アラートレスポンスのスキーマ
    """
    id: uuid.UUID
    product_id: uuid.UUID
    target_price: float
    is_active: bool
    created_at: datetime

class ErrorResponse(BaseModel):
    """
    エラーレスポンスのスキーマ
    """
    detail: str = Field(..., example="エラーが発生しました", description="エラーの詳細")
