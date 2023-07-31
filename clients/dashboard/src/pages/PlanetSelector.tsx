import { Flex, Stepper, VStack } from "@chakra-ui/react";
import { useContext, useEffect } from "react";
import { Background, Controls, MiniMap, ReactFlow, useEdgesState, useNodesState } from "reactflow";
import "reactflow/dist/style.css";
import { TravelContext } from "../lib/travelProvider";
import { WebsocketContext } from "../lib/websocketProvider";
import { PlanetDefault, PlanetInput, PlanetOutput } from "../components/planetNode";
import { PlanetGraph } from "../components/planetGraph";
import { PlanetCounter } from "../components/planetCounter";
import bg from "/assets/backgrounds/bg_graph.png";



export function PlanetSelector() {

    document.body.style.backgroundImage = `url(${bg})`
    document.body.animate([
        { backgroundPositionX: "0px", backgroundPositionY: "0px" },
        { backgroundPositionX: "4096px", backgroundPositionY: "-1024px" },
    ], {
        duration: 300000,
        iterations: Infinity
    }
    )

    return (
        <>
            <PlanetGraph />
        </>
    )
}

