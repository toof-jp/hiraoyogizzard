import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.howa import HowaResponse, SutraQuote  # モデルをインポート

client = TestClient(app)


def test_root_endpoint():
    """ルートエンドポイントのテスト"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["status"] == "healthy"


def test_health_check():
    """ヘルスチェックエンドポイントのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_healthz_check():
    """/healthz エンドポイントのテスト"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.text == "ok"


# 以下の2つのテストは現在の仕様にないためコメントアウト
# def test_get_themes():
#     """テーマ取得エンドポイントのテスト"""
#     response = client.get("/v1/howa/themes")
#     assert response.status_code == 200
#     data = response.json()
#     assert "themes" in data
#     assert len(data["themes"]) > 0


# def test_get_audiences():
#     """対象者取得エンドポイントのテスト"""
#     response = client.get("/v1/howa/audiences")
#     assert response.status_code == 200
#     data = response.json()
#     assert "audiences" in data
#     assert len(data["audiences"]) > 0


def test_generate_howa_success():
    """法話生成の正常ケーステスト"""
    request_data = {
        "theme": "感謝",
        "audiences": ["若者"]
    }
    response = client.post("/v1/howa", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    # レスポンスの必須フィールドをチェック
    required_fields = ["title", "introduction", "problem_statement", 
                      "sutra_quote", "modern_example", "conclusion"]
    for field in required_fields:
        assert field in data
    
    # sutra_quoteの構造をチェック
    assert "text" in data["sutra_quote"]
    assert "source" in data["sutra_quote"]


def test_generate_howa_success_with_mock(monkeypatch):
    """
    【モックテスト】法話生成が成功するケース
    GeminiServiceをモック化し、ダミーのレスポンスを返すように設定
    """
    # 1. 差し替え用のダミーレスポンスを定義
    dummy_response = HowaResponse(
        title="【モック】感謝の心",
        introduction="これはモックの導入です。",
        problem_statement="これはモックの問題提起です。",
        sutra_quote=SutraQuote(text="モックの経典引用", source="モック経"),
        modern_example="これはモックの現代例です。",
        conclusion="これがモックの結論です。"
    )

    # 2. GeminiService.generate_content を差し替える非同期関数を定義
    async def mock_generate_content(*args, **kwargs):
        return dummy_response

    # 3. monkeypatch を使って、実際のメソッドをダミー関数に差し替える
    monkeypatch.setattr(
        "app.services.gemini_service.GeminiService.generate_content",
        mock_generate_content
    )

    # 4. APIを呼び出す
    request_data = {"theme": "感謝", "audiences": ["若者"]}
    response = client.post("/v1/howa", json=request_data)

    # 5. 結果を検証
    assert response.status_code == 200
    assert response.json()["title"] == "【モック】感謝の心"


def test_generate_howa_fails_with_mock(monkeypatch):
    """
    【モックテスト】Gemini APIの呼び出しでエラーが発生するケース
    """
    # 1. 意図的に例外を発生させるダミー関数を定義
    async def mock_raise_exception(*args, **kwargs):
        raise ValueError("Gemini APIとの通信エラー")

    # 2. メソッドを差し替える
    monkeypatch.setattr(
        "app.services.gemini_service.GeminiService.generate_content",
        mock_raise_exception
    )

    # 3. APIを呼び出す
    request_data = {"theme": "感謝", "audiences": ["若者"]}
    response = client.post("/v1/howa", json=request_data)

    # 4. 503エラーが返ってくることを検証
    assert response.status_code == 503
    assert "法話の生成に失敗しました" in response.json()["detail"]


def test_generate_howa_invalid_request():
    """法話生成の異常ケーステスト"""
    # themeが空のケース
    request_data = {
        "theme": "",
        "audiences": ["若者"]
    }
    response = client.post("/v1/howa", json=request_data)
    assert response.status_code == 422
    
    # audiencesが空のケース
    request_data = {
        "theme": "感謝",
        "audiences": []
    }
    response = client.post("/v1/howa", json=request_data)
    assert response.status_code == 422


def test_interactive_step_1_create_prompts():
    """【対話テスト①】プロンプト生成ステップのテスト"""
    request_data = {
        "step": "create_prompts",
        "theme": "人生における無常について",
        "context": {}
    }
    response = client.post("/v1/howa/interactive-step", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["step"] == "create_prompts"
    assert "news_search_prompt" in data["result"]
    assert "sutra_search_prompt" in data["result"]
    assert "無常" in data["result"]["news_search_prompt"]


def test_interactive_step_2_run_news_search():
    """【対話テスト②】時事ネタ検索ステップを実行し、ニュース出力を確認する"""
    # ステップ1: まず、検索用のプロンプトを生成させる
    theme = "AIと人間の共存"
    step1_request = {
        "step": "create_prompts",
        "theme": theme,
        "context": {}
    }
    step1_response = client.post("/v1/howa/interactive-step", json=step1_request)

    # --- ★ここから修正 ---
    # もしステータスコードが200でなかった場合、エラーの詳細を出力してテストを失敗させる
    if step1_response.status_code != 200:
        print("\n--- サーバーからのエラーレスポンス ---")
        try:
            # レスポンスボディをJSONとしてパースして表示
            error_details = step1_response.json()
            print(error_details)
        except Exception:
            # JSONでパースできない場合は、テキストとして表示
            print(step1_response.text)
        print("------------------------------------")
    
    assert step1_response.status_code == 200
    # --- ★ここまで修正 ---

    step1_result = step1_response.json()["result"]
    news_search_prompt = step1_result.get("news_search_prompt")
    assert news_search_prompt is not None

    # ステップ2: ステップ1で得たプロンプトを使って、ニュース検索を実行
    step2_request = {
        "step": "run_news_search",
        "theme": theme,
        "context": {
            "news_search_prompt": news_search_prompt
        }
    }
    response = client.post("/v1/howa/interactive-step", json=step2_request)
    assert response.status_code == 200
    data = response.json()

    # --- 結果の検証 ---
    assert data["step"] == "run_news_search"
    assert "found_topics" in data["result"]
    
    found_topics = data["result"]["found_topics"]
    assert isinstance(found_topics, list)
    
    # 検索結果が空でないことを期待する (APIが正常に動作すれば何かしら見つかるはず)
    assert len(found_topics) > 0, "ニュース検索結果が空でした。APIまたはプロンプトを確認してください。"
    
    # 検索結果の各項目が文字列であることを確認
    for topic in found_topics:
        assert isinstance(topic, str)

    # テスト実行時にコンソールに出力して目視確認する
    print(f"\n--- News Search Test Results for theme '{theme}' ---")
    for i, topic in enumerate(found_topics):
        print(f"{i+1}: {topic}")
    print("--------------------------------------------------")


# --- ★ここから新しい連携テストを追加 ---
def test_interactive_step_3_chained_search():
    """【連携テスト③】経典検索の結果を元にニュース検索を行う"""
    theme = "執着を手放すこと"
    context = {}

    # 1. 最初のプロンプトを生成
    step1_req = {"step": "create_prompts", "theme": theme, "context": context}
    step1_res = client.post("/v1/howa/interactive-step", json=step1_req).json()
    assert "news_search_prompt" in step1_res["result"]
    context.update(step1_res["result"])

    # 2. 経典を検索 (ダミー)
    step2_req = {"step": "run_sutra_search", "theme": theme, "context": context}
    step2_res = client.post("/v1/howa/interactive-step", json=step2_req).json()
    assert "found_quote" in step2_res["result"]
    context.update(step2_res["result"])

    # --- ★ここからロジックを修正 ---
    # 3. 経典の情報をコンテキストに含めて、「ニュース検索」を実行させる
    #    (プロンプトの再生成は不要)
    step3_req = {"step": "run_news_search", "theme": theme, "context": context}
    step3_res = client.post("/v1/howa/interactive-step", json=step3_req)
    
    assert step3_res.status_code == 200
    step3_data = step3_res.json()

    # 4. 結果を検証
    assert "found_topics" in step3_data["result"]
    found_topics = step3_data["result"]["found_topics"]
    assert isinstance(found_topics, list)
    assert len(found_topics) > 0, "経典情報を元にしたニュース検索結果が空でした。"

    print("\n--- News Search Results (with Sutra context) ---")
    for topic in found_topics:
        print(f"- {topic}")
    print("------------------------------------------------")

@pytest.mark.e2e
def test_simple_write_howa_step():
    """
    【単体E2Eテスト】法話執筆ステップ（write_howa）のみをテストする。
    事前に用意した時事ネタと経典データを使って、法話が生成されるかだけを確認する。
    """
    print("\n--- [Simple E2E Test] Start: Testing 'write_howa' step only ---")
    
    # 1. テストに必要なデータを事前に準備
    theme = "感謝の心を持つこと"
    dummy_context = {
        "found_quote": {
            "quote": "一切の事柄は、心を前駆者とし、心を主とし、心によって作り出される。",
            "source": "法句経"
        },
        "found_topics": [
            "2025年、世界的な食糧支援活動が報じられ、多くの人々が感謝のメッセージをSNSに投稿した。"
        ]
    }

    # 2. 'write_howa'ステップを直接呼び出すリクエストを作成
    request_data = {
        "step": "write_howa",
        "theme": theme,
        "context": dummy_context
    }

    # 3. APIを呼び出し
    print("Calling API to generate howa...")
    response = client.post("/v1/howa/interactive-step", json=request_data)

    # 4. 結果を検証
    assert response.status_code == 200, f"APIがエラーを返しました: {response.text}"
    
    data = response.json()
    assert "final_howa" in data["result"], "レスポンスに'final_howa'が含まれていません。"
    
    howa_candidates = data["result"]["final_howa"]
    assert isinstance(howa_candidates, list), "生成された法話はリスト形式であるべきです。"
    assert len(howa_candidates) == 1, "1つの時事ネタから1つの法話が生成されるべきです。"
    
    generated_howa = howa_candidates[0]
    assert isinstance(generated_howa, str), "法話は文字列であるべきです。"
    assert len(generated_howa) > 50, "生成された法話が短すぎます。"

    print("\n✅ [Simple E2E Test] Successfully generated howa!")
    print("--- Generated Howa ---")
    print(generated_howa)
    print("----------------------------------------")

# --- ▼▼▼ この新しいE2Eテストをファイル末尾に追加してください ▼▼▼ ---
@pytest.mark.e2e
def test_4_e2e_full_generation_and_evaluation_flow():
    """
    【E2Eテスト④】プロンプト生成から評価まで、一連の対話ステップをすべて実行する。
    注意: このテストは実際のAPIを複数回呼び出すため、時間がかかります。
    """
    theme = "ミニマリズムと心の平穏"
    context = {}
    print(f"\n--- [E2E Test Start] Theme: {theme} ---")

    # ステップ1: プロンプト生成
    print("[Step 1: Creating Prompts]")
    step1_req = {"step": "create_prompts", "theme": theme, "context": context}
    step1_res = client.post("/v1/howa/interactive-step", json=step1_req)
    assert step1_res.status_code == 200
    context.update(step1_res.json()["result"])
    assert "news_search_prompt" in context

    # ステップ2: 経典検索 (ダミー)
    print("[Step 2: Running Sutra Search]")
    step2_req = {"step": "run_sutra_search", "theme": theme, "context": context}
    step2_res = client.post("/v1/howa/interactive-step", json=step2_req)
    assert step2_res.status_code == 200
    context.update(step2_res.json()["result"])
    assert "found_quote" in context
    print(f"  -> Sutra Found: {context['found_quote']['source']}")

    # ステップ3: ニュース検索 (★実API呼び出し)
    print("[Step 3: Running News Search]")
    step3_req = {"step": "run_news_search", "theme": theme, "context": context}
    step3_res = client.post("/v1/howa/interactive-step", json=step3_req)
    assert step3_res.status_code == 200
    context.update(step3_res.json()["result"])
    assert "found_topics" in context
    print(f"  -> Found {len(context['found_topics'])} topics.")

    # ステップ4: 法話執筆 (★実API呼び出し)
    print("[Step 4: Writing Howa Candidates]")
    step4_req = {"step": "write_howa", "theme": theme, "context": context}
    step4_res = client.post("/v1/howa/interactive-step", json=step4_req)
    assert step4_res.status_code == 200
    # 'evaluate_howa'ステップは'howa_candidates'というキーを期待するため、キー名を変更してcontextに追加
    context["howa_candidates"] = step4_res.json()["result"]["final_howa"]
    assert "howa_candidates" in context
    print(f"  -> Generated {len(context['howa_candidates'])} howa candidates.")

    # ステップ5: 法話評価 (★実API呼び出し)
    print("[Step 5: Evaluating Howa Candidates]")
    step5_req = {"step": "evaluate_howa", "theme": theme, "context": context}
    step5_res = client.post("/v1/howa/interactive-step", json=step5_req)
    assert step5_res.status_code == 200
    result_data = step5_res.json()["result"]
    
    # 最終結果を検証
    assert "best_howa" in result_data
    best_howa = result_data["best_howa"]
    assert isinstance(best_howa, str)
    assert len(best_howa) > 100, "最終的に選ばれた法話が短すぎます。"

    print("\n✅ [E2E Test] Successfully completed all steps!")
    print("--- Final Selected Howa ---")
    print(best_howa)
    print("---------------------------\n")

