import { Flex } from "@chakra-ui/react";
import { useContext, useEffect } from "react";
import { Background, Controls, Edge, MiniMap, ReactFlow, useEdgesState, useNodesState } from "reactflow";
import "reactflow/dist/style.css";
import { TravelContext } from "../lib/travelProvider";
import { WebsocketContext } from "../lib/websocketProvider";

export function PlanetSelector() {

    const { } = useContext(TravelContext)

    const { flow_graph, current_step_id } = useContext(TravelContext)
    console.log("from planet " + current_step_id)
    console.log("with conf" + JSON.stringify(flow_graph))

    const [nodes, setNodes, onNodesChange] = useNodesState(flow_graph.nodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(flow_graph.edges);

    useEffect(() => {
        setNodes(flow_graph.nodes)
        setEdges(flow_graph.edges)
    }, [flow_graph])

    // should take full size of container
    return (
        <Flex h="80vh" w="80vw">
            <p>{current_step_id}</p>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                fitView>
                <MiniMap style={{ height: 120 }} zoomable pannable />
                <Controls />
                <Background color="#aaa" gap={16} />
            </ReactFlow>
        </Flex>
    )
}

