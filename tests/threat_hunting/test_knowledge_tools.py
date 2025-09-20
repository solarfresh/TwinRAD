import json
import uuid
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from twinrad.threat_hunting.knowledge.graphs import MindMap
from twinrad.threat_hunting.knowledge.tools import (GoogleSearchTool,
                                                    MindMapGraphBuilder,
                                                    PageLoaderTool,
                                                    PlaywrightWrapper,
                                                    ToolConfig,
                                                    WebScrapingTool)


@pytest.fixture
def mock_config():
    mock_config = MagicMock(spec=ToolConfig)
    return mock_config

@pytest.fixture
def mock_gs_successful_response():
    return {
        "items": [
            {
                "title": "Example Domain",
                "link": "https://www.example.com",
                "snippet": "This domain is for use in illustrative examples in documents."
            },
            {
                "title": "Another Example Page",
                "link": "https://www.example.org/page",
                "snippet": "Another page for illustrative purposes."
            }
        ]
    }

@pytest.fixture
def expected_gs_processed_results():
    return [
        {
            "title": "Example Domain",
            "url": "https://www.example.com",
            "snippet": "This domain is for use in illustrative examples in documents."
        },
        {
            "title": "Another Example Page",
            "url": "https://www.example.org/page",
            "snippet": "Another page for illustrative purposes."
        }
    ]


@pytest.fixture
def mind_map_mock_config():
    mock_config = MagicMock(spec=ToolConfig)
    return mock_config

@pytest.fixture
def mind_map_mock_data() -> Dict[str, Any]:
    """Generates a complete, valid mind map JSON for testing."""
    node_ids = {
        "central_idea": str(uuid.uuid4()),
        "main_topic_1": str(uuid.uuid4()),
        "sub_topic_1": str(uuid.uuid4()),
        "keyword_1": str(uuid.uuid4()),
        "keyword_2": str(uuid.uuid4()),
        "main_topic_2": str(uuid.uuid4()),
        "sub_topic_2": str(uuid.uuid4())
    }

    return {
        "central_idea": {
            "label": "Renewable Energy Challenges",
            "type": "CentralIdea",
            "node_id": node_ids["central_idea"]
        },
        "main_topics": [
            {
                "label": "Technological Hurdles",
                "type": "MainTopic",
                "node_id": node_ids["main_topic_1"],
                "sub_topics": [
                    {
                        "label": "Intermittency",
                        "type": "SubTopic",
                        "node_id": node_ids["sub_topic_1"],
                        "keywords": [
                            {
                                "label": "Batteries",
                                "type": "Keyword",
                                "node_id": node_ids["keyword_1"]
                            },
                            {
                                "label": "Energy Storage",
                                "type": "Keyword",
                                "node_id": node_ids["keyword_2"]
                            }
                        ]
                    }
                ]
            }
        ],
        "relationships": [
            {
                "source": node_ids["sub_topic_1"],
                "target": node_ids["keyword_1"],
                "type": "SUPPORTS"
            }
        ]
    }

@pytest.mark.asyncio
async def test_run_initial_build_success(mind_map_mock_config, mind_map_mock_data):
    """Tests the first run with a valid, complete JSON input."""
    builder = MindMapGraphBuilder(config=mind_map_mock_config)
    json_input = json.dumps(mind_map_mock_data)

    response = await builder.run(json_output=json_input)
    response_data = json.loads(response)

    # 1. Check the response message
    assert response_data["status"] == "success"

    # 2. Check the graph's state
    assert isinstance(builder.graph, MindMap)

    central_idea = builder.graph.central_ideas.get('Renewable Energy Challenges')
    if central_idea is None:
        assert False, "CentralIdea not be None after initial run."

    assert central_idea.label == "Renewable Energy Challenges"

    # 3. Check the number of nodes and relationships
    assert len(builder.graph.all_nodes) == 5
    assert len(builder.graph.all_relationships) == 1

