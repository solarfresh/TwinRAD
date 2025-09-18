import json
from typing import Any, Dict

from pydantic import ValidationError

from twinrad.schemas.graphs import MindMap
from twinrad.tools.common.base_tool import BaseTool, ToolConfig


class MindMapGraphBuilder(BaseTool):
    """
    A tool that constructs and updates a MindMap graph from structured LLM output.
    It uses the schema's internal methods to handle conceptual uniqueness.
    """

    def __init__(self, config: ToolConfig):
        super().__init__(config=config)
        # The main graph object to be built
        self.graph: MindMap = MindMap()

    async def run(self, **kwargs) -> Any:
        """
        Parses LLM-generated JSON and updates the internal graph.
        """
        json_output = kwargs.get('json_output', '{}')
        if not json_output:
            return json.dumps({"status": "error", "message": "Input JSON is empty."})

        try:
            llm_data = json.loads(json_output)

            self.update_graph(llm_data)

            # Return a confirmation and a snapshot of the current graph state
            return json.dumps({"status": "success", "graph_snapshot": self.graph.model_dump_json()}, ensure_ascii=False)

        except json.JSONDecodeError as e:
            return json.dumps({"status": "error", "message": f"Failed to parse JSON: {e}"})
        except ValidationError as e:
            return json.dumps({"status": "error", "message": f"Validation error: {e}"})

    def update_graph(self, data: Dict[str, Any]) -> None:
        """
        Parses LLM output and updates the internal graph incrementally.
        """
        # Step 1: Handle the central idea
        if not data:
            return None

        self.graph.add_central_idea_data(data)

    def get_name(self) -> str:
        return "mind_map_graph_builder"

    def get_description(self) -> str:
        return "Builds a mind map graph from structured JSON output."

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "json_output": {
                    "type": "string",
                    "description": "A JSON string containing the mind map structure."
                }
            },
            "required": ["json_output"]
        }