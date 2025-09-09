import json
from typing import Any, Dict, List

import httpx
from playwright.async_api import async_playwright

from twinrad.configs.settings import settings
from twinrad.tools.common.base_tool import BaseTool


class GoogleSearchTool(BaseTool):
    """
    A tool that performs a Google search using the official Custom Search JSON API.

    API Documentation:
        https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
    """
    def __init__(self):
        super().__init__()
        # These should be loaded from a secure configuration or environment variables
        self.api_key = settings.google_search_engine_api_key
        self.cx = settings.google_search_engine_id
        self.base_url = settings.google_search_engine_base_url
        self.client = httpx.AsyncClient()

    async def run(self, **kwargs) -> Any:
        """
        Executes a Google search for the given query using the Custom Search API.

        Args:
            query: The search query string.

        Returns:
            A JSON string containing the search results.
        """
        if not self.api_key or not self.cx:
            return json.dumps({"error": "API key or Search Engine ID (cx) is not configured."})

        query = kwargs.get('query', '')
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query
        }

        try:
            if not params.get('q'):
                raise ValueError("Missing 'query' parameter.")

            response = await self.client.get(self.base_url, params=params, timeout=10.0)
            response.raise_for_status()  # Raise an exception for bad status codes

            search_data = response.json()
            items = search_data.get("items", [])

            processed_results: List[Dict[str, str | None]] = []
            for result in items:
                processed_results.append({
                    "title": result.get("title"),
                    "url": result.get("link"),
                    "snippet": result.get("snippet")
                })

            return json.dumps(processed_results)

        except httpx.HTTPStatusError as e:
            error_message = f"HTTP error during Google search: {e.response.text}"
            return json.dumps({"error": error_message})
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            return json.dumps({"error": error_message})

    def get_name(self) -> str:
        return "google_search"

    def get_description(self) -> str:
        return "Performs a Google search and returns a list of web page links and snippets."

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string to search on Google."
                }
            },
            "required": ["query"]
        }


class PlaywrightWrapper:
    """
    A wrapper for Playwright to perform web scraping tasks.
    """
    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None
        self.timeout = 300000

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch()
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def scrape_all_text_from_url(self, url: str) -> str:
        if not self._page:
            raise RuntimeError("Playwright page is not initialized.")

        try:
            await self._page.goto(url, timeout=self.timeout)
            element = self._page.locator('body')
            data = await element.all_inner_texts()
            return json.dumps({"url": url, "query": 'body', "data": ''.join(data)})
        except Exception as e:
            return json.dumps({"error": str(e)})

    async def scrape_from_html(self, html_content: str, query: str) -> str:
        """
        Scrapes data from raw HTML content.

        Args:
            html_content (str): The raw HTML content to load.
            query (str): The CSS selector to identify the data to be scraped.
        """
        if not self._page:
            raise RuntimeError("Playwright page is not initialized.")

        try:
            await self._page.set_content(html_content)
            data = await self._page.locator(query).inner_text()
            return json.dumps({"query": query, "data": data})
        except Exception as e:
            return json.dumps({"error": str(e)})

    async def scrape_from_url(self, url: str, query: str) -> str:
        """
        Navigates to a URL and scrapes data based on a query.

        Args:
            url (str): The URL of the webpage to scrape.
            query (str): The CSS selector to identify the data to be scraped.
        """
        if not self._page:
            raise RuntimeError("Playwright page is not initialized.")

        try:
            await self._page.goto(url, timeout=self.timeout)
            element = self._page.locator(query)
            data = await element.inner_text()
            return json.dumps({"url": url, "query": query, "data": data})
        except Exception as e:
            return json.dumps({"error": str(e)})

    async def get_raw_html(self, url: str) -> str:
        """
        Navigates to a URL and returns the raw HTML content.
        """
        if not self._page:
            raise RuntimeError("Playwright page is not initialized.")

        try:
            await self._page.goto(url, timeout=self.timeout)
            html_content = await self._page.content()
            return json.dumps({"url": url, "html_content": html_content})
        except Exception as e:
            return json.dumps({"error": str(e)})


class PageLoaderTool(BaseTool):
    """
    A tool to load the raw HTML content of a webpage.
    """

    async def run(self, **kwargs) -> Any:
        """
        Executes the page loading task and returns the raw HTML.
        """
        url = kwargs.get('url', '')
        if not url:
            return json.dumps({"error": "Missing 'url' parameter."})

        # Call the asynchronous method to get the HTML content
        async with PlaywrightWrapper() as playwright:
            return await playwright.get_raw_html(url)

    def get_name(self) -> str:
        return "load_page_html"

    def get_description(self) -> str:
        return "Navigates to a given URL and returns the entire raw HTML content of the page as a JSON string."

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the webpage to load."
                }
            },
            "required": ["url"]
        }


class WebScrapingTool(BaseTool):
    """
    A concrete tool implementation for the WebScout agent.
    """

    async def run(self, **kwargs) -> Any:
        """
        Executes the web scraping task.

        Args:
            html_content (str): The raw HTML content to scrape.
            query (str): The CSS selector to identify the data to be scraped.
        """
        url = kwargs.get('url', '')
        self.logger.debug(f"Running WebScoutTool with url: {url}")
        if not url:
            return json.dumps({"error": "Missing 'url' parameter."})

        async with PlaywrightWrapper() as playwright:
            return await playwright.scrape_all_text_from_url(url=url)

    def get_name(self) -> str:
        return "scrape_web_data"

    def get_description(self) -> str:
        return "Scrapes data from a specified HTML content using a CSS selector query and returns it as a JSON string."

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The url of the webpage to scrape."
                }
            },
            "required": ["url"]
        }