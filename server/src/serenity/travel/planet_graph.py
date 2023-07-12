from typing import List
import networkx as nx
from pydantic import BaseModel
from pydantic.fields import Field


class PlanetNode(BaseModel):
    id: str
    name: str
    description: str
    min_stop_minutes: float = Field(
        ..., description="Minimum time to stop in minutes", ge=0
    )
    max_stop_minutes: float = Field(
        ..., description="Maximum time to stop in minutes", ge=0
    )


class PlanetLink(BaseModel):
    source: str
    target: str
    travel_minutes: float = Field(..., description="Travel time in minutes", ge=0)


class PlanetaryConfig(BaseModel):
    directed: bool = True
    multigraph: bool = False
    nodes: List[PlanetNode]
    links: List[PlanetLink]


class PlanetGraph(nx.DiGraph):
    def __init__(self, planetary_config: PlanetaryConfig):
        graph = nx.node_link_graph(planetary_config.model_dump())
        super().__init__(graph)
