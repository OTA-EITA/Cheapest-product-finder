import logging
import sys
from logging.handlers import RotatingFileHandler
from core.config import settings

def configure_logging():
    """
    アプリケーション全体のロギングを設定
    """
    # ルートロガーの設定
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # コンソール出力
            logging.StreamHandler(sys.stdout),
            
            # ローテーションファイルハンドラ
            RotatingFileHandler(
                filename='app.log',
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
        ]
    )

    # サードパーティライブラリのログレベル調整
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

    # アプリケーション固有のロガー
    app_logger = logging.getLogger('cheapest_price_finder')
    app_logger.setLevel(logging.INFO)

    return app_logger

# デフォルトロガーの取得
logger = configure_logging()
