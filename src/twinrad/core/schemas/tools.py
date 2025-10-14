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
    p: float = 1.0
    q: float = 1.0

    window_size: int
    embedding_dim: int
    batch_size: int
    learning_rate: float
    epochs: int
    steps_per_epoch: int | None = None