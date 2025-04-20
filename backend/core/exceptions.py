class BaseAppException(Exception):
    """アプリケーション全体の基本例外"""
    pass

class ValidationError(BaseAppException):
    """バリデーション関連のエラー"""
    pass

# データベース関連
class DatabaseError(BaseAppException):
    """データベース操作中のエラー"""
    pass

class RecordNotFoundError(DatabaseError):
    """指定されたレコードが見つからない"""
    pass

class DuplicateRecordError(DatabaseError):
    """重複レコードが見つかった"""
    pass

# スクレイピング関連
class ScrapingError(BaseAppException):
    """スクレイピング処理中のエラー"""
    def __init__(self, message: str, source: str = None):
        super().__init__(message)
        self.source = source

class NetworkError(ScrapingError):
    """ネットワーク関連のエラー"""
    pass

class ParseError(ScrapingError):
    """データ解析中のエラー"""
    pass

# 認証・認可関連
class AuthenticationError(BaseAppException):
    """認証に関するエラー"""
    pass

class PermissionDeniedError(AuthenticationError):
    """権限がない操作"""
    pass

# サービス関連
class ServiceError(BaseAppException):
    """サービス層での一般的なエラー"""
    pass

class ExternalServiceError(ServiceError):
    """外部サービス呼び出し中のエラー"""
    pass

class RateLimitExceededError(ExternalServiceError):
    """APIレート制限を超過"""
    pass

# データ処理関連
class DataProcessingError(BaseAppException):
    """データ処理中のエラー"""
    pass

class InvalidDataError(DataProcessingError):
    """不正なデータ形式"""
    pass

# 価格関連
class PriceAnalysisError(BaseAppException):
    """価格分析中のエラー"""
    pass

class PriceComparisonError(PriceAnalysisError):
    """価格比較中のエラー"""
    pass

# 追加の特定のエラー
class ConfigurationError(BaseAppException):
    """設定関連のエラー"""
    pass

class ProductNotFoundError(BaseAppException):
    """商品が見つからない"""
    pass

class UserNotFoundError(BaseAppException):
    """ユーザーが見つからない"""
    pass
