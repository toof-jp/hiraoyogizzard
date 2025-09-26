from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List, Dict, Any
from pydantic import ValidationError

from ...models.howa import (
    GenerateHowaRequest,
    HowaResponse,
    HowaTaskStatus,
    HowaTaskStatusResponse,
    HowaTaskSubmissionResponse,
    InteractiveStepRequest,
    InteractiveStepResponse,
)
from ...services.howa_service import HowaGenerationService
from ...services.task_queue import HowaTaskQueue

router = APIRouter()

# --- ▼▼▼ 1. 依存性注入のための関数を定義 ▼▼▼ ---
# この関数により、APIが呼び出されるたびに新しいサービスインスタンスが生成され、
# 複数リクエスト間での意図しないデータ共有を防ぎます。
def get_howa_service():
    """HowaGenerationServiceのインスタンスを生成する依存関係"""
    return HowaGenerationService()


def get_task_queue(request: Request) -> HowaTaskQueue:
    queue: HowaTaskQueue | None = getattr(request.app.state, "howa_task_queue", None)
    if queue is None:
        raise HTTPException(status_code=503, detail="Task queue is not available")
    return queue

# --- ▲▲▲ ここまで ▲▲▲ ---


# --- ▼▼▼ 2. 一括生成エンドポイントの修正 ▼▼▼ ---
@router.post(
    "",
    response_model=HowaTaskSubmissionResponse,
    summary="法話生成タスクを登録する",
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_howa_task_endpoint(
    request_data: GenerateHowaRequest,
    queue: HowaTaskQueue = Depends(get_task_queue),
):
    """法話生成を非同期で実行するタスクを登録する。"""

    try:
        task_id = await queue.enqueue(request_data.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"タスクの登録に失敗しました: {exc}") from exc

    return HowaTaskSubmissionResponse(task_id=task_id, status=HowaTaskStatus.QUEUED)


@router.get(
    "/{task_id}",
    response_model=HowaTaskStatusResponse,
    summary="法話生成タスクの状態を取得する",
)
async def get_howa_task_status_endpoint(
    task_id: str,
    queue: HowaTaskQueue = Depends(get_task_queue),
):
    task = await queue.load(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="指定されたタスクは存在しません")

    howa_result: HowaResponse | None = None
    if task.result:
        try:
            howa_result = HowaResponse(**task.result)
        except ValidationError:
            # 結果が壊れていてもステータス自体は返す
            howa_result = None

    return HowaTaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        result=howa_result,
        error=task.error,
    )
# --- ▲▲▲ ここまで ▲▲▲ ---


# --- ▼▼▼ 3. 対話型エンドポイントの修正 ▼▼▼ ---
@router.post(
    "/interactive-step", 
    response_model=InteractiveStepResponse, 
    summary="【開発用】法話生成の各ステップを個別に実行"
)
async def interactive_step_endpoint(
    request: InteractiveStepRequest,
    # こちらもDependsを使ってサービスを取得
    service: HowaGenerationService = Depends(get_howa_service)
):
    """
    対話的に法話を生成するプロセスの各ステップを個別に実行します。
    開発やデバッグに使用します。
    """
    try:
        # サービスメソッドにaudiencesも渡すように修正
        result = await service.execute_interactive_step(
            step=request.step,
            theme=request.theme,
            audiences=request.audiences,
            context=request.context
        )
        return InteractiveStepResponse(
            step=request.step,
            result=result,
            message=f"Step '{request.step}' executed successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# --- ▲▲▲ ここまで ▲▲▲ ---
