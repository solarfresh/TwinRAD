import json
import random
from typing import Any, Dict

from networkx import Graph
from networkx.readwrite import json_graph

from twinrad.core.schemas.tools import Node2VecConfig
from twinrad.core.tools.base_tool import BaseTool


class Node2Vec(BaseTool):

    def __init__(self, config: Node2VecConfig):
        super().__init__(config=config)
        self.num_walks = config.num_walks
        self.walk_length = config.walk_length
        self.p = config.p
        self.q = config.q

    async def run(self, **kwargs) -> Any:
        """
        json_data = {
            "nodes": [
                {"id": "A", "label": "Node A"},
                {"id": "B", "label": "Node B"},
                {"id": "C", "label": "Node C"}
            ],
            "edges": [
                {"source": "A", "target": "B", "weight": 1},
                {"source": "B", "target": "C", "weight": 2}
            ]
        }
        """
        json_data_string = kwargs.get('json_data', '')
        G = json_graph.node_link_graph(json.loads(json_data_string), edges="edges")
        walks = self.generate_node2vec_walks(graph=G)
        return json.dumps(walks)

    def node2vec_walk(self, graph: Graph, start_node):
        """
        Generates a single random walk starting from start_node.
        p: Return parameter
        q: In-out parameter
        """
        walk = [str(start_node)]

        for _ in range(self.walk_length - 1):
            current_node = walk[-1]
            neighbors = list(graph.neighbors(current_node))

            if not neighbors:
                break

            next_node = None

            # Calculate transition probabilities
            # This is a simplified version for demonstration
            # A full implementation would involve more complex probability calculations

            # Get previous node in the walk
            previous_node = str(walk[-2]) if len(walk) > 1 else None

            probabilities = {}
            total_prob = 0

            for neighbor in neighbors:
                neighbor = str(neighbor)
                prob = 1.0  # Base probability

                # Distance from previous node
                dist = 0
                if previous_node is not None:
                    if neighbor == previous_node:
                        dist = 0
                    elif graph.has_edge(previous_node, neighbor):
                        dist = 1
                    else:
                        dist = 2

                # Apply p and q parameters
                if dist == 0:
                    prob = 1 / self.p
                elif dist == 1:
                    prob = 1
                elif dist == 2:
                    prob = 1 / self.q

                probabilities[neighbor] = prob
                total_prob += prob

            # Normalize probabilities and choose the next node
            normalized_probs = [probabilities[n] / total_prob for n in neighbors]
            next_node = random.choices(neighbors, weights=normalized_probs)[0]

            walk.append(str(next_node))

        return walk

    def generate_node2vec_walks(self, graph: Graph):
        """
        Generates multiple random walks for all nodes in the graph.
        """
        walks = []
        nodes = list(graph.nodes())
        for _ in range(self.num_walks):
            random.shuffle(nodes)
            for node in nodes:
                walk = self.node2vec_walk(graph, node)
                walks.append(walk)

        return walks

    def get_name(self) -> str:
        return "node2vec"

    def get_description(self) -> str:
        return "Generates biased random walks on a graph to learn node embeddings. The walks are configured by the return parameter 'p' and the in-out parameter 'q'."

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "json_data": {
                    "type": "string",
                    "description": "A JSON string representing the graph with 'nodes' and 'links' fields, following the networkx node-link data format."
                },
                "num_walks": {
                    "type": "integer",
                    "description": "The number of random walks to generate starting from each node. Default is 10."
                },
                "walk_length": {
                    "type": "integer",
                    "description": "The length of each random walk. Default is 80."
                },
                "p": {
                    "type": "number",
                    "description": "The return parameter 'p', controlling the probability of immediately revisiting a node. A high 'p' discourages revisiting. Default is 1.0."
                },
                "q": {
                    "type": "number",
                    "description": "The in-out parameter 'q', controlling the probability of exploring new nodes. A high 'q' encourages exploration, while a low 'q' encourages staying local. Default is 1.0."
                }
            },
            "required": ["json_data"]
        }
