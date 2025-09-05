import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from twinrad.tools.knowledge.retrieval import (PlaywrightWrapper,
                                               WebScrapingTool)


@pytest.mark.asyncio
async def test_aenter_initializes_attributes():
    """
    Tests that __aenter__ correctly initializes Playwright, browser, and page.
    """
    mock_context = AsyncMock(name="mock_context")
    mock_browser = AsyncMock(name="mock_browser", new_context=AsyncMock(return_value=mock_context))
    mock_chromium = AsyncMock(name="mock_chromium", launch=AsyncMock(return_value=mock_browser))
    mock_playwright_start_return_value = AsyncMock(name="mock_playwright_start_return_value", chromium=mock_chromium)
    mock_async_playwright = AsyncMock(name="mock_async_playwright", start=AsyncMock(return_value=mock_playwright_start_return_value))
    mock_context.new_page.return_value = MagicMock(name="mock_page")

    with patch('twinrad.tools.knowledge.retrieval.async_playwright', return_value=mock_async_playwright):
        async with PlaywrightWrapper() as pw_wrapper:
            assert pw_wrapper._playwright is mock_playwright_start_return_value
            assert pw_wrapper._browser is mock_browser
            assert pw_wrapper._context is mock_context
            mock_context.new_page.assert_called_once()
            assert pw_wrapper._page is not None

@pytest.mark.asyncio
async def test_aexit_closes_resources():
    """
    Tests that __aexit__ correctly closes the browser and stops Playwright.
    """
    mock_browser = AsyncMock()
    mock_playwright = AsyncMock()

    pw_wrapper = PlaywrightWrapper()
    pw_wrapper._browser = mock_browser
    pw_wrapper._playwright = mock_playwright

    await pw_wrapper.__aexit__(None, None, None)

    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()

@pytest.mark.asyncio
async def test_scrape_data_success():
    """
    Tests successful data scraping and JSON output.
    """
    mock_inner_text = "Test Data"
    mock_locator = AsyncMock(inner_text=AsyncMock(return_value=mock_inner_text))
    mock_page = AsyncMock(locator=MagicMock(return_value=mock_locator))

    pw_wrapper = PlaywrightWrapper()
    pw_wrapper._page = mock_page

    url = "https://example.com"
    query = "div.test"
    result = await pw_wrapper.scrape_data(url, query)

    expected_json = {"url": url, "query": query, "data": mock_inner_text}
    assert json.loads(result) == expected_json
    mock_page.goto.assert_called_once_with(url)
    mock_page.locator.assert_called_once_with(query)

@pytest.mark.asyncio
async def test_scrape_data_error_on_missing_element():
    """
    Tests that a Playwright error is caught and an error JSON is returned.
    """
    mock_inner_text = AsyncMock(side_effect=TimeoutError("Locator timed out."))
    mock_locator = MagicMock(inner_text=mock_inner_text)
    mock_page = AsyncMock(locator=MagicMock(return_value=mock_locator))

    mock_context = AsyncMock(name="mock_context")
    mock_browser = AsyncMock(name="mock_browser", new_context=AsyncMock(return_value=mock_context))
    mock_chromium = AsyncMock(name="mock_chromium", launch=AsyncMock(return_value=mock_browser))
    mock_playwright_start_return_value = AsyncMock(name="mock_playwright_start_return_value", chromium=mock_chromium)
    mock_async_playwright = AsyncMock(name="mock_async_playwright", start=AsyncMock(return_value=mock_playwright_start_return_value))
    mock_context.new_page.return_value = mock_page

    url = "https://example.com"
    query = "div.non-existent"

    with patch('twinrad.tools.knowledge.retrieval.async_playwright', return_value=mock_async_playwright):
        async with PlaywrightWrapper() as playwright_tool:
            result = await playwright_tool.scrape_data(url, query)
            error_data = json.loads(result)

    assert "error" in error_data
    assert "timed out" in error_data["error"]

@pytest.mark.asyncio
async def test_run_success():
    """
    Tests a successful run of the tool with valid parameters.
    """
    # Mock the PlaywrightWrapper's scrape_data method to return a canned response
    mock_scrape_data = AsyncMock(return_value=json.dumps({"data": "Success"}))
    mock_playwright_wrapper = AsyncMock()
    mock_playwright_wrapper.__aenter__.return_value.scrape_data = mock_scrape_data

    # Patch the class itself to return our mock instance
    with patch('twinrad.tools.knowledge.retrieval.PlaywrightWrapper', return_value=mock_playwright_wrapper):
        tool = WebScrapingTool()
        result = await tool.run(url="http://example.com", query=".test")

        expected_json = {"data": "Success"}
        assert json.loads(result) == expected_json
        mock_scrape_data.assert_called_once_with("http://example.com", ".test")

@pytest.mark.asyncio
async def test_run_missing_url():
    """
    Tests that a run with a missing URL returns the correct error message.
    """
    mock_scrape_data = AsyncMock(return_value=json.dumps({"data": "Success"}))
    mock_playwright_wrapper = AsyncMock()
    mock_playwright_wrapper.__aenter__.return_value.scrape_data = mock_scrape_data

    with patch('twinrad.tools.knowledge.retrieval.PlaywrightWrapper', return_value=mock_playwright_wrapper):
        tool = WebScrapingTool()
        result = json.loads(await tool.run(query=".test"))

    assert result == {"error": "Missing 'url' or 'query' parameters."}

@pytest.mark.asyncio
async def test_run_missing_query():
    """
    Tests that a run with a missing query returns the correct error message.
    """
    mock_scrape_data = AsyncMock(return_value=json.dumps({"data": "Success"}))
    mock_playwright_wrapper = AsyncMock()
    mock_playwright_wrapper.__aenter__.return_value.scrape_data = mock_scrape_data

    with patch('twinrad.tools.knowledge.retrieval.PlaywrightWrapper', return_value=mock_playwright_wrapper):
        tool = WebScrapingTool()
        result = json.loads(await tool.run(url="http://example.com"))

    assert result == {"error": "Missing 'url' or 'query' parameters."}

def test_get_name():
    """
    Tests that get_name returns the correct string.
    """
    tool = WebScrapingTool()
    assert tool.get_name() == "scrape_web_data"

def test_get_description():
    """
    Tests that get_description returns the correct string.
    """
    tool = WebScrapingTool()
    assert tool.get_description() == "Scrapes data from a specified URL using a CSS selector query and returns it as a JSON string."

def test_get_parameters():
    """
    Tests that get_parameters returns the correct dictionary.
    """
    tool = WebScrapingTool()
    expected_params = {
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
    assert tool.get_parameters() == expected_params
