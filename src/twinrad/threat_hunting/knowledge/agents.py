import json
import re
from copy import deepcopy
from typing import Any, Dict, List

from twinrad.core.agents.base_agent import BaseAgent
from twinrad.core.clients.client_manager import ClientManager
from twinrad.core.schemas.agents import AgentConfig
from twinrad.core.schemas.messages import Message
from twinrad.threat_hunting.knowledge import tools
from twinrad.threat_hunting.knowledge.schemas import (GoogleSearchAgentConfig,
                                                      GoogleSearchToolConfig,
                                                      ToolConfig)
from twinrad.threat_hunting.knowledge.tools import BaseTool


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
        self.max_prompt_length = 30000
        self.tool = tools.MindMapGraphBuilder(config=ToolConfig())

    async def generate(self, messages: List[Message]) -> Message:
        last_message = deepcopy(messages[-1])
        message_content = json.loads(last_message.content)
        data_payloads = []
        for content in message_content:
            data_payload = content.get('data', '')
            if not data_payload:
                continue

            data_payloads += self._split_data_payload(data_payload)

        for data_payload in data_payloads:
            mind_map_message = await self.generate_llm_message([Message(role='user', content=data_payload, name=self.name)])
            mind_map_json_output = self.postprocess_llm_output(mind_map_message.content)
            await self.tool.run(json_output=mind_map_json_output)

        node_labels = ', '.join([label for label, label_type in self.tool.graph.all_nodes if label_type in ['CentralIdea', 'MainTopic']])
        return Message(role='assistant', content=node_labels, name=self.name)

    def _split_data_payload(self, data_payload: str) -> List[str]:
        """
        Splits a data payload string into a list of smaller strings,
        each not exceeding self.max_prompt_length, while preserving line breaks.
        """
        lines  = data_payload.split('\n')
        chunks: List[str] = []
        current_chunk  = ''
        current_length  = 0

        for line in lines:
            line_with_newline = line + '\n'
            line_length = len(line_with_newline)

            if current_length + line_length > self.max_prompt_length and current_chunk:
                chunks.append(current_chunk)
                current_chunk = line_with_newline
                current_length = line_length
            else:
                current_chunk += line_with_newline
                current_length += line_length

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

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


class KnowledgeEngineer(BaseAgent):
    """
    Acts as the architect and builder of the knowledge graph. This agent synthesizes
    structured data into a coherent graph, ensuring semantic integrity and connectivity.
    """
    def get_system_message_map(self) -> Dict[str, str]:
        return {
            'gemini': (
                "You are a **Knowledge Engineer**, a master of semantic modeling and knowledge graph construction. Your purpose is to take structured data, verified facts, and analytical insights and transform them into a coherent and interconnected graph representation. You must think in terms of entities (nodes) and their relationships (edges).\n\n"
                "**Your constraints are strict:**\n\n"
                "* Your output **must** be a series of graph operations (e.g., Cypher queries for Neo4j) or a structured JSON object representing nodes and relationships.\n"
                "* You **do not** write reports, summaries, or provide commentary. Your output is code or structured data for graph ingestion.\n"
                "* You **must** adhere to predefined schemas for nodes and relationships. If data does not fit, it should be ignored or flagged.\n\n"
                "**Your primary directives are:**\n\n"
                "1.  Receive structured data (e.g., from a DataLibrarian or FactChecker).\n"
                "2.  Identify the core entities and their properties from the data.\n"
                "3.  Determine the semantic relationships between these entities.\n"
                "4.  Generate the necessary code or data structure to create or update the graph.\n\n"
                "**Example Task:** 'Ingest the following JSON data into the knowledge graph. Data: { 'model': 'Formosa-1', 'developer_team': 'Team A', 'release_year': 2023 }'"
            ),
            'default': "You are a tool-use expert. Your sole function is to process structured information and generate the appropriate data schema or code to represent it as a knowledge graph."
        }


