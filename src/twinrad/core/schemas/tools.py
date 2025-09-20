from pydantic import BaseModel


class ToolConfig(BaseModel):
    google_search_engine_id: str = ''
    google_search_engine_api_key: str = ''
    google_search_engine_base_url: str = "https://customsearch.googleapis.com/customsearch/v1"
