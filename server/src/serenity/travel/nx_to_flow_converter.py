from typing import List, Tuple

from serenity.common.definitions import PlanetaryConfig
from serenity.travel.planet_graph import PlanetGraph


class NxToFlowGraphConverter:
    def __init__(self, graph: PlanetGraph) -> None:
        self._graph = graph
        self._node_link_data = graph.to_dict()

    def node_link_to_flow(self, current_id: str | Tuple[str, str]) -> dict:
        """Converts a PlanetGraph to a react flow js-compatible JSON object."""

        react_graph = {}

        react_graph["nodes"] = self._prepare_nodes(current_id)
        react_graph["edges"] = self._prepare_edges(current_id)

        return react_graph

    def _prepare_edges(self, current_id: str | Tuple[str, str]) -> List[dict]:
        return [
            {
                "id": f"{link['source']}-{link['target']}",
                "source": link["source"],
                "target": link["target"],
                "animated": current_id == (link["source"], link["target"]),
                "hidden": not self._both_nodes_visible(link, current_id),
            }
            for link in self._node_link_data["links"]
        ]

    def _both_nodes_visible(self, link: dict, current_id: str) -> bool:
        # get source node data
        source_data = self._graph.nodes[link["source"]].copy()
        target_data = self._graph.nodes[link["target"]].copy()
        source = self._visible({**source_data, "id": link["source"]}, current_id)
        target = self._visible({**target_data, "id": link["target"]}, current_id)
        return source and target

    def _get_node_type(self, node_id: str) -> str:
        if self._graph.in_degree(node_id) == 0:
            return "input"
        elif self._graph.out_degree(node_id) == 0:
            return "output"
        return "default"

    def _prepare_nodes(self, current_id: str | Tuple[str, str]) -> List[dict]:
        is_landed = isinstance(current_id, str)
        return [
            {
                "id": node["id"],
                "type": self._get_node_type(node["id"]),
                "data": {
                    "label": node["name"],
                    "description": node["description"],
                    "min_step_minutes": node["min_step_minutes"],
                    "max_step_minutes": node["max_step_minutes"],
                    "is_current": node["id"] == current_id,
                },
                "position": {"x": node["position_x"], "y": node["position_y"]},
                "hidden": not self._visible(node, current_id),
                "draggable": False,
                "selectable": is_landed and self._is_next_step(node["id"], current_id),
                "deletable": False,
            }
            for node in self._node_link_data["nodes"]
        ]

    def _is_next_step(self, target_id: str, current_id: str | Tuple[str, str]) -> bool:
        if isinstance(current_id, tuple):
            return current_id[1] == target_id

        return target_id in self._graph.reachable_planets(current_id)

    def _visible(self, node: dict, current_id: str) -> bool:
        """We want to show only planets that have been visited or that are
        reachable from the current planet.
        """
        if node["visited"]:
            return True

        if self._is_next_step(node["id"], current_id):
            return True

        return False
