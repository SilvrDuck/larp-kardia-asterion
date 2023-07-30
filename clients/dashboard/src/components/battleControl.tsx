import { Button, Grid, GridItem, HStack, VStack } from "@chakra-ui/react";
import { useContext } from "react";
import { WebsocketContext } from "../lib/websocketProvider";




function Directions() {

    const { sendMessage } = useContext(WebsocketContext)

    const move = (direction: string) => {
        sendMessage({
            topic: "command",
            type: "move",
            concerns: "sonar",
            data: {
                owner: "npcs",
                direction: direction,
            },
        })
    }

    return (
        <VStack>
            <Button onClick={() => move("north")}>N</Button>
            <HStack>
                <Button onClick={() => move("west")}>O</Button>
                <Button onClick={() => move("east")}>E</Button>
            </HStack>
            <Button onClick={() => move("south")}>S</Button>
        </VStack>
    )
}

export function BattleControl() {

    return (
        <>
            <VStack pr="1em">
                <Directions />
            </VStack>
        </>
    )
}