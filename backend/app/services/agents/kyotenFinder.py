import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from google.cloud import discoveryengine_v1 as discoveryengine
from google.protobuf.json_format import MessageToDict

from app.core.config import settings


@dataclass
class KyotenSearchRequest:
    theme: str


@dataclass
class KyotenSearchResponse:
    sutra_text: str
    source: str
    context: str
    related_themes: List[str] = field(default_factory=list)


class KyotenFinder:
    """Vertex AI Search を使って拠点情報を検索するクラス"""

    def __init__(self) -> None:
        self.project_id = settings.vertex_ai_project_id
        self.location = settings.vertex_ai_location
        self.data_store_id = settings.vertex_ai_data_store_id

    def search(self, search_query: str) -> KyotenSearchResponse:
        """データストアを検索し、KyotenSearchResponse形式で返す"""

        client = discoveryengine.SearchServiceClient()
        serving_config = client.serving_config_path(
            project=self.project_id,
            location=self.location,
            data_store=self.data_store_id,
            serving_config="default_config",
        )

        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=search_query,
            page_size=10,
        )

        response = client.search(request)
        parsed = self._parse_search_response(response, search_query)
        return parsed or self._build_fallback_response(search_query)

    async def search_sutra_placeholder(self, request: KyotenSearchRequest) -> KyotenSearchResponse:
        """スタンドアロン動作用のダミー検索。検索テーマを受け取り固定レスポンスを返す"""

        await asyncio.sleep(0)
        return self._build_fallback_response(request.theme)

    def _parse_search_response(
        self,
        response: discoveryengine.SearchResponse,
        search_query: str,
    ) -> Optional[KyotenSearchResponse]:
        for result in getattr(response, "results", []):
            document = getattr(result, "document", None)
            if not document:
                continue

            payload = self._document_to_payload(document)
            if not payload:
                continue

            return self._build_response_from_payload(payload, search_query)
        return None

    def _document_to_payload(self, document: discoveryengine.Document) -> Dict[str, Any]:
        for attr in ("struct_data", "derived_struct_data"):
            payload = self._struct_to_dict(getattr(document, attr, None))
            if payload:
                return payload

        json_data = getattr(document, "json_data", None)
        if json_data:
            try:
                parsed = json.loads(json_data)
            except json.JSONDecodeError:
                return {}
            if isinstance(parsed, dict):
                return parsed

        return {}

    def _struct_to_dict(self, struct_obj: Any) -> Dict[str, Any]:
        if struct_obj is None:
            return {}

        if isinstance(struct_obj, dict):
            return struct_obj

        try:
            return MessageToDict(struct_obj, preserving_proto_field_name=True)
        except TypeError:
            try:
                return dict(struct_obj)
            except TypeError:
                return {}

    def _build_response_from_payload(
        self,
        payload: Dict[str, Any],
        search_query: str,
    ) -> KyotenSearchResponse:
        sutra_text = self._extract_text(
            payload,
            ["sutra_text", "sutraText", "quote", "title"],
            search_query,
        )
        source = self._extract_text(
            payload,
            ["source", "sutra_source", "sutraSource", "book"],
            "",
        )
        context = self._extract_text(
            payload,
            ["context", "summary", "explanation", "description"],
            "",
        )
        related = (
            payload.get("related_themes")
            or payload.get("relatedThemes")
            or payload.get("themes")
            or payload.get("keywords")
        )
        related_themes = self._normalize_related_themes(related)

        return KyotenSearchResponse(
            sutra_text=sutra_text,
            source=source,
            context=context,
            related_themes=related_themes,
        )

    def _extract_text(self, payload: Dict[str, Any], keys: List[str], default_value: str) -> str:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str):
                stripped = value.strip()
                if stripped:
                    return stripped
            elif isinstance(value, list):
                items = [str(item).strip() for item in value if str(item).strip()]
                if items:
                    return " / ".join(items)
            elif value is not None:
                result = str(value).strip()
                if result:
                    return result
        return default_value

    def _normalize_related_themes(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]

        if isinstance(value, str):
            separators = [",", "、", "，", ";", "|", "/"]
            for sep in separators:
                if sep in value:
                    parts = value.split(sep)
                    break
            else:
                parts = [value]
            return [part.strip() for part in parts if part.strip()]

        if value is None:
            return []

        stringified = str(value).strip()
        return [stringified] if stringified else []

    def _build_fallback_response(self, search_query: Optional[str] = None) -> KyotenSearchResponse:
        return KyotenSearchResponse(
            sutra_text="一切衆生悉有仏性（いっさいしゅじょうしつうぶっしょう）",
            source="涅槃経",
            context="すべての生きとし生けるものには、等しく仏となる可能性（仏性）が備わっているという教え",
            related_themes=["慈悲", "平等", "覚醒"],
        )
