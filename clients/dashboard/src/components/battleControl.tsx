import { Button, Grid, Text, GridItem, HStack, Heading, PinInput, PinInputField, Radio, Select, Spacer, VStack, position } from "@chakra-ui/react";
import { useCallback, useContext, useEffect, useState } from "react";
import { InitMessage, WebsocketContext } from "../lib/websocketProvider";
import { Position, SonarContext } from "../lib/sonarProvider";
import { colToIdx, rowToIdx, idxToCol, idxToRow } from "./battleGrid";
import { set } from "fp-ts";
import { OwnerContext } from "../lib/ownerContext";
import { TravelContext } from "../lib/travelProvider";
import { SonarConfigContext } from "../lib/sonarConfigProvider";




function Directions() {

    const { sendMessage } = useContext(WebsocketContext)
    const owner = useContext(OwnerContext)

    const move = (direction: string) => {
        sendMessage!({
            topic: "command",
            type: "move",
            concerns: "sonar",
            data: {
                owner: owner,
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

function Launcher({ target, submit }: { target: "launch_torpedo" | "launch_mine", submit: string }) {

    const [x, setX] = useState("")
    const [y, setY] = useState("")
    const { sendMessage } = useContext(WebsocketContext)
    const owner = useContext(OwnerContext)
    const { map } = useContext(SonarContext)

    const fire = (e) => {
        e.preventDefault()

        sendMessage!({
            topic: "command",
            type: target,
            concerns: "sonar",
            data: {
                owner: owner,
                target: {
                    x: rowToIdx(x!),
                    y: colToIdx(parseInt(y!)),
                } as Position,
            },
        })
        setY("")
        setX("")
    }

    return (
        <HStack>
            <Select placeholder='#' onChange={(e) => setX(e.target.value)} value={x}>
                {[...Array(map?.width).keys()].map((index) => idxToCol(index)).map(
                    (index) => (
                        <option
                            key={"select" + index.toString()}
                            value={index}
                        >{index}
                        </option>
                    )
                )}
            </Select>
            <Select placeholder='#' onChange={(e) => setY(e.target.value)} value={y}>
                {[...Array(map?.height).keys()].map((index) => idxToRow(index)).map(
                    (index) => (
                        <option
                            key={"select" + index.toString()}
                            value={index}
                        >{index}
                        </option>
                    )
                )}
            </Select>
            <Button onClick={fire} type="submit" >{submit}</Button>

        </HStack >
    )
}

function Mines() {

    const { map } = useContext(SonarContext)
    const { sendMessage } = useContext(WebsocketContext)

    const mines = map!.mine_positions

    function handleMine(uid: string) {
        return (e) => {
            e.preventDefault()

            sendMessage!({
                topic: "command",
                type: "detonate_mine",
                concerns: "sonar",
                data: { mine_uid: uid }
            },
            )
        }

    }

    return (
        <>
            <VStack>
                {
                    Object.entries(mines).map(([uid, position]) =>
                    (
                        <HStack key={uid}>
                            <Text fontSize="xl" fontWeight={"bold"}>
                                {idxToCol(position.x)} {idxToRow(position.y)}
                            </Text>
                            <Button onClick={handleMine(uid)} type="submit" >Détonner</Button>
                        </HStack>
                    )
                    )
                }
            </VStack>
        </>
    )
}


export function BattleControl() {

    const { use_control_panel } = useContext(SonarConfigContext)
    const owner = useContext(OwnerContext)

    const displayDirection = owner === "npcs" || !use_control_panel
    const directions = displayDirection ? <Directions /> : <></>

    return (
        <>
            <VStack pr="1em">
                {directions}
                <Spacer />
                <Heading size="md">Torpille</Heading>
                <Launcher target="launch_torpedo" submit="Feu" />
                <Spacer />
                <Heading size="md">Mines</Heading>
                <Launcher target="launch_mine" submit="Poser" />
                <Mines />
                <Spacer />
            </VStack>
        </>
    )
}