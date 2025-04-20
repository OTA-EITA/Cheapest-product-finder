import logging
import structlog
from typing import Any, Dict

def configure_logging() -> structlog.BoundLogger:
    """
    構造化ロギングを設定する関数
    
    Returns:
        structlog.BoundLogger: 設定されたロガー
    """
    # 標準のpythonロギング設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # structlogの設定
    structlog.configure(
        processors=[
            # 辞書から文字列への変換
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # コンソール出力用のレンダラー
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # structlogのインスタンスを作成
    logger = structlog.get_logger()
    
    return logger

def log_action(
    logger: structlog.BoundLogger, 
    action: str, 
    details: Dict[str, Any] = None, 
    level: str = 'info'
) -> None:
    """
    構造化されたログを記録する関数
    
    Args:
        logger (structlog.BoundLogger): ロガーインスタンス
        action (str): 実行されたアクション
        details (Dict[str, Any], optional): アクションの詳細情報
        level (str, optional): ログレベル. デフォルトは'info'
    """
    log_method = getattr(logger, level)
    
    log_data = {'action': action}
    if details:
        log_data.update(details)
    
    log_method(action, **log_data)