@pytest.mark.asyncio
async def test_run_incremental_update(mind_map_mock_config, mind_map_mock_data):
    """Tests adding new nodes and relationships to an existing graph."""
    builder = MindMapGraphBuilder(config=mind_map_mock_config)

    # First run (initial build)
    await builder.run(json_output=json.dumps(mind_map_mock_data))

    central_idea = builder.graph.central_ideas.get('Renewable Energy Challenges')
    if central_idea is None:
        assert False, "CentralIdea not be None after initial run."

    # Prepare a new JSON with additional data
    new_data = {
        "central_idea": {
            "label": "Renewable Energy Challenges",
            "type": "CentralIdea"
        },
        "main_topics": [
            {
                "label": "Economic Factors",
                "type": "MainTopic",
                "node_id": str(uuid.uuid4()),
                "sub_topics": [
                    {
                        "label": "High Initial Costs",
                        "type": "SubTopic",
                        "node_id": str(uuid.uuid4()),
                        "keywords": []
                    }
                ]
            }
        ],
        "relationships": [
            {
                "source": central_idea.node_id,
                "target": central_idea.main_topics.pop().node_id, # Pop a node to get an existing one
                "type": "LEADS_TO"
            }
        ]
    }

    await builder.run(json_output=json.dumps(new_data))

    # Check the new state of the graph
    assert len(builder.graph.all_nodes) == 7 # 5 initial + 2 new
    assert len(builder.graph.all_relationships) == 2 # 1 initial + 1 new

@pytest.mark.asyncio
async def test_run_with_duplicate_nodes(mind_map_mock_config, mind_map_mock_data):
    """Tests that the builder correctly handles and ignores duplicate nodes."""
    builder = MindMapGraphBuilder(config=mind_map_mock_config)

    # Run twice with the exact same data
    await builder.run(json_output=json.dumps(mind_map_mock_data))
    await builder.run(json_output=json.dumps(mind_map_mock_data))

    if builder.graph is None:
        assert False, "Graph should not be None after initial run."

    # The number of nodes and relationships should not increase on the second run
    assert len(builder.graph.all_nodes) == 5
    assert len(builder.graph.all_relationships) == 1

@pytest.mark.asyncio
async def test_run_invalid_json(mind_map_mock_config):
    """Tests failure case with a malformed JSON string."""
    builder = MindMapGraphBuilder(config=mind_map_mock_config)
    invalid_json = '{"central_idea": "test_label", "branches": ['

    response = await builder.run(json_output=invalid_json)
    response_data = json.loads(response)

    assert response_data["status"] == "error"
    assert "Failed to parse JSON" in response_data["message"]

@pytest.mark.asyncio
async def test_run_with_pydantic_validation_error(mind_map_mock_config):
    """Tests failure case when JSON is valid but violates the Pydantic schema."""
    builder = MindMapGraphBuilder(config=mind_map_mock_config)
    invalid_schema_data = {
        "central_idea": {
            "label": "Test",
            "type": "InvalidType" # This is not a valid Literal type
        }
    }

    response = await builder.run(json_output=json.dumps(invalid_schema_data))
    response_data = json.loads(response)

    assert response_data["status"] == "error"
    assert "Validation error" in response_data["message"]

@pytest.mark.asyncio
async def test_gs_run_success(mock_config, mock_gs_successful_response, expected_gs_processed_results):
    """
    Tests a successful run of the GoogleSearchTool with a valid query.
    """
    mock_config.google_search_engine_api_key = "test_key"
    mock_config.google_search_engine_id = "test_cx"
    mock_config.google_search_engine_base_url = "http://test-api.com"

    # Mock the HTTP response object
    mock_client_instance  = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value=mock_gs_successful_response)
    mock_response.raise_for_status.return_value = None
    mock_client_instance.get = AsyncMock(return_value=mock_response)

    tool = GoogleSearchTool(config=mock_config)
    tool.client = mock_client_instance
    result = await tool.run(query="test query")

    # Assertions
    assert json.loads(result) == expected_gs_processed_results
    mock_client_instance.get.assert_called_once_with(
        "http://test-api.com",
        params={'key': 'test_key', 'cx': 'test_cx', 'q': 'test query'},
        timeout=10.0
    )

