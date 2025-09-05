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

    async def scrape_data(self, url: str, query: str) -> str:
        """
        Navigates to a URL and scrapes data based on a query.
        """
        try:
            if not self._page:
                raise RuntimeError("Playwright page is not initialized.")

            await self._page.goto(url)
            element = self._page.locator(query)
            data = await element.inner_text()
            return json.dumps({"url": url, "query": query, "data": data})
        except Exception as e:
            return json.dumps({"error": str(e)})


class WebScrapingTool(BaseTool):
    """
    A concrete tool implementation for the WebScout agent.
    """
    def __init__(self):
        super().__init__()

        self.playwright_tool = PlaywrightWrapper()

    async def run(self, **kwargs) -> Any:
        """
        Executes the web scraping task.

        Args:
            url (str): The URL of the webpage to scrape.
            query (str): The CSS selector to identify the data to be scraped.
        """
        url = kwargs.get('url', '')
        query = kwargs.get('query', '')
        self.logger.debug(f"Running WebScoutTool with url: {url} and query: {query}")
        if not url or not query:
            return json.dumps({"error": "Missing 'url' or 'query' parameters."})

        async with self.playwright_tool as playwright:
            return await playwright.scrape_data(url, query)

    def get_name(self) -> str:
        return "scrape_web_data"

    def get_description(self) -> str:
        return "Scrapes data from a specified URL using a CSS selector query and returns it as a JSON string."

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the webpage to scrape."
                },
                "query": {
                    "type": "string",
                    "description": "The CSS selector to identify the data to be scraped."
                }
            },
            "required": ["url", "query"]
        }