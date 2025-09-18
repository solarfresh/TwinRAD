from typing import List, Literal, Optional, Set, Tuple
from uuid import uuid4

from pydantic import BaseModel, Field


class Node(BaseModel):
    label: str
    node_id: str = Field(default_factory=lambda: str(uuid4()))
    type: Literal['CentralIdea', 'MainTopic', 'SubTopic', 'Keyword']

    class ConfigDict:
        frozen = True # Makes the model immutable and hashable


class Edge(BaseModel):
    edge_id: str = Field(default_factory=lambda: str(uuid4()))
    source: str
    target: str
    type: Literal['SUPPORTS', 'LEADS_TO', 'RELATED_TO']

    class ConfigDict:
        frozen = True


class KeywordNode(Node):
    type: Literal['Keyword'] = 'Keyword'


class SubTopicNode(Node):
    type: Literal['SubTopic'] = 'SubTopic'
    keywords: List[KeywordNode] = Field(default_factory=list)
    unique_keywords: Set[Tuple[str, str]] = Field(default_factory=set, exclude=True)

    def add_keyword(self, keyword: KeywordNode):
        if (keyword.label, keyword.type) not in self.unique_keywords:
            self.keywords.append(keyword)
            self.unique_keywords.add((keyword.label, keyword.type))

class MainTopicNode(Node):
    type: Literal['MainTopic'] = 'MainTopic'
    sub_topics: List[SubTopicNode] = Field(default_factory=list)
    unique_sub_topics: Set[Tuple[str, str]] = Field(default_factory=set, exclude=True)

    def add_sub_topic(self, sub_topic: SubTopicNode):
        if (sub_topic.label, sub_topic.type) not in self.unique_sub_topics:
            self.sub_topics.append(sub_topic)
            self.unique_sub_topics.add((sub_topic.label, sub_topic.type))


class CentralIdeaNode(Node):
    type: Literal['CentralIdea'] = 'CentralIdea'
    main_topics: List[MainTopicNode] = Field(default_factory=list)
    unique_main_topics: Set[Tuple[str, str]] = Field(default_factory=set, exclude=True)

    def add_main_topic(self, main_topic: MainTopicNode):
        if (main_topic.label, main_topic.type) not in self.unique_main_topics:
            self.main_topics.append(main_topic)
            self.unique_main_topics.add((main_topic.label, main_topic.type))


class MindMap(BaseModel):
    central_idea: Optional[CentralIdeaNode] = None
    all_nodes: Set[Tuple[str, str]] = Field(default_factory=set)
    all_relationships: Set[Tuple[str, str]] = Field(default_factory=set)

    def add_node(self, node: Node):
        self.all_nodes.add((node.label, node.type))

    def add_relationship(self, relationship: Edge):
        self.all_relationships.add((relationship.source, relationship.target))
