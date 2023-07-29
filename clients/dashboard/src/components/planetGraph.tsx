import { Flex } from "@chakra-ui/react";
import { useContext, useEffect } from "react";
import { Background, Controls, MiniMap, ReactFlow, useEdgesState, useNodesState } from "reactflow";
import "reactflow/dist/style.css";
import { TravelContext } from "../lib/travelProvider";
import { WebsocketContext, initMessage } from "../lib/websocketProvider";
import { PlanetDefault, PlanetInput, PlanetOutput } from "../components/planetNode";

const nodeTypes = {
    planetInput: PlanetInput,
    planetOutput: PlanetOutput,
    planetDefault: PlanetDefault,
}

export function PlanetGraph() {

    const { flow_graph, current_step_id } = useContext(TravelContext)
    const { sendMessage } = useContext(WebsocketContext)

    const [nodes, setNodes, onNodesChange] = useNodesState(flow_graph.nodes as []);
    const [edges, setEdges, onEdgesChange] = useEdgesState(flow_graph.edges as []);

    useEffect(() => {
        setNodes(flow_graph.nodes as [])
        setEdges(flow_graph.edges as [])
    }, [flow_graph])

    if (current_step_id === "__init__" && sendMessage !== null) {
        console.log("sending init message")
        sendMessage(initMessage)
    }

    if (current_step_id === "__init__") {
        return <p>loading...</p>
    }

    return (
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                fitView>
                <MiniMap style={{ height: 120 }} zoomable pannable />
                <Controls />
                <Background color="#222" gap={50} size={15} variant="cross" />
            </ReactFlow>
    )
}

