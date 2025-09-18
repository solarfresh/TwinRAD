import json
import uuid
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from twinrad.schemas.graphs import MindMap
from twinrad.tools.common.base_tool import ToolConfig
from twinrad.tools.knowledge.curation import MindMapGraphBuilder


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
        "branches": [
            {
                "label": "Technological Hurdles",
                "type": "MainTopic",
                "node_id": node_ids["main_topic_1"],
                "sub_branches": [
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
    if builder.graph.central_idea is None:
        assert False, "CentralIdea not be None after initial run."

    response_data = json.loads(response)

    # 1. Check the response message
    assert response_data["status"] == "success"

    # 2. Check the graph's state
    assert isinstance(builder.graph, MindMap)
    assert builder.graph.central_idea.label == "Renewable Energy Challenges"

    # 3. Check the number of nodes and relationships
    assert len(builder.graph.all_nodes) == 5
    assert len(builder.graph.all_relationships) == 1

@pytest.mark.asyncio
async def test_run_incremental_update(mind_map_mock_config, mind_map_mock_data):
    """Tests adding new nodes and relationships to an existing graph."""
    builder = MindMapGraphBuilder(config=mind_map_mock_config)

    # First run (initial build)
    await builder.run(json_output=json.dumps(mind_map_mock_data))

    if builder.graph.central_idea is None:
        assert False, "CentralIdea not be None after initial run."

    # Prepare a new JSON with additional data
    new_data = {
        "branches": [
            {
                "label": "Economic Factors",
                "type": "MainTopic",
                "node_id": str(uuid.uuid4()),
                "sub_branches": [
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
                "source": builder.graph.central_idea.node_id,
                "target": builder.graph.central_idea.main_topics.pop().node_id, # Pop a node to get an existing one
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