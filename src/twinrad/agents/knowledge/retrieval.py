import json
from typing import Any, Dict, List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.clients.client_manager import ClientManager
from twinrad.schemas.agents import AgentConfig
from twinrad.schemas.clients import LLMRequest, LLMResponse
from twinrad.schemas.messages import Message
from twinrad.schemas.tools import ToolConfig
from twinrad.tools.common.base_tool import BaseTool
from twinrad.tools.knowledge.retrieval import (GoogleSearchTool,
                                               PageLoaderTool, WebScrapingTool)


class DataLibrarian(BaseAgent):
    """
    Acts as the curator and manager of structured data.
    This agent's primary responsibility is to interact with internal
    and external databases, APIs, and other structured data sources
    to retrieve specific information. It's the equivalent of a librarian
    expertly navigating a large, organized archive.
    """

    def get_system_message_map(self) -> Dict[str, str]:
        return {
            'en': (
                "You are a **Data Librarian**, an expert in structured data retrieval. Your sole purpose is to access, query, and retrieve specific information from databases and APIs. You are an expert at discerning the most efficient and precise method to obtain data without engaging in conversation or creative reasoning.\n\n"
                "**Your constraints are strict:**\n\n"
                "  * You **do not** write prose, generate content, or summarize information.\n"
                "  * You **must only** return the raw, retrieved data or the direct output from your data source queries.\n"
                "  * If a query fails or no data is found, return a standardized, structured error message.\n"
                "  * Your output must be formatted as **JSON**.\n\n"
                "**Your primary directives are:**\n\n"
                "1.  Identify the correct data source (e.g., database, API) based on the user's request.\n"
                "2.  Formulate the most efficient query to retrieve the exact data requested.\n"
                "3.  Execute the query.\n"
                "4.  Return the output in the specified JSON format.\n\n"
                "**Example Task:** Retrieve the release date and the primary developer team for the \"Formosa-1\" AI model from the internal knowledge graph.\n\n"
                "**Expected Output Format:**\n\n"
                "```json\n"
                "{\n"
                "  \"request\": \"Formosa-1_details\",\n"
                "  \"status\": \"success\",\n"
                "  \"data\": {\n"
                "    \"model\": \"Formosa-1\",\n"
                "    \"release_date\": \"YYYY-MM-DD\",\n"
                "    \"developer_team\": \"team_name\"\n"
                "  }\n"
                "}\n"
                "```\n"
            ),
            'default': "You are a tool-use expert. Your only function is to select and execute the correct tool call."
        }


class QueryDecision(BaseAgent):
    """
    An expert agent that decides whether to provide a final summary or to
    generate a new search query based on the completeness of collected data.
    """

    def get_system_message_map(self) -> Dict[str, str]:
        return {
            'en': (
                "You are a specialized analysis agent. Your task is to analyze the provided search results and scraped content to determine if the user's original query has been fully answered.\n\n"
                "Your output must be one of two formats:\n"
                "1. If the information is **insufficient**, provide a new, refined search query as a simple string. For example: 'new query string here'\n"
                "2. If the information is **sufficient**, and you have a comprehensive summary, respond with a single, empty string to signal completion.\n\n"
                "Prioritize providing a full summary if possible. Only provide a new query if the data is clearly incomplete or contradictory. Do not add any extra text, explanations, or conversation."
            ),
            'default': (
                "You are an analysis agent. If the provided data is insufficient, respond with a new search query. Otherwise, respond with a single, empty string to stop."
            )
        }


class SearchAgent(BaseAgent):
    """
    Acts as an expert search agent responsible for finding relevant web pages
    based on a natural language query.
    """
    def __init__(self, config: AgentConfig, client_manager: ClientManager):
        super().__init__(config, client_manager)
        self.config.tool_use = True
        self.tool = GoogleSearchTool(config=ToolConfig(
            google_search_engine_id=self.config.google_search_engine_id,
            google_search_engine_api_key=self.config.google_search_engine_api_key,
            google_search_engine_base_url=self.config.google_search_engine_base_url,
        ))

    def get_system_message_map(self) -> Dict[str, str]:
        return {'default': "This function is not adopted."}

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


