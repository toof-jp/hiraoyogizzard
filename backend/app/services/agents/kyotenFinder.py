from google.cloud import discoveryengine_v1 as discoveryengine
from app.core.config import settings

class KyotenFinder:
    """Vertex AI Search を使って拠点情報を検索するクラス"""

    def __init__(self):
        self.project_id = settings.vertex_ai_project_id
        self.location = settings.vertex_ai_location
        self.data_store_id = settings.vertex_ai_data_store_id

    def search(self, search_query: str) -> discoveryengine.SearchResponse:
        """データストアを検索する"""

        # Create a client
        client = discoveryengine.SearchServiceClient()

        # The full resource name of the search engine serving config
        serving_config = client.serving_config_path(
            project=self.project_id,
            location=self.location,
            data_store=self.data_store_id,
            serving_config="default_config",
        )

        # Construct the search request
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=search_query,
            page_size=10,
        )

        # Make the search request
        response = client.search(request)

        return response
