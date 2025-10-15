import json
from unittest.mock import MagicMock

import networkx as nx
import pytest

from twinrad.core.tools.embeddings import Node2Vec, Node2VecConfig


@pytest.fixture
def sample_graph_data():
    """Provides sample graph data in the expected JSON format."""
    return {
        "nodes": [
            {"id": "A"},
            {"id": "B"},
            {"id": "C"},
            {"id": "D"}
        ],
        "edges": [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
            {"source": "B", "target": "D"}
        ]
    }

@pytest.fixture
def node2vec_instance():
    """Provides a configured Node2Vec instance for testing."""
    config = Node2VecConfig(num_walks=2, walk_length=3, p=1.0, q=1.0)
    return Node2Vec(config=config)

def test_node2vec_init(node2vec_instance):
    """Test that the Node2Vec instance is initialized correctly."""
    assert node2vec_instance.num_walks == 2
    assert node2vec_instance.walk_length == 3
    assert node2vec_instance.p == 1.0
    assert node2vec_instance.q == 1.0

@pytest.mark.asyncio
async def test_run_generates_walks(node2vec_instance, sample_graph_data):
    """Test the run method to ensure it processes the graph and generates walks."""
    json_data_string = json.dumps(sample_graph_data)
    kwargs = {'json_data': json_data_string}

    # Use a MagicMock to control the output of the walk generation for predictable testing
    node2vec_instance.generate_node2vec_walks = MagicMock(return_value=[
        ['A', 'B', 'C'],
        ['A', 'B', 'D'],
        ['B', 'C', 'B'],
        ['C', 'B', 'A']
    ])

    walks_json = await node2vec_instance.run(**kwargs)
    walks = json.loads(walks_json)

    assert isinstance(walks, list)
    assert len(walks) == 4  # Based on the mock return value
    assert walks[0] == ['A', 'B', 'C']
    node2vec_instance.generate_node2vec_walks.assert_called_once()

def test_generate_node2vec_walks(node2vec_instance, sample_graph_data):
    """Test the walk generation logic to ensure the correct number of walks are created."""
    G = nx.node_link_graph(sample_graph_data, edges="edges")

    # Use a MagicMock to ensure node2vec_walk is called correctly
    node2vec_instance.node2vec_walk = MagicMock(side_effect=lambda graph, node: [node, 'X', 'Y'])

    walks = node2vec_instance.generate_node2vec_walks(graph=G)

    expected_num_walks = node2vec_instance.num_walks * len(G.nodes)
    assert len(walks) == expected_num_walks

def test_node2vec_walk_length(node2vec_instance):
    """Test that a single walk has the correct length."""
    G = nx.Graph()
    G.add_edges_from([('A', 'B'), ('B', 'C')])

    walk = node2vec_instance.node2vec_walk(graph=G, start_node='A')

    assert len(walk) == node2vec_instance.walk_length

def test_node2vec_walk_end_condition(node2vec_instance):
    """Test that the walk stops if it reaches a node with no neighbors."""
    node2vec_instance.walk_length = 5
    G = nx.Graph()
    G.add_edge('A', 'B')

    walk = node2vec_instance.node2vec_walk(graph=G, start_node='B')

    # The walk should stop at 'B' because it has no neighbors other than 'A'
    # from which it came. The code should handle this correctly.
    # A single walk from B can only go to A, but then it's stuck.
    # The logic handles `if not neighbors: break`
    assert len(walk) <= 5
    assert walk[-1] == 'B' or walk[-1] == 'A'