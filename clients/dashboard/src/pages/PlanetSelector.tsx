import { Flex } from "@chakra-ui/react";
import { useContext, useEffect } from "react";
import { Background, Controls, Edge, MiniMap, ReactFlow, useEdgesState, useNodesState } from "reactflow";
import "reactflow/dist/style.css";
import { TravelContext } from "../lib/travelState";

export function PlanetSelector() {

    const { react_flow_graph, current_step_id } = useContext(TravelContext)
    console.log("from planet" + react_flow_graph.toString())

    const [nodes, setNodes, onNodesChange] = useNodesState(react_flow_graph.nodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(react_flow_graph.edges);

    useEffect(() => {
        setNodes(react_flow_graph.nodes)
        setEdges(react_flow_graph.edges)
    }, [react_flow_graph])

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