@pytest.mark.asyncio
async def test_gs_run_missing_query(mock_config):
    """
    Tests that a run with a missing query returns the correct error message.
    """
    mock_config.google_search_engine_api_key = "test_key"
    mock_config.google_search_engine_id = "test_cx"
    mock_config.google_search_engine_base_url = "http://test-api.com"

    mock_client_instance  = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_client_instance.get = AsyncMock(return_value=mock_response)

    tool = GoogleSearchTool(config=mock_config)
    tool.client = mock_client_instance
    result = json.loads(await tool.run())

    # Assertions
    assert "error" in result
    assert "An unexpected error occurred: Query parameter cannot be empty or missing." in result["error"]
    mock_client_instance.assert_not_called()

@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_gs_run_http_error(mock_get, mock_config):
    """
    Tests that an HTTP error (e.g., 404, 500) is handled correctly.
    """
    mock_config.google_search_engine_api_key = "test_key"
    mock_config.google_search_engine_id = "test_cx"
    mock_config.google_search_engine_base_url = "http://test-api.com"

    # Mock the HTTP response object to raise an error
    mock_get.side_effect = httpx.HTTPStatusError(
        message="Not Found", request=httpx.Request("GET", ""), response=httpx.Response(404, request=httpx.Request("GET", ""), content="Not Found")
    )

    tool = GoogleSearchTool(config=mock_config)
    result = json.loads(await tool.run(query="test query"))

    # Assertions
    assert "error" in result
    assert "HTTP error during Google search" in result["error"]

@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_gs_run_connection_error(mock_get, mock_config):
    """
    Tests that a connection-level exception is handled correctly.
    """
    mock_config.google_search_engine_api_key = "test_key"
    mock_config.google_search_engine_id = "test_cx"
    mock_config.google_search_engine_base_url = "http://test-api.com"

    # Mock the HTTP response object to raise a connection error
    mock_get.side_effect = httpx.ConnectError("Connection failed")

    tool = GoogleSearchTool(config=mock_config)
    result = json.loads(await tool.run(query="test query"))

    # Assertions
    assert "error" in result
    assert "An unexpected error occurred: Connection failed" in result["error"]

@pytest.mark.asyncio
async def test_gs_run_missing_api_credentials(mock_config):
    """
    Tests that the tool returns an error if API credentials are not configured.
    """
    mock_config.google_search_engine_api_key = None
    mock_config.google_search_engine_id = None
    mock_config.google_search_engine_base_url = "http://test-api.com"

    tool = GoogleSearchTool(config=mock_config)
    result = json.loads(await tool.run(query="test query"))

    # Assertions
    assert "error" in result
    assert "API key or Search Engine ID (cx) is not configured." in result["error"]

def test_gs_get_name(mock_config):
    """
    Tests that get_name returns the correct string.
    """
    mock_config.google_search_engine_api_key = "test_key"
    mock_config.google_search_engine_id = "test_cx"
    mock_config.google_search_engine_base_url = "http://test-api.com"
    tool = GoogleSearchTool(config=mock_config)
    assert tool.get_name() == "google_search"

def test_gs_get_description(mock_config):
    """
    Tests that get_description returns the correct string.
    """
    mock_config.google_search_engine_api_key = "test_key"
    mock_config.google_search_engine_id = "test_cx"
    mock_config.google_search_engine_base_url = "http://test-api.com"
    tool = GoogleSearchTool(config=mock_config)
    assert tool.get_description() == "Performs a Google search and returns a list of web page links and snippets."

def test_gs_get_parameters(mock_config):
    """
    Tests that get_parameters returns the correct dictionary.
    """
    mock_config.google_search_engine_api_key = "test_key"
    mock_config.google_search_engine_id = "test_cx"
    mock_config.google_search_engine_base_url = "http://test-api.com"
    tool = GoogleSearchTool(config=mock_config)
    expected_params = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string to search on Google."
            }
        },
        "required": ["query"]
    }
    assert tool.get_parameters() == expected_params

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

    with patch('twinrad.threat_hunting.knowledge.tools.async_playwright', return_value=mock_async_playwright):
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
async def test_pw_scrape_from_html_success():
    """
    Tests successful data scraping from HTML content.
    """
    mock_inner_text = "Test Data"
    mock_locator = AsyncMock(inner_text=AsyncMock(return_value=mock_inner_text))
    mock_page = AsyncMock(locator=MagicMock(return_value=mock_locator))

    pw_wrapper = PlaywrightWrapper()
    pw_wrapper._page = mock_page

    html_content = "<div><p>Test Data</p></div>"
    query = "p"
    result = await pw_wrapper.scrape_from_html(html_content, query)

    expected_json = {"query": query, "data": mock_inner_text}
    assert json.loads(result) == expected_json
    mock_page.set_content.assert_called_once_with(html_content)
    mock_page.locator.assert_called_once_with(query)