class SelectorFinder(BaseAgent):
    """
    Acts as an expert CSS selector finder. This agent's primary responsibility is to
    identify the most accurate CSS selector for a given piece of information on a webpage.
    """
    def __init__(self, config: AgentConfig, client_manager: ClientManager):
        super().__init__(config, client_manager)
        self.tool = PageLoaderTool()

    def get_tool_message_map(self) -> Dict[str, str]:
        return {
            'en': (
                "You are a tool-use agent. Your sole purpose is to determine which tool to call based on the user's request. You have access to one tool: load_page_html.\n"
                "The tool signature is: load_page_html(url: str) -> str\n"
                "The tool returns the full raw HTML content of the page as a JSON string.\n"
                "Given a request that contains a URL, your task is to call this tool to retrieve the page content.\n"
                "Your response must be a valid JSON object in the format: {\"tool\": \"load_page_html\", \"args\": {\"url\": \"your_url_here\"}}\n"
            ),
            'default': (
                "You are a tool-use expert. Your sole function is to call tools to perform web-based tasks.\n"
                "You have access to the following tool:\n"
                "load_page_html(url: str) -> str\n"
                "Your response must be a valid JSON object representing a tool call, like: {\"tool\": \"load_page_html\", \"args\": {\"url\": \"http://example.com\"}}\n"
            )
        }

    def get_system_message_map(self) -> Dict[str, str]:
        """
        System message for the second LLM call: Selector extraction.
        """
        return {
            'en': (
                "You are a specialized agent designed to find CSS selectors. Your task is to analyze the provided HTML content and identify the most specific and accurate CSS selector for the user's request.\n"
                "Your final output must be **only the CSS selector string**. Do not add any extra text, explanations, or conversation.\n"
                "If no suitable selector can be found, return 'ERROR: No suitable selector found.'\n"
            ),
            'default': (
                "Your sole purpose is to analyze the provided HTML and return a CSS selector that precisely locates the information in the user's request.\n"
                "Return only the CSS selector string. If a selector cannot be found, return 'ERROR: No suitable selector found.'\n"
            )
        }

    def get_tool_call(self, messages: List[Message]) -> Dict[str, Any]:
        return {
            "tool": self.tool.get_name(),
            "args": {
                "url": messages[-1].content
            }
        }

    def get_tool_map(self) -> Dict[str, BaseTool | None]:
        return {
            self.tool.get_name(): self.tool
        }


class URLOrchestrator(BaseAgent):
    """
    Acts as a URL management and orchestration agent. Its primary role is to
    receive a list of search result URLs, manage a cache to prevent redundant
    processing, and pass individual URLs to the next agent in the flow.
    """
    def __init__(self, config: AgentConfig, client_manager: ClientManager):
        super().__init__(config, client_manager)
        self.processed_urls = set()  # Cache to store processed URLs

    def get_system_message_map(self) -> Dict[str, str]:
        # This is a logic-based agent, so the system message is simple and informative.
        return {
            'en': "You are an orchestration agent. Your task is to manage the flow of URLs and ensure no duplicates are processed. Pass each unique URL to the next agent.",
            'default': "You are an orchestration agent."
        }

    async def generate(self, messages: List[Message]) -> Message:
        """
        Receives search results, processes them for unique URLs, and
        returns the next URL to be processed by the subsequent agent.
        """
        last_message = messages[-1]

        # Check if the message is from the SearchAgent (which provides search results)
        try:
            search_results = json.loads(last_message.content)
            original_query = messages[-2].content
            message_contents = []
            if isinstance(search_results, list):
                # Populate the pending_urls list with new, unique URLs
                for result in search_results:
                    url = result.get('url')
                    if url and url not in self.processed_urls:
                        message_contents.append({"url": url, "query": original_query})
                        self.processed_urls.add(url)

            return Message(
                role='user',
                content=json.dumps(message_contents, ensure_ascii=False),
                name=self.name
            )

        except json.JSONDecodeError:
            self.logger.error("Failed to parse search results JSON.")
            return Message(role='user', content=json.dumps({"error": "Failed to parse search results."}), name=self.name)


class WebScout(BaseAgent):
    """
    Acts as an expert web research agent. This agent's primary responsibility is to
    access, parse, and extract information from web pages using specialized tools.
    """
    def __init__(self, config: AgentConfig, client_manager: ClientManager):
        super().__init__(config, client_manager)
        self.config.tool_use = True
        self.tool = WebScrapingTool()

    def get_system_message_map(self) -> Dict[str, str]:
        return {
            'default': 'This is not adopted.'
        }

    def get_tool_call(self, messages: List[Message]) -> Dict[str, Any]:
        return {
            "tool": self.tool.get_name(),
            "args": {
                "url_contents": messages[-1].content
            }
        }

    def get_tool_map(self) -> Dict[str, BaseTool | None]:
        return {
            self.tool.get_name(): self.tool
        }
