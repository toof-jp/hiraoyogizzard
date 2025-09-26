from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional
from enum import Enum


class AudienceType(str, Enum):
    """対象者の種類"""
    CHILDREN = "子供"
    YOUTH = "若者"
    BUSINESS_PERSON = "ビジネスパーソン"
    ELDERLY = "高齢者"
    UNSPECIFIED = "指定なし"


class SutraQuote(BaseModel):
    """経典の引用"""
    text: str = Field(..., description="引用された経典の本文")
    source: str = Field(..., description="出典（例: 法句経 第十七章『忿怒品』）")


class GenerateHowaRequest(BaseModel):
    """法話生成リクエスト"""
    theme: str = Field(..., min_length=1, description="法話のテーマ", example="感謝")
    audiences: List[str] = Field(..., min_length=1, description="対象となる聴衆の種類", example=["若者", "ビジネスパーソン"])


class HowaResponse(BaseModel):
    """法話レスポンス"""
    title: str = Field(..., description="生成された法話の顔となるタイトル")
    introduction: str = Field(..., description="聴衆の心を引き込む、物語の始まり（時事ネタを含む）")
    problem_statement: str = Field(..., description="導入から仏教のテーマへと繋ぐ、問題提起")
    sutra_quote: SutraQuote = Field(..., description="法話の根拠となる、経典からの引用")
    modern_example: str = Field(..., description="教えを現代のシーンで解説する、具体的な例え話")
    conclusion: str = Field(..., description="聴衆が持ち帰れる、物語の締めくくりと実践のヒント")
    #candidates: List[str] = Field(..., description="[デバッグ用] 生成された法話の候補一覧")
    
class InteractiveStepRequest(BaseModel):
    """対話型APIのリクエスト"""
    step: Literal["create_prompts", "run_news_search", "run_sutra_search","write_howa", "evaluate_howa"]
    theme: str
    audiences: List[str] = Field(default=[], description="対象となる聴衆の種類", example=["若者", "ビジネスパーソン"])
    context: Dict[str, Any] = {} # 前のステップからの情報を引き継ぐためのコンテキスト

class InteractiveStepResponse(BaseModel):
    """対話型APIのレスポンス"""
    step: str
    result: Dict[str, Any]
    message: str


class HowaTaskStatus(str, Enum):
    """法話生成タスクのステータス"""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class HowaTaskSubmissionResponse(BaseModel):
    """タスク作成時のレスポンス"""

    task_id: str
    status: HowaTaskStatus


class HowaTaskStatusResponse(BaseModel):
    """タスクの現在の状態を返すレスポンス"""

    task_id: str
    status: HowaTaskStatus
    result: Optional[HowaResponse] = None
    error: Optional[str] = None
