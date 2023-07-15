import { Flex } from "@chakra-ui/react";
import { Background, Controls, MiniMap, ReactFlow, useEdgesState, useNodesState } from "reactflow";
import "reactflow/dist/style.css";

export function PlanetSelector() {

    const { gameState } = useServerContext();

    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    setEdges(gameState.react_flow_graph.edges);
    setNodes(gameState.react_flow_graph.nodes);

    // should take full size of container
    return (
        <Flex h="80vh" w="80vw">
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

function useServerContext(): { gameState: any; } {
    throw new Error("Function not implemented.");
}