@pytest.mark.asyncio
async def test_pw_scrape_from_html_error():
    """
    Tests that a Playwright error during HTML scraping is caught.
    """
    mock_locator = MagicMock(inner_text=AsyncMock(side_effect=TimeoutError("Locator timed out.")))
    mock_page = AsyncMock(locator=MagicMock(return_value=mock_locator))

    pw_wrapper = PlaywrightWrapper()
    pw_wrapper._page = mock_page

    html_content = "<div></div>"
    query = "p"
    result = await pw_wrapper.scrape_from_html(html_content, query)

    error_data = json.loads(result)
    assert "error" in error_data
    assert "timed out" in error_data["error"]

@pytest.mark.asyncio
async def test_pw_get_raw_html_success():
    """
    Tests successful retrieval of raw HTML content.
    """
    mock_content = "<html><body><h1>Test</h1></body></html>"
    mock_page = AsyncMock(content=AsyncMock(return_value=mock_content))

    pw_wrapper = PlaywrightWrapper()
    pw_wrapper._page = mock_page

    url = "http://example.com"
    result = await pw_wrapper.get_raw_html(url)

    expected_json = {"url": url, "html_content": mock_content}
    assert json.loads(result) == expected_json
    mock_page.goto.assert_called_once_with(url, timeout=300000)

@pytest.mark.asyncio
async def test_pw_get_raw_html_error():
    """
    Tests that a goto error is caught and a JSON error message is returned.
    """
    mock_page = AsyncMock(goto=AsyncMock(side_effect=TimeoutError("Page navigation timed out.")))

    pw_wrapper = PlaywrightWrapper()
    pw_wrapper._page = mock_page

    url = "http://invalid.url"
    result = await pw_wrapper.get_raw_html(url)

    error_data = json.loads(result)
    assert "error" in error_data
    assert "timed out" in error_data["error"]

@pytest.mark.asyncio
async def test_pw_scrape_from_url_success():
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
    result = await pw_wrapper.scrape_from_url(url, query)

    expected_json = {"url": url, "query": query, "data": mock_inner_text}
    assert json.loads(result) == expected_json
    mock_page.goto.assert_called_once_with(url, timeout=300000)
    mock_page.locator.assert_called_once_with(query)

@pytest.mark.asyncio
async def test_pw_scrape_from_url_error_on_missing_element():
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

    with patch('twinrad.threat_hunting.knowledge.tools.async_playwright', return_value=mock_async_playwright):
        async with PlaywrightWrapper() as playwright_tool:
            result = await playwright_tool.scrape_from_url(url, query)
            error_data = json.loads(result)

    assert "error" in error_data
    assert "timed out" in error_data["error"]

@pytest.mark.asyncio
async def test_pl_run_success():
    """
    Tests a successful run of the PageLoaderTool with a valid URL.
    """
    # Mock the return value of get_raw_html
    mock_html_content = {"url": "http://example.com", "html_content": "<html><body>test</body></html>"}
    mock_get_raw_html = AsyncMock(return_value=json.dumps(mock_html_content))

    # Mock the PlaywrightWrapper context manager
    mock_pw_wrapper = AsyncMock()
    mock_pw_wrapper.__aenter__.return_value = AsyncMock(get_raw_html=mock_get_raw_html)

    # Patch the PlaywrightWrapper class itself to return our mock instance
    with patch('twinrad.threat_hunting.knowledge.tools.PlaywrightWrapper', return_value=mock_pw_wrapper):
        tool = PageLoaderTool()
        result = await tool.run(url="http://example.com")

    # Assertions
    assert json.loads(result) == mock_html_content
    mock_get_raw_html.assert_called_once_with("http://example.com")


@pytest.mark.asyncio
async def test_pl_run_missing_url():
    """
    Tests that a run with a missing URL returns the correct error message.
    """
    tool = PageLoaderTool()
    result = json.loads(await tool.run())

    assert "error" in result
    assert "Missing 'url' parameter." in result["error"]


