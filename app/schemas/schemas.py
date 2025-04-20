from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Union
from datetime import datetime

# ユーザー関連のスキーマ
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

# 商品関連のスキーマ
class ProductBase(BaseModel):
    name: str
    source: str
    url: str
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    external_id: str

class ProductResponse(ProductBase):
    id: int
    external_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 価格関連のスキーマ
class PriceBase(BaseModel):
    price: float
    shipping_fee: Optional[float] = None
    total_price: float
    currency: str = "JPY"

class PriceCreate(PriceBase):
    product_id: int

class PriceResponse(PriceBase):
    id: int
    product_id: int
    timestamp: datetime
    
    class Config:
        orm_mode = True

# 価格履歴のスキーマ
class PriceHistoryResponse(BaseModel):
    product: ProductResponse
    prices: List[PriceResponse]
    
    class Config:
        orm_mode = True

# お気に入り関連のスキーマ
class FavoriteCreate(BaseModel):
    product_id: int

class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    product: ProductResponse
    
    class Config:
        orm_mode = True

# 検索履歴のスキーマ
class SearchHistoryCreate(BaseModel):
    query: str

class SearchHistoryResponse(BaseModel):
    id: int
    user_id: int
    query: str
    timestamp: datetime
    
    class Config:
        orm_mode = True

# 価格アラートのスキーマ
class PriceAlertBase(BaseModel):
    target_price: float

class PriceAlertCreate(PriceAlertBase):
    product_id: int

class PriceAlertResponse(PriceAlertBase):
    id: int
    user_id: int
    product_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    product: ProductResponse
    
    class Config:
        orm_mode = True

# 検索結果のスキーマ
class SearchResultItem(BaseModel):
    name: str
    url: str
    price: Optional[float] = None
    price_text: Optional[str] = None
    img_url: Optional[str] = None
    shipping: Optional[str] = None
    source: str

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    total_results: int
