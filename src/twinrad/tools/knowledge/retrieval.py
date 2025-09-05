import json
from typing import Any, Dict

from playwright.async_api import async_playwright

from twinrad.tools.common.base_tool import BaseTool


class PlaywrightWrapper:
    """
    A wrapper for Playwright to perform web scraping tasks.
    """
    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None

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
            await self._page.goto(url)
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
            await self._page.goto(url)
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
        html_content = kwargs.get('html_content', '')
        query = kwargs.get('query', '')
        self.logger.debug(f"Running WebScoutTool with html_content: {html_content} and query: {query}")
        if not html_content or not query:
            return json.dumps({"error": "Missing 'html_content' or 'query' parameters."})

        async with PlaywrightWrapper() as playwright:
            return await playwright.scrape_from_html(html_content, query)

    def get_name(self) -> str:
        return "scrape_web_data"

    def get_description(self) -> str:
        return "Scrapes data from a specified HTML content using a CSS selector query and returns it as a JSON string."

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The CSS selector to identify the data to be scraped."
                },
                "html_content": {
                    "type": "string",
                    "description": "The raw HTML content of the webpage to scrape."
                }
            },
            "required": ["query", "html_content"]
        }