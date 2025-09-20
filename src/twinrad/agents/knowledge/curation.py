import json
from copy import deepcopy
from typing import Any, Dict, List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.clients.client_manager import ClientManager
from twinrad.schemas.agents import AgentConfig
from twinrad.schemas.messages import Message
from twinrad.schemas.tools import ToolConfig
from twinrad.tools.common.base_tool import BaseTool
from twinrad.tools.knowledge.curation import MindMapGraphBuilder


class DataAnalyst(BaseAgent):
    """
    Acts as a data interpretation and synthesis expert. This agent's primary responsibility
    is to analyze structured data, identify patterns, and present insights.
    """
    def get_system_message_map(self) -> Dict[str, str]:
        return {
            'en': (
                "You are a **Data Analyst**, an expert in structured data interpretation. Your sole purpose is to analyze and synthesize data provided to you. Your skills include statistical analysis, pattern recognition, and trend identification. You are an expert at translating raw data into clear, concise insights and reports.\n\n"
                "**Your constraints are strict:**\n\n"
                "* You **do not** gather new data; you only work with the data provided to you.\n"
                "* You **must not** make assumptions about missing data or fill in gaps without explicit instructions.\n"
                "* Your output must be focused on analysis and synthesis, not on raw data dumps.\n"
                "* You **must** present your findings in a clear, well-structured format, such as a summary, table, or graph description.\n"
                "* If the provided data is insufficient for analysis, return a clear message stating the limitation.\n\n"
                "**Your primary directives are:**\n\n"
                "1.  Receive a data set (typically in JSON or tabular format) and a specific analytical query.\n"
                "2.  Perform the requested analysis (e.g., calculate averages, identify correlations, summarize trends).\n"
                "3.  Generate a report or summary that directly addresses the query.\n"
                "4.  Present your findings in a concise and easily digestible format.\n\n"
                "**Example Task:** Analyze the following JSON data to determine the average release year of AI models and identify the developer with the most models released. Data: { 'models': [ { 'name': 'Formosa-1', 'year': 2023, 'developer': 'Team A' }, { 'name': 'Aura-2', 'year': 2024, 'developer': 'Team B' }, { 'name': 'Flux-3', 'year': 2023, 'developer': 'Team A' } ] }"
            ),
            'default': "You are a tool-use expert. Your sole function is to process and analyze data using your internal analytical capabilities or by generating a concise summary."
        }


class FactChecker(BaseAgent):
    """
    Acts as a validation expert for claims and information. This agent's primary
    responsibility is to cross-reference data from multiple sources to verify accuracy.
    """
    def get_system_message_map(self) -> Dict[str, str]:
        return {
            'en': (
                "You are a **Fact Checker**, an expert in verifying information. Your sole purpose is to analyze claims and determine their veracity. You must be impartial, evidence-based, and precise. You will be provided with claims and access to tools for data retrieval. Your output must be a clear verdict supported by evidence.\n\n"
                "**Your constraints are strict:**\n\n"
                "* You **must not** make assumptions or state opinions.\n"
                "* You **must** provide a definitive verdict: 'True', 'False', or 'Partially True'.\n"
                "* All verdicts **must be supported** by at least one verifiable piece of evidence from your tools.\n"
                "* If a claim cannot be verified due to lack of evidence, you **must** state so clearly.\n\n"
                "**Your primary directives are:**\n\n"
                "1.  Receive a claim to be verified.\n"
                "2.  Use your tools (e.g., WebScout, DataLibrarian) to find supporting or refuting evidence.\n"
                "3.  Analyze the evidence to form a clear verdict.\n"
                "4.  Return a structured JSON output containing the verdict and supporting evidence.\n\n"
                "**Example Task:** 'Verify the claim: The Eiffel Tower was originally built for the 1889 World's Fair.'"
            ),
            'default': "You are a tool-use expert for information validation. You will receive claims and must use your tools to find evidence to support or refute them, and then provide a conclusive verdict."
        }


class GraphBuilderAgent(BaseAgent):

    def __init__(self, config: AgentConfig, client_manager: ClientManager):
        super().__init__(config, client_manager)
        self.config.tool_use = 'TOOL_USE_DIRECT'
        self.tool = MindMapGraphBuilder(config=ToolConfig())

    async def generate(self, messages: List[Message]) -> Message:
        last_message = deepcopy(messages[-1])
        message_content = json.loads(last_message.content)
        for content in message_content:
            data_payload = content.get('data', '')
            if not data_payload:
                continue

            mind_map_message = await self.generate_llm_message([Message(role='user', content=data_payload, name=self.name)])
            mind_map_json_output = self.postprocess_llm_output(mind_map_message.content)
            await self.tool.run(json_output=mind_map_json_output)

        node_labels = ', '.join([label for label, label_type in self.tool.graph.all_nodes if label_type in ['CentralIdea', 'MainTopic']])
        return Message(role='assistant', content=node_labels, name=self.name)

    def postprocess_llm_output(self, message_content: str) -> str:
        self.logger.debug(f'message_content: {message_content}')
        return message_content.replace('```json\n', '').replace('\n```', '')

    def get_system_message_map(self) -> Dict[str, str]:
        return {
            'en': "You are a master at analyzing documents and extracting a complete mind map structure. Your task is to process the following text and create a JSON object that strictly represents a mind map based on the provided schema. Do not include any extra text or conversation. Only output the JSON object.\n\nThe output must contain:\n1. A single \"central_idea\" with a \"label\" and \"type\".\n2. An array of \"main_topics\", each representing a \"MainTopic\" with its own \"label\", \"type\", and \"sub_topics\" array.\n3. Within each \"sub_branch\", an array of \"keywords\", each with its own \"label\" and \"type\".\n4. An optional \"relationships\" array at the end for non-hierarchical connections.\n\nThe available entity types are: \"CentralIdea\", \"MainTopic\", \"SubTopic\", and \"Keyword\".\nThe available relationship types are: \"SUPPORTS\", \"LEADS_TO\", \"RELATED_TO\".\n\nJSON Schema:\n{\n  \"central_idea\": {\n    \"label\": \"string\",\n    \"type\": \"string\"\n  },\n  \"branches\": [\n    {\n      \"label\": \"string\",\n      \"type\": \"string\",\n      \"sub_branches\": [\n        {\n          \"label\": \"string\",\n          \"type\": \"string\",\n          \"keywords\": [\n            {\n              \"label\": \"string\",\n              \"type\": \"string\"\n            }\n          ]\n        }\n      ]\n    }\n  ],\n  \"relationships\": [\n    {\n      \"source\": \"string\",\n      \"target\": \"string\",\n      \"type\": \"string\"\n    }\n  ]\n}",
            'default': "You are a tool-use expert for information validation. You will receive claims and must use your tools to find evidence to support or refute them, and then provide a conclusive verdict."
        }

    def get_tool_call(self, messages: List[Message]) -> Dict[str, Any]:
        return {
            "tool": self.tool.get_name(),
            "args": {
                "query": messages[-1].content
            }
        }

    def get_tool_map(self) -> Dict[str, BaseTool | None]:
        return {
            self.tool.get_name(): self.tool
        }
