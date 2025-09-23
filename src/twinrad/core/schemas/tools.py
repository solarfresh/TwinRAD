from pydantic import BaseModel


class ToolConfig(BaseModel):
    pass


class GoogleSearchConfig(ToolConfig):
    google_search_engine_id: str = ''
    google_search_engine_api_key: str = ''
    google_search_engine_base_url: str = "https://customsearch.googleapis.com/customsearch/v1"


class Node2VecConfig(ToolConfig):
    """
    p: Return parameter
    q: In-out parameter
    """
    num_walks: int
    walk_length: int
    p: float
    q: float