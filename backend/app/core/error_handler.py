import logging
from typing import Dict, Any

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorHandler:
    """エラーハンドリングクラス"""
    
    @staticmethod
    def handle_generation_error(error: Exception) -> Dict[str, Any]:
        """法話生成エラーのハンドリング"""
        logger.error(f"法話生成エラー: {str(error)}")
        return {
            "error": "法話の生成に失敗しました",
            "detail": str(error),
            "suggestion": "テーマや対象者を変更して再試行してください"
        }
    
    @staticmethod
    def handle_validation_error(error: Exception) -> Dict[str, Any]:
        """バリデーションエラーのハンドリング"""
        logger.error(f"バリデーションエラー: {str(error)}")
        return {
            "error": "入力データが正しくありません",
            "detail": str(error),
            "suggestion": "入力内容を確認して再試行してください"
        }