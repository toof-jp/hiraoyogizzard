from fastapi import APIRouter, HTTPException
from typing import List, Literal, Dict, Any
from ...models.howa import InteractiveStepRequest, InteractiveStepResponse
from ...models.howa import GenerateHowaRequest, HowaResponse
from ...services.howa_service import HowaGenerationService

router = APIRouter()

# サービスインスタンス
howa_service = HowaGenerationService()


@router.post("", response_model=HowaResponse, summary="法話の草稿を生成する")
async def generate_howa(request: GenerateHowaRequest):
    """
    法話を生成する

    - **theme**: 法話のテーマ
    - **audiences**: 対象となる聴衆の種類
    """
    try:
        # サービスを呼び出す
        return await howa_service.execute_interactive_step("create_prompts", request.theme, {})
    except HTTPException as http_exc:
        # サービス層で発生したHTTPExceptionをそのまま再発生させる
        raise http_exc
    except Exception as e:
        # 予期せぬその他のエラーは500エラーとして処理
        raise HTTPException(status_code=500, detail=f"サーバー内部で予期せぬエラーが発生しました: {str(e)}")
    
# --- ★ここから新機能のテスト用エンドポイントを追加 ---
@router.post("/interactive-step", response_model=InteractiveStepResponse, summary="【テスト用】法話生成の各ステップを個別に実行")
async def generate_howa_interactive_step(request: InteractiveStepRequest):
    """
    対話的に法話を生成するプロセスの各ステップを個別に実行します。
    単体テストやデバッグに使用します。
    """
    try:
        result = await howa_service.execute_interactive_step(request.step, request.theme, request.context)
        return InteractiveStepResponse(
            step=request.step,
            result=result,
            message=f"Step '{request.step}' executed successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))