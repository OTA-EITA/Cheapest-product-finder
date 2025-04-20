from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """ユーザーモデル"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    favorites = relationship("Favorite", back_populates="user")
    search_history = relationship("SearchHistory", back_populates="user")
    price_alerts = relationship("PriceAlert", back_populates="user")

class Product(Base):
    """商品モデル"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    external_id = Column(String(255), index=True)  # 外部サイトでの商品ID
    source = Column(String(50))  # Amazon, 楽天, Yahoo!ショッピングなど
    url = Column(String(1024))
    image_url = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    prices = relationship("Price", back_populates="product")
    favorites = relationship("Favorite", back_populates="product")
    price_alerts = relationship("PriceAlert", back_populates="product")

class Price(Base):
    """価格履歴モデル"""
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Float)
    shipping_fee = Column(Float, nullable=True)
    total_price = Column(Float)  # 商品価格 + 送料
    currency = Column(String(10), default="JPY")
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="prices")

class Favorite(Base):
    """お気に入り商品モデル"""
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorites")

class SearchHistory(Base):
    """検索履歴モデル"""
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="search_history")

class PriceAlert(Base):
    """価格アラートモデル"""
    __tablename__ = "price_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    target_price = Column(Float)  # 設定した目標価格
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="price_alerts")
    product = relationship("Product", back_populates="price_alerts")
