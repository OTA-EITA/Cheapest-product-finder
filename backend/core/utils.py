import re
import unicodedata
from typing import Optional, Union
from datetime import datetime, timedelta

def normalize_text(text: str) -> str:
    """
    テキストを正規化する関数
    
    Args:
        text (str): 正規化する文字列
    
    Returns:
        str: 正規化された文字列
    """
    # 全角文字を半角に変換
    text = unicodedata.normalize('NFKC', text)
    
    # 小文字に変換
    text = text.lower()
    
    # 余分な空白を削除
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def sanitize_price(price_str: Union[str, float, int]) -> Optional[float]:
    """
    価格文字列をサニタイズし、数値に変換
    
    Args:
        price_str (Union[str, float, int]): 価格文字列または数値
    
    Returns:
        Optional[float]: サニタイズされた価格、変換不能な場合はNone
    """
    if isinstance(price_str, (int, float)):
        return float(price_str)
    
    if not isinstance(price_str, str):
        return None
    
    try:
        # 全角数字を半角に変換
        price_str = price_str.translate(str.maketrans({
            '０': '0', '１': '1', '２': '2', '３': '3', '４': '4', 
            '５': '5', '６': '6', '７': '7', '８': '8', '９': '9'
        }))
        
        # 通貨記号、カンマ、スペースを削除
        price_str = re.sub(r'[¥$,\s]', '', price_str)
        
        return float(price_str)
    except ValueError:
        return None

def generate_unique_id(prefix: str = '') -> str:
    """
    一意のID生成
    
    Args:
        prefix (str, optional): IDの接頭辞
    
    Returns:
        str: 生成された一意のID
    """
    import uuid
    
    unique_id = str(uuid.uuid4()).replace('-', '')
    return f"{prefix}{unique_id}" if prefix else unique_id

def calculate_time_difference(date1: datetime, date2: datetime) -> timedelta:
    """
    2つの日時の差を計算
    
    Args:
        date1 (datetime): 最初の日時
        date2 (datetime): 2番目の日時
    
    Returns:
        timedelta: 日時の差
    """
    return abs(date1 - date2)

def truncate_text(text: str, max_length: int = 100, ellipsis: str = '...') -> str:
    """
    テキストを指定の長さまで切り詰める
    
    Args:
        text (str): 元のテキスト
        max_length (int, optional): 最大長さ. デフォルトは100
        ellipsis (str, optional): 省略記号. デフォルトは'...'
    
    Returns:
        str: 切り詰められたテキスト
    """
    return text[:max_length] + ellipsis if len(text) > max_length else text

def validate_email(email: str) -> bool:
    """
    メールアドレスの簡易バリデーション
    
    Args:
        email (str): バリデーションするメールアドレス
    
    Returns:
        bool: 有効なメールアドレスならTrue
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """
    機密データをマスクする
    
    Args:
        data (str): マスクする文字列
        mask_char (str, optional): マスク文字. デフォルトは'*'
        visible_chars (int, optional): 表示する末尾の文字数. デフォルトは4
    
    Returns:
        str: マスクされた文字列
    """
    if len(data) <= visible_chars:
        return data
    
    return data[:-visible_chars] + (mask_char * visible_chars)