@pytest.mark.asyncio
async def test_pl_run_playwright_error():
    """
    Tests that a Playwright error during run is caught and returned.
    """
    # Mock the return value of get_raw_html to be an error
    mock_error_message = {"error": "Page navigation failed."}
    mock_get_raw_html = AsyncMock(return_value=json.dumps(mock_error_message))

    # Mock the PlaywrightWrapper context manager
    mock_pw_wrapper = AsyncMock()
    mock_pw_wrapper.__aenter__.return_value = AsyncMock(get_raw_html=mock_get_raw_html)

    # Patch the PlaywrightWrapper class itself
    with patch('twinrad.threat_hunting.knowledge.tools.PlaywrightWrapper', return_value=mock_pw_wrapper):
        tool = PageLoaderTool()
        result = await tool.run(url="http://invalid-url.com")

    assert json.loads(result) == mock_error_message
    mock_get_raw_html.assert_called_once_with("http://invalid-url.com")


def test_pl_get_name():
    """
    Tests that get_name returns the correct string.
    """
    tool = PageLoaderTool()
    assert tool.get_name() == "load_page_html"


def test_pl_get_description():
    """
    Tests that get_description returns the correct string.
    """
    tool = PageLoaderTool()
    # This assertion needs to be updated to match the correct description.
    assert tool.get_description() == "Navigates to a given URL and returns the entire raw HTML content of the page as a JSON string."


def test_pl_get_parameters():
    """
    Tests that get_parameters returns the correct dictionary.
    """
    tool = PageLoaderTool()
    expected_params = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL of the webpage to load."
            }
        },
        "required": ["url"]
    }
    assert tool.get_parameters() == expected_params

@pytest.mark.asyncio
async def test_ws_run_success(mock_config):
    """
    Tests a successful run of the tool with valid parameters.
    """
    # Mock the PlaywrightWrapper's scrape_data method to return a canned response
    mock_scrape_data = AsyncMock(return_value=json.dumps({"data": "Success"}))
    mock_playwright_wrapper = AsyncMock()
    mock_playwright_wrapper.__aenter__.return_value.scrape_all_text_from_url = mock_scrape_data

    # Patch the class itself to return our mock instance
    with patch('twinrad.threat_hunting.knowledge.tools.PlaywrightWrapper', return_value=mock_playwright_wrapper):
        tool = WebScrapingTool(config=mock_config)
        result = await tool.run(url_contents="[{\"url\":\"https://example.com/\"}]")

        expected_json = [{"data": "Success"}]
        assert json.loads(result) == expected_json
        mock_scrape_data.assert_called_once_with("https://example.com/")

@pytest.mark.asyncio
async def test_ws_run_missing_url(mock_config):
    """
    Tests that a run with a missing URL returns the correct error message.
    """
    mock_scrape_data = AsyncMock(return_value=json.dumps({"data": "Success"}))
    mock_playwright_wrapper = AsyncMock()
    mock_playwright_wrapper.__aenter__.return_value.scrape_all_text_from_url = mock_scrape_data

    with patch('twinrad.threat_hunting.knowledge.tools.PlaywrightWrapper', return_value=mock_playwright_wrapper):
        tool = WebScrapingTool(config=mock_config)
        result = json.loads(await tool.run())

    assert result == {"error": "Missing 'url_contents' parameter."}

def test_ws_get_name(mock_config):
    """
    Tests that get_name returns the correct string.
    """
    tool = WebScrapingTool(config=mock_config)
    assert tool.get_name() == "scrape_web_data"

def test_ws_get_description(mock_config):
    """
    Tests that get_description returns the correct string.
    """
    tool = WebScrapingTool(config=mock_config)
    assert tool.get_description() == "Scrapes data from a specified HTML content using a CSS selector query and returns it as a JSON string."

def test_ws_get_parameters(mock_config):
    """
    Tests that get_parameters returns the correct dictionary.
    """
    tool = WebScrapingTool(config=mock_config)
    expected_params = {
        "type": "object",
        "properties": {
            "url_contents": {
                "type": "string",
                "description": "A JSON string containing a list of URLs to scrape."
            }
        },
        "required": ["url_contents"]
    }
    assert tool.get_parameters() == expected_params
