from typing import Self
import networkx as nx
import orjson
from serenity.common.config import settings

from serenity.common.definitions import PlanetaryConfig


class PlanetGraph(nx.DiGraph):
    def __init__(self, planetary_config: PlanetaryConfig):
        graph = nx.node_link_graph(planetary_config.model_dump())
        super().__init__(graph)

    def to_planetary_config(self) -> PlanetaryConfig:
        return PlanetaryConfig(**self.to_dict())

    def to_dict(self) -> dict:
        return nx.node_link_data(self)

    def reachable_planets(self, source_id: str) -> set[str]:
        return self.successors(source_id)

    def starting_planet(self) -> str:
        in_degrees = self.in_degree()

        candidates = []
        for node_id, in_degree in in_degrees:
            if in_degree == 0:
                candidates.append(node_id)

        if len(candidates) != 1:
            raise ValueError("Planet graph must have exactly one starting planet")

        return candidates[0]

    @classmethod
    def default_planetary_config(cls) -> PlanetaryConfig:
        with open(settings.planetary_config_path, "rb") as file:
            return PlanetaryConfig(**orjson.loads(file.read()))  # pylint: disable=no-member
