import json
from typing import Dict, List

from twinrad.agents.common.base_agent import BaseAgent
from twinrad.clients.client_manager import ClientManager
from twinrad.schemas.agents import AgentConfig
from twinrad.schemas.clients import LLMRequest, LLMResponse
from twinrad.schemas.messages import Message
from twinrad.tools.knowledge.retrieval import PageLoaderTool, WebScrapingTool


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
            'gemini': (
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


class SelectorFinder(BaseAgent):
    """
    Acts as an expert CSS selector finder. This agent's primary responsibility is to
    identify the most accurate CSS selector for a given piece of information on a webpage.
    """
    def __init__(self, config: AgentConfig, client_manager: ClientManager):
        super().__init__(config, client_manager)
        self.tool = PageLoaderTool()

    def get_system_message_map(self) -> Dict[str, str]:
        return {
            'gemini': (
                "You are a tool-use agent. Your sole purpose is to determine which tool to call based on the user's request. You have access to one tool: load_page_html.\n"
                "The tool signature is: load_page_html(url: str) -> str\n"
                "The tool returns the full raw HTML content of the page as a JSON string.\n"
                "Given a request that contains a URL, your task is to call this tool to retrieve the page content.\n"
                "Your response must be a valid JSON object in the format: {\"tool\": \"load_page_html\", \"args\": {\"url\": \"your_url_here\"}}\n"
            ),
            # Add other model families here
            'default': (
                "You are a tool-use expert. Your sole function is to call tools to perform web-based tasks.\n"
                "You have access to the following tool:\n"
                "load_page_html(url: str) -> str\n"
                "Your response must be a valid JSON object representing a tool call, like: {\"tool\": \"load_page_html\", \"args\": {\"url\": \"http://example.com\"}}\n"
            )
        }

    async def generate(self, messages: List[Message]) -> Message:
        """
        Processes a user request to find a CSS selector.

        This agent uses its LLM to decide when to call the PageLoaderTool
        and then to reason about the HTML to find the correct selector.
        """
        # Step 1: LLM determines if it needs to call the tool
        # The LLM's role is to parse the user's input and generate a tool call
        original_query = messages[-1].content
        request = LLMRequest(
            model=self.model,
            messages=messages,
            system_message=self.system_message,
        )
        response: LLMResponse = await self.client_manager.generate(request)

        self.logger.info(f'LLM response: {response.text}')
        # Step 2: Check if the LLM output is a tool call
        try:
            tool_call = json.loads(response.text.replace('```json', '').replace('```', '').strip())
            self.logger.debug(f'tool_call: {tool_call}')
            if tool_call.get("tool") != self.tool.get_name():
                raise ValueError("LLM generated an invalid tool call.")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.warning(f"Failed to get a valid tool call. Assuming LLM's first response is final: {e}")
            return Message(role='user', content=response.text, name=self.name)

        # Step 3: Execute the PageLoaderTool to get the HTML
        tool_output_json_string  = await self.tool.run(**tool_call.get("args", {}))

        try:
            tool_output_dict = json.loads(tool_output_json_string)
            if "error" in tool_output_dict:
                self.logger.warning("Tool execution failed, returning error to user.")
                return Message(role='user', content=tool_output_json_string, name=self.name)
            html_content = tool_output_dict.get("html_content", "")
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse tool output, returning error to user.")
            return Message(role='user', content=json.dumps({"error": "Failed to parse tool output."}), name=self.name)

        # Step 4: Use the LLM again to extract the CSS selector from the HTML
        extraction_messages = [
            Message(role='user', content=original_query, name=self.name),
            Message(role='tool', content=json.dumps({"html_content": html_content}), name=self.tool.get_name())
        ]

        final_request = LLMRequest(
            model=self.model,
            messages=extraction_messages,
            system_message=self._get_extraction_prompt(),
        )
        final_response: LLMResponse = await self.client_manager.generate(final_request)
        final_output = {
            "html_content": html_content,
            "query": final_response.text.strip(),  # The final selector
        }

        return Message(role='user', content=json.dumps(final_output), name=self.name)

    def _get_extraction_prompt(self) -> str:
        """
        System message for the second LLM call: Selector extraction.
        """
        model = self.config.model
        prompt_map = {
            'gemini': (
                "You are a specialized agent designed to find CSS selectors. Your task is to analyze the provided HTML content and identify the most specific and accurate CSS selector for the user's request.\n"
                "Your final output must be **only the CSS selector string**. Do not add any extra text, explanations, or conversation.\n"
                "If no suitable selector can be found, return 'ERROR: No suitable selector found.'\n"
            ),
            'default': (
                "Your sole purpose is to analyze the provided HTML and return a CSS selector that precisely locates the information in the user's request.\n"
                "Return only the CSS selector string. If a selector cannot be found, return 'ERROR: No suitable selector found.'\n"
            )
        }

        # Check if the model name contains a key from the prompt map
        for key, prompt_content in prompt_map.items():
            if key in model.lower():
                return prompt_content

        # Fallback if no specific model or family is matched
        return prompt_map['default']


class WebScout(BaseAgent):
    """
    Acts as an expert web research agent. This agent's primary responsibility is to
    access, parse, and extract information from web pages using specialized tools.
    """
    def __init__(self, config: AgentConfig, client_manager: ClientManager):
        super().__init__(config, client_manager)
        self.tool = WebScrapingTool()

    def get_system_message_map(self) -> Dict[str, str]:
        return {
            'gemini': (
                "You are a specialized data extraction agent. Your sole function is to scrape data from provided HTML content using a given CSS selector.\n"
                "You have access to a single tool, `scrape_web_data(html_content: str, query: str)`.\n"
                "Your job is pure execution. When given HTML content and a CSS selector, you must call the tool and return the result.\n"
                "Your response must be a valid JSON object in the format: {\"tool\": \"scrape_web_data\", \"args\": {\"html_content\": \"html_here\", \"query\": \"selector_here\"}}\n"
            ),
            'default': (
                "You are a tool-use expert. Your sole function is to call the `scrape_web_data(html_content: str, query: str)` tool.\n"
                "Your response must be a valid JSON object representing a tool call, like: {\"tool\": \"scrape_web_data\", \"args\": {\"html_content\": \"...\", \"query\": \".selector\"}}\n"
            )
        }

    async def generate(self, messages: List[Message]) -> Message:
        """
        Processes a request to scrape data using a provided HTML and CSS selector.
        """
        # Step 1: The LLM's role is to parse the input and generate a tool call
        latest_message = messages[-1]

        try:
            # The input from the SelectorFinder is a JSON string
            input_data = json.loads(latest_message.content)
            html_content = input_data.get("html_content")
            query = input_data.get("query")

            if not html_content or not query:
                return Message(role='user', content=json.dumps({"error": "Missing html_content or query in input."}), name=self.name)
        except json.JSONDecodeError:
            return Message(role='user', content=json.dumps({"error": "Invalid JSON input."}), name=self.name)

        # Step 2: Directly call the tool with the parsed arguments
        # The agent's LLM is no longer used for this step. The agent acts as a pure executor.
        results = {
            "html_content": html_content,
            "query": query
        }

        try:
            content = await self.tool.run(**results)
            return Message(role='user', content=content, name=self.name)
        except Exception as e:
            self.logger.error(f"WebScrapingTool execution failed: {e}")
            return Message(role='user', content=json.dumps({"error": f"Tool execution failed: {e}"}), name=self.name)