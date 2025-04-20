from typing import Any, Optional
import redis
import json
from datetime import timedelta

from .config import settings
from .exceptions import ConfigurationError

class CacheManager:
    """
    Redisを使用したキャッシュ管理クラス
    """
    def __init__(self, redis_url: str = None):
        """
        Redisクライアントの初期化
        
        Args:
            redis_url (str, optional): Redis接続URL
        """
        try:
            self.redis_url = redis_url or 'redis://localhost:6379/0'
            self.client = redis.from_url(self.redis_url)
        except Exception as e:
            raise ConfigurationError(f"Redisの接続に失敗: {e}")
    
    def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> None:
        """
        キャッシュに値を設定
        
        Args:
            key (str): キャッシュキー
            value (Any): 保存する値
            expire (Optional[int], optional): 有効期限(秒). デフォルトは設定ファイルの値
        """
        try:
            # 値をJSON文字列に変換
            serialized_value = json.dumps(value)
            
            # 有効期限の設定
            expiration = expire or settings.CACHE_EXPIRATION_SECONDS
            
            self.client.setex(key, expiration, serialized_value)
        except Exception as e:
            # ロギングや例外処理を追加
            raise ConfigurationError(f"キャッシュの保存に失敗: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        キャッシュから値を取得
        
        Args:
            key (str): 取得するキャッシュキー
        
        Returns:
            Optional[Any]: 取得した値、存在しない場合はNone
        """
        try:
            cached_value = self.client.get(key)
            
            if cached_value:
                # JSON文字列から元の型に戻す
                return json.loads(cached_value)
            
            return None
        except Exception as e:
            # ロギングや例外処理を追加
            raise ConfigurationError(f"キャッシュの取得に失敗: {e}")
    
    def delete(self, key: str) -> None:
        """
        キャッシュから特定のキーを削除
        
        Args:
            key (str): 削除するキャッシュキー
        """
        try:
            self.client.delete(key)
        except Exception as e:
            # ロギングや例外処理を追加
            raise ConfigurationError(f"キャッシュの削除に失敗: {e}")
    
    def clear(self) -> None:
        """
        全キャッシュをクリア
        """
        try:
            self.client.flushdb()
        except Exception as e:
            # ロギングや例外処理を追加
            raise ConfigurationError(f"キャッシュのクリアに失敗: {e}")

# シングルトンインスタンスを作成
cache_manager = CacheManager()
