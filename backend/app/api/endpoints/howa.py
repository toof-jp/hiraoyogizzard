from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from ...models.howa import GenerateHowaRequest, HowaResponse, InteractiveStepRequest, InteractiveStepResponse
from ...services.howa_service import HowaGenerationService

router = APIRouter()

# --- ▼▼▼ 1. 依存性注入のための関数を定義 ▼▼▼ ---
# この関数により、APIが呼び出されるたびに新しいサービスインスタンスが生成され、
# 複数リクエスト間での意図しないデータ共有を防ぎます。
def get_howa_service():
    """HowaGenerationServiceのインスタンスを生成する依存関係"""
    return HowaGenerationService()

# --- ▲▲▲ ここまで ▲▲▲ ---


# --- ▼▼▼ 2. 一括生成エンドポイントの修正 ▼▼▼ ---
@router.post(
    "", 
    response_model=HowaResponse, 
    summary="法話を一括生成する"
)
async def generate_howa_endpoint(
    request: GenerateHowaRequest,
    # Dependsを使って、リクエストごとにサービスを取得
    service: HowaGenerationService = Depends(get_howa_service)
):
    """
    テーマと対象者に基づいて、法話を一括で生成します。
    内部で経典検索、ニュース検索、執筆、評価の一連の処理を実行します。
    """
    try:
        # 新しい一括生成メソッドを呼び出す
        return await service.generate_full_howa(request)
    except Exception as e:
        # 予期せぬエラーは500エラーとして処理
        raise HTTPException(status_code=500, detail=f"サーバー内部で予期せぬエラーが発生しました: {str(e)}")
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