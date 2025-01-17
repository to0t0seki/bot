import logging
import argparse
from typing import Optional

def setup_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """
    共通のロガー設定を提供する関数
    
    Args:
        name (str): ロガーの名前（通常は__name__）
        log_level (str, optional): ログレベル（DEBUG/INFO/WARNING/ERROR/CRITICAL）
                                  未指定の場合はコマンドライン引数から取得
    
    Returns:
        logging.Logger: 設定済みのロガーインスタンス
    """
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(add_help=False)  # メインのヘルプと競合しないように
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO'
    )
    
    # 既存の引数を解析（エラーは無視）
    try:
        args, _ = parser.parse_known_args()
    except:
        args = parser.parse_args([])  # デフォルト値を使用
    
    # ログレベルの決定（引数で指定されたものを優先）
    level = (log_level or args.log_level).upper()
    
    logger = logging.getLogger(name)
    
    # 既存のハンドラーがある場合は追加しない
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger