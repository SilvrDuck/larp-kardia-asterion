import logging
from typing import List, Tuple
from serenity.common.adapter import Adapter
from serenity.common.definitions import Jsonable
from serenity.common.redis_client import RedisMessage
import networkx as nx
from serenity.travel.definitions import TravelState
from serenity.travel.planet_graph import PlanetGraph


class NxToFlowAdapter(Adapter[TravelState]):
    status_model = TravelState

    @classmethod
    def _adapt(cls, model: TravelState) -> Jsonable:
        graph = PlanetGraph(model.planetary_config)
        flow_graph = cls._node_link_to_flow(graph, model.current_step_id)

        output = model.model_dump(exclude={"planetary_config"}, mode="json")
        output["flow_graph"] = flow_graph
        output["num_steps"] = nx.dag_longest_path_length(graph) + 1

        return output

    @classmethod
    def _node_link_to_flow(cls, graph: PlanetGraph, current_id: str | Tuple[str, str]) -> dict:
        """Converts a PlanetGraph to a react flow js-compatible JSON object."""

        react_graph = {}

        react_graph["nodes"] = cls._prepare_nodes(graph, current_id)
        react_graph["edges"] = cls._prepare_edges(graph, current_id)

        return react_graph

    @classmethod
    def _prepare_edges(cls, graph: PlanetGraph, current_id: str | Tuple[str, str]) -> List[dict]:
        return [
            {
                "id": f"{link['source']}-{link['target']}",
                "source": link["source"],
                "target": link["target"],
                "animated": current_id == (link["source"], link["target"]),
                "hidden": not cls._both_nodes_visible(link, graph, current_id),
            }
            for link in graph.to_dict()["links"]
        ]

    @classmethod
    def _both_nodes_visible(cls, link: dict, graph: PlanetGraph, current_id: str) -> bool:
        # get source node data
        source_data = graph.nodes[link["source"]].copy()
        target_data = graph.nodes[link["target"]].copy()
        source = cls._visible(graph, {**source_data, "id": link["source"]}, current_id)
        target = cls._visible(graph, {**target_data, "id": link["target"]}, current_id)
        return source and target

    @classmethod
    def _get_node_type(cls, graph: PlanetGraph, node_id: str) -> str:
        if graph.in_degree(node_id) == 0:
            return "planetInput"
        elif graph.out_degree(node_id) == 0:
            return "planetOutput"
        return "planetDefault"

    @classmethod
    def _prepare_nodes(cls, graph: PlanetGraph, current_id: str | Tuple[str, str]) -> List[dict]:
        is_landed = isinstance(current_id, str)
        return [
            {
                "id": node["id"],
                "type": cls._get_node_type(graph, node["id"]),
                "data": {
                    "id": node["id"],
                    "label": node["name"],
                    "description": node["description"],
                    "min_step_minutes": node["min_step_minutes"],
                    "max_step_minutes": node["max_step_minutes"],
                    "is_current": node["id"] == current_id,
                    "is_next_step": cls._is_next_step(graph, node["id"], current_id),
                    "visited": node["visited"],
                },
                "position": {"x": node["position_x"], "y": node["position_y"]},
                "hidden": not cls._visible(graph, node, current_id),
                "draggable": False,
                "selectable": is_landed and cls._is_next_step(graph, node["id"], current_id),
                "deletable": False,
            }
            for node in graph.to_dict()["nodes"]
        ]

    @classmethod
    def _is_next_step(cls, graph: PlanetGraph, target_id: str, current_id: str | Tuple[str, str]) -> bool:
        if isinstance(current_id, tuple):
            return current_id[1] == target_id

        return target_id in graph.reachable_planets(current_id)

    @classmethod
    def _visible(cls, graph: PlanetGraph, node: dict, current_id: str) -> bool:
        """We want to show only planets that have been visited or that are
        reachable from the current planet.
        """
        if node["visited"]:
            return True

        if cls._is_next_step(graph, node["id"], current_id):
            return True

        return False
