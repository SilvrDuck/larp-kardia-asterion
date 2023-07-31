import { Button, Grid, GridItem, HStack, Heading, PinInput, PinInputField, Spacer, VStack } from "@chakra-ui/react";
import { useCallback, useContext, useState } from "react";
import { WebsocketContext } from "../lib/websocketProvider";
import { Position } from "../lib/sonarProvider";
import { colToIdx, rowToIdx } from "./battleGrid";
import { set } from "fp-ts";




function Directions({ controled }: { controled: "players" | "npcs" }) {

    const { sendMessage } = useContext(WebsocketContext)

    const move = (direction: string) => {
        sendMessage!({
            topic: "command",
            type: "move",
            concerns: "sonar",
            data: {
                owner: controled,
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

function Launcher({ controled }: { controled: "players" | "npcs" }) {

    const [x, setX] = useState("")
    const [y, setY] = useState("")
    const { sendMessage } = useContext(WebsocketContext)

    const fire = (e) => {
        e.preventDefault()

        sendMessage!({
            topic: "command",
            type: "launch_torpedo",
            concerns: "sonar",
            data: {
                owner: controled,
                target: {
                    x: rowToIdx(x!),
                    y: colToIdx(parseInt(y!)),
                } as Position,
            },
        })
    }

    return (
        <HStack>
            <PinInput type='alphanumeric'>
                <PinInputField value={x} onChange={(e) => setX(e.target.value)} />
                <PinInputField value={y} onChange={(e) => setY(e.target.value)} />
            </PinInput>
            <Button onClick={fire} type="submit" >Fire</Button>
        </HStack>
    )
}

export function BattleControl({ controled }: { controled: "players" | "npcs" }) {

    return (
        <>
            <VStack pr="1em">
                <Directions controled={controled} />
                <Spacer />
                <Heading size="md">Torpedo</Heading>
                <Launcher controled={controled} />
                <Spacer />
            </VStack>
        </>
    )
}