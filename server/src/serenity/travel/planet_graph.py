import networkx as nx

from serenity.common.definitions import PlanetaryConfig


class PlanetGraph(nx.DiGraph):
    def __init__(self, planetary_config: PlanetaryConfig):
        graph = nx.node_link_graph(planetary_config.model_dump())
        super().__init__(graph)

    def to_dict(self) -> dict:
        return nx.node_link_data(self)

    def reachable_planets(self, source_id: str) -> set[str]:
        return set(nx.descendants(self, source_id))
