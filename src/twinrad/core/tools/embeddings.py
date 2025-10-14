import json
import random
from itertools import chain
from typing import Any, Dict

from networkx import Graph
from networkx.readwrite import json_graph

from twinrad.core.schemas.tools import Node2VecConfig
from twinrad.core.tools.base_tool import BaseTool

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset

    using_torch = True
except ImportError:
    using_torch = False


class Node2VecWalker:

    def __init__(self, num_walks: int, walk_length: int, p = 1.0, q = 1.0):
        self.num_walks = num_walks
        self.walk_length = walk_length
        self.p = p
        self.q = q

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


if using_torch:
    class Word2Vec(nn.Module):
        def __init__(self, vocab_size, embedding_dim):
            super().__init__()
            self.vocab_size = vocab_size
            self.embedding_dim = embedding_dim

            # Two embedding layers: one for center nodes, one for context nodes
            self.center_embeddings = nn.Embedding(self.vocab_size, self.embedding_dim)
            self.context_embeddings = nn.Embedding(self.vocab_size, self.embedding_dim)

        def forward(self, center, context):
            center_embeds = self.center_embeddings(center)
            context_embeds = self.context_embeddings(context)

            # Calculate dot product as the similarity score
            score = torch.sum(center_embeds * context_embeds, dim=1)

            return score


    class Node2Vec(BaseTool):
        class Node2VecDataset(Dataset):
            def __init__(self, walks, window_size):
                self.data = []

                # Build vocabulary and map nodes to integers
                self.node_to_idx = {node: i for i, node in enumerate(set(chain(*walks)))}
                self.idx_to_node = {i: node for node, i in self.node_to_idx.items()}
                self.vocab_size = len(self.node_to_idx)

                # Create (center, context) pairs
                for walk in walks:
                    indexed_walk = [self.node_to_idx[node] for node in walk]
                    for i, center_node_idx in enumerate(indexed_walk):
                        context_nodes = indexed_walk[max(0, i - window_size) : i] + \
                                        indexed_walk[i + 1 : i + window_size + 1]
                        for context_node_idx in context_nodes:
                            self.data.append((center_node_idx, context_node_idx))

            def __len__(self):
                return len(self.data)

            def __getitem__(self, idx):
                center, context = self.data[idx]
                return center, context

        def __init__(self, config: Node2VecConfig) -> None:
            super().__init__(config)

            self.config = config
            self.node2vec_walker = Node2VecWalker(
                num_walks=config.num_walks,
                walk_length=config.walk_length,
                p=config.p,
                q=config.q
            )

        async def run(self, **kwargs) -> Any:
            walks = await self.node2vec_walker.run(**kwargs)
            dataset = self.Node2VecDataset(json.loads(walks), self.config.window_size)
            dataloader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=True)

            word2vec = Word2Vec(vocab_size=dataset.vocab_size, embedding_dim=self.config.embedding_dim)
            criterion = nn.BCEWithLogitsLoss()
            optimizer = optim.Adam(word2vec.parameters(), lr=self.config.learning_rate)

            self.fit(word2vec, dataset, dataloader, criterion, optimizer)
            embeddings = word2vec.center_embeddings.weight.data
            node_embeddings = {dataset.idx_to_node[i]: embeddings[i].tolist() for i in range(dataset.vocab_size)}
            return json.dumps(node_embeddings)

        def fit(self, word2vec, dataset, dataloader, criterion, optimizer):
            if self.config.steps_per_epoch is None:
                steps_per_epoch = len(dataloader)
            else:
                steps_per_epoch = self.config.steps_per_epoch

            for epoch in range(self.config.epochs):
                total_loss = 0
                steps = 0
                for center_nodes, context_nodes in dataloader:
                    if steps > steps_per_epoch:
                        break

                    steps += 1
                    # Negative sampling (simplified)
                    neg_samples = torch.randint(0, dataset.vocab_size, (center_nodes.size(0), 5))

                    optimizer.zero_grad()

                    # Positive loss
                    pos_scores = word2vec(center_nodes, context_nodes)
                    pos_loss = criterion(pos_scores, torch.ones_like(pos_scores))

                    # Negative loss
                    neg_scores = word2vec(center_nodes.repeat(neg_samples.size(1)), neg_samples.flatten())
                    neg_loss = criterion(neg_scores, torch.zeros_like(neg_scores))

                    loss = pos_loss + neg_loss
                    loss.backward()
                    optimizer.step()

                    total_loss += loss.item()

                self.logger.info(f"Epoch {epoch+1}/{self.config.epochs}, Loss: {total_loss / steps_per_epoch:.4f}")

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
