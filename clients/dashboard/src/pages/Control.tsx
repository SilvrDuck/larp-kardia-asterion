import { useContext, useEffect } from "react"
import { useParams } from "react-router-dom"
import { SonarContext } from "../lib/sonarProvider"
import bg from "/assets/backgrounds/bg_panel.png";
import { Box, Flex, Spacer, Text, VStack } from '@chakra-ui/react'
import { OutOfBattle } from "../components/outOffBattle";
import { BattleControl } from "../components/battleControl";
import { OwnerContext } from "../lib/ownerContext";
import { InitMessage, WebsocketContext } from "../lib/websocketProvider";
import { TravelContext } from "../lib/travelProvider";


export function Control() {

    const { owner } = useParams<{ owner: string }>()
    const { in_battle } = useContext(SonarContext)
    const { sendMessage } = useContext(WebsocketContext)
    const { ship_state } = useContext(TravelContext)

    useEffect(() => {
        if (in_battle === null && sendMessage !== null) {
            console.log("sending init message")
            sendMessage(InitMessage({ concerns: "sonar" }))

        }
    }, [in_battle, sendMessage])

    document.body.style.backgroundImage = `url(${bg})`

    if (in_battle === null) {
        return <p>Chargement...</p>
    }

    if (owner !== "players" && owner !== "npcs") {
        return <p>[Hors-Jeu] APPELEZ UN PNJ SI VOUS VOYEZ ÇA. Invalid owner: {owner}, change URL!</p>
    }

    const indicator = owner === "npcs" ? <Box color="white" >{ship_state}</Box> : <></>


    if (in_battle) {
        return (
            <OwnerContext.Provider value={owner}>
                <VStack>
                    <BattleControl />
                    <Spacer />
                    {indicator}
                </VStack>
            </OwnerContext.Provider>
        )
    } else {
        return (
            <VStack>
                <Flex mt="4em">
                    <Spacer />
                    <OutOfBattle />
                    <Spacer />
                </Flex>
                {indicator}
            </VStack>
        )
    }
}
