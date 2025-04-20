import uuid
from sqlalchemy import (
    Column, Integer, String, Float, 
    DateTime, Boolean, ForeignKey, Text, 
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from database.base import Base

class User(Base):
    """
    ユーザーモデル
    """
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    price_alerts = relationship("PriceAlert", back_populates="user")
    search_history = relationship("SearchHistory", back_populates="user")

class Product(Base):
    """
    商品モデル
    """
    __tablename__ = 'products'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    category = Column(String)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    price_histories = relationship("PriceHistory", back_populates="product")
    price_alerts = relationship("PriceAlert", back_populates="product")
    external_sources = relationship("ProductExternalSource", back_populates="product")

class ProductExternalSource(Base):
    """
    商品の外部ソース情報
    """
    __tablename__ = 'product_external_sources'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'))
    source_name = Column(String, nullable=False)  # 'Amazon', '楽天市場' など
    external_product_id = Column(String, nullable=False)
    product_url = Column(String)
    
    # リレーションシップ
    product = relationship("Product", back_populates="external_sources")

    # 複合ユニークキー
    __table_args__ = (
        UniqueConstraint('source_name', 'external_product_id', name='_source_external_id_uc'),
    )

class PriceHistory(Base):
    """
    商品の価格履歴モデル
    """
    __tablename__ = 'price_histories'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'))
    price = Column(Float, nullable=False)
    source = Column(String)  # Amazon, 楽天など
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    product = relationship("Product", back_populates="price_histories")

class PriceAlert(Base):
    """
    価格アラートモデル
    """
    __tablename__ = 'price_alerts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'))
    target_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    user = relationship("User", back_populates="price_alerts")
    product = relationship("Product", back_populates="price_alerts")

class SearchHistory(Base):
    """
    検索履歴モデル
    """
    __tablename__ = 'search_histories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    query = Column(String, nullable=False)
    searched_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    user = relationship("User", back_populates="search_history")