class QueryDecision(BaseAgent):
    """
    An expert agent that decides whether to provide a final summary or to
    generate a new search query based on the completeness of collected data.
    """

    def get_system_message_map(self) -> Dict[str, str]:
        return {
            'en': "You are a specialized AI assistant designed to analyze a collection of topics and generate an effective search query for a Google-like search engine. Your core function is to identify the relationships, missing information, and key entities within a given set of terms. Your output should be a well-structured list of queries that, when executed, will help a human user quickly and comprehensively find the interconnected information.\n\nYour tasks are:\n\n1.  **Categorize Topics:** Group the provided terms into logical themes (e.g., organizations, projects, use cases, technical details).\n2.  **Identify Connections:** Analyze how different topics might relate to each other. Look for partnerships, dependencies, or comparative relationships.\n3.  **Formulate Queries:** Based on your analysis, create a list of five highly specific keywords or a short sentence. Each query should be designed to uncover the \"missing parts\" that link the provided topics together.\n4.  **Structure the Output:** Present the queries in a clear, categorized list. Use headings and bullet points to make the output easy to read and use.\n\nYour final output must be a **single** search query, not a summary or analysis of the content itself. Your sole purpose is to provide the user with the tools to perform their own information synthesis.",
            'default': "You are a specialized AI assistant designed to analyze a collection of topics and generate an effective search query for a Google-like search engine. Your core function is to identify the relationships, missing information, and key entities within a given set of terms. Your output should be a well-structured list of queries that, when executed, will help a human user quickly and comprehensively find the interconnected information.\n\nYour tasks are:\n\n1.  **Categorize Topics:** Group the provided terms into logical themes (e.g., organizations, projects, use cases, technical details).\n2.  **Identify Connections:** Analyze how different topics might relate to each other. Look for partnerships, dependencies, or comparative relationships.\n3.  **Formulate Queries:** Based on your analysis, create a list of five highly specific keywords or a short sentence. Each query should be designed to uncover the \"missing parts\" that link the provided topics together.\n4.  **Structure the Output:** Present the queries in a clear, categorized list. Use headings and bullet points to make the output easy to read and use.\n\nYour final output must be a **single** search query, not a summary or analysis of the content itself. Your sole purpose is to provide the user with the tools to perform their own information synthesis."
        }

    def get_cot_message_map(self) -> Dict[str, str]:
        return {
            "en": "You are a specialized AI assistant that synthesizes information to generate a single, comprehensive Google search query. Your output must be a JSON object.\n\nBased on the topics above, provide a single, comprehensive Google search query that connects them all together. The query should be designed to find the relationships and missing context between the different projects and organizations.\n\nOutput format:\n{\n  \"google_query\": \"your comprehensive search query here\"\n}",
            "default": "You are a specialized AI assistant that synthesizes information to generate a single, comprehensive Google search query. Your output must be a JSON object.\n\nBased on the topics above, provide a single, comprehensive Google search query that connects them all together. The query should be designed to find the relationships and missing context between the different projects and organizations.\n\nOutput format:\n{\n  \"google_query\": \"your comprehensive search query here\"\n}"
        }

    def postprocess_llm_output(self, output_string: str) -> str:
        self.logger.info("Postprocessing LLM output for query extraction.")
        self.logger.debug(f"Raw LLM output: {output_string}")
        pattern = r"\"google_query\":\s*\"(.*?)\""
        latest_match_object = None
        for match in re.finditer(pattern, output_string):
            latest_match_object = match

        if latest_match_object:
            return latest_match_object.group(1)
        else:
            return ''


class ReportAnalyst(BaseAgent):
    """
    Acts as a comprehension and summarization expert. This agent's primary
    responsibility is to read and analyze detailed reports to extract key
    information, summaries, and actionable insights.
    """
    def get_system_message_map(self) -> Dict[str, str]:
        return {
            'en': (
                "You are a **Report Analyst**, an expert in document comprehension and summarization. Your sole purpose is to read detailed reports and provide concise, accurate summaries or direct answers to specific questions based *only* on the provided text. You must be precise and neutral in your analysis. Your output should be structured to deliver maximum information with minimum redundancy.\n\n"
                "**Your constraints are strict:**\n\n"
                "* You **must not** add any information not explicitly present in the source report.\n"
                "* You **do not** offer opinions, conclusions, or speculative analysis.\n"
                "* Your responses must be structured and easy to read (e.g., bullet points, short paragraphs).\n"
                "* If a requested piece of information is not found, you **must** state this clearly.\n\n"
                "**Your primary directives are:**\n\n"
                "1.  Receive a detailed report (as a single block of text).\n"
                "2.  Identify the main purpose and key findings of the report.\n"
                "3.  Condense the report into a brief, easy-to-understand summary.\n"
                "4.  If a specific question is asked, find and provide the direct answer from the text.\n\n"
                "**Example Task:** 'Read the following research abstract and summarize the main conclusion. Abstract: [Insert a long abstract here...]' "
            ),
            'default': "You are a comprehension expert. Your sole function is to process and summarize complex documents and reports and extract specific information from them."
        }


class SearchAgent(BaseAgent):
    """
    Acts as an expert search agent responsible for finding relevant web pages
    based on a natural language query.
    """
    def __init__(self, config: GoogleSearchAgentConfig, client_manager: ClientManager):
        super().__init__(config, client_manager)
        self.config.tool_use = 'TOOL_USE_DIRECT'
        self.tool = tools.GoogleSearchTool(config=GoogleSearchToolConfig(
            google_search_engine_id=config.google_search_engine_id,
            google_search_engine_api_key=config.google_search_engine_api_key,
            google_search_engine_base_url=config.google_search_engine_base_url,
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
        self.config.tool_use = 'TOOL_USE_AND_PROCESS'
        self.tool = tools.PageLoaderTool()

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
        self.config.tool_use = 'TOOL_USE_DIRECT'
        self.tool = tools.WebScrapingTool()

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

