import json
from typing import Any, Dict, Optional, Set

from pydantic import ValidationError

from twinrad.schemas.graphs import (CentralIdeaNode, Edge, KeywordNode,
                                    MainTopicNode, MindMap, Node, SubTopicNode)
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
            return json.dumps({"status": "success", "graph_snapshot": self.graph.model_dump_json()})

        except json.JSONDecodeError as e:
            return json.dumps({"status": "error", "message": f"Failed to parse JSON: {e}"})
        except ValidationError as e:
            return json.dumps({"status": "error", "message": f"Validation error: {e}"})

    def update_graph(self, data: Dict[str, Any]) -> None:
        """
        Parses LLM output and updates the internal graph incrementally.
        """
        # Step 1: Handle the central idea
        central_idea_data = data.get('central_idea', {})
        if central_idea_data and not self.graph.central_idea:
            self.graph.central_idea = CentralIdeaNode(**central_idea_data)
            self.graph.add_node(self.graph.central_idea)

        # Step 2: Traverse and add branches, sub-branches, and keywords
        if self.graph.central_idea:
            for branch_data in data.get('branches', []):
                try:
                    main_topic = MainTopicNode(**branch_data)
                    self.graph.central_idea.add_main_topic(main_topic)
                    self.graph.add_node(main_topic)

                    for sub_branch_data in branch_data.get('sub_branches', []):
                        sub_topic = SubTopicNode(**sub_branch_data)
                        main_topic.add_sub_topic(sub_topic)
                        self.graph.add_node(sub_topic)

                        for keyword_data in sub_branch_data.get('keywords', []):
                            keyword = KeywordNode(**keyword_data)
                            sub_topic.add_keyword(keyword)
                            self.graph.add_node(keyword)

                except ValidationError as e:
                    self.logger.warning(f"Skipping invalid branch data: {e}")

        # Step 3: Add relationships (no change here)
        for rel_data in data.get('relationships', []):
            try:
                rel = Edge(**rel_data)
                self.graph.add_relationship(rel)
            except ValidationError as e:
                self.logger.warning(f"Skipping invalid relationship data: {e}")

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