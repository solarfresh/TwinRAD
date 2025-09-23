from pydantic import BaseModel


class ToolConfig(BaseModel):
    pass


class Node2VecConfig(ToolConfig):
    """
    p: Return parameter
    q: In-out parameter
    """
    num_walks: int
    walk_length: int
    p: float
    q: float