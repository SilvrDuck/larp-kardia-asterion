import { Flex, background } from "@chakra-ui/react";
import { useContext, useEffect, useState } from "react";
import { Background, Controls, MarkerType, MiniMap, ReactFlow, useEdgesState, useNodesState } from "reactflow";
import "reactflow/dist/style.css";
import { TravelContext } from "../lib/travelProvider";
import { WebsocketContext, InitMessage } from "../lib/websocketProvider";
import { PlanetDefault, PlanetInput, PlanetOutput } from "../components/planetNode";
import { set } from "fp-ts";

export type EdgeData = {
    towards_next_step: boolean,
}


const nodeTypes = {
    planetInput: PlanetInput,
    planetOutput: PlanetOutput,
    planetDefault: PlanetDefault,
}


function addEdgeProperties(edges: any[]) {
    return edges.map(e => {
        e.style = { strokeWidth: 1.5, stroke: "#fff" };
        e.markerEnd = { type: MarkerType.ArrowClosed, color: "#fff" }

        if (e.data.towards_next_step) {
            e.style.stroke = "#3182ce"
            e.markerEnd.color = "#3182ce"
        }

        return e
    })
}

export function PlanetGraph() {


    const { flow_graph, current_step_id } = useContext(TravelContext)
    const { sendMessage } = useContext(WebsocketContext)

    const [nodes, setNodes, onNodesChange] = useNodesState(flow_graph.nodes as []);
    const [edges, setEdges, onEdgesChange] = useEdgesState(flow_graph.edges as []);

    useEffect(() => {
        setNodes(flow_graph.nodes as [])
        setEdges(addEdgeProperties(flow_graph.edges))
    }, [flow_graph])

    useEffect(() => {
        if (current_step_id === "__init__" && sendMessage !== null) {
            console.log("sending init message")
            sendMessage(InitMessage({ concerns: "travel" }))

        }
    }, [current_step_id, sendMessage])


    if (current_step_id === "__init__") {
        return <p>Chargement...</p>
    }

    return (
        <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView>
            <Controls showInteractive={false} style={{ opacity: .3 }} />
            <Background color="#224" gap={50} size={15} variant="cross" />
        </ReactFlow>
    )
}

