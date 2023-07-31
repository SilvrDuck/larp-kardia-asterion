import { useContext } from "react"
import { useParams } from "react-router-dom"
import { SonarContext } from "../lib/sonarProvider"
import bg from "/assets/backgrounds/bg_panel.png";
import { Flex, Spacer } from '@chakra-ui/react'
import { OutOfBattle } from "../components/outOffBattle";
import { BattleControl } from "../components/battleControl";


export function Control() {

    const { owner } = useParams<{ owner: string }>()
    const { in_battle } = useContext(SonarContext)

    document.body.style.backgroundImage = `url(${bg})`

    if (in_battle === null) {
        return <p>Chargement...</p>
    }

    if (owner !== "players" && owner !== "npcs") {
        return <p>[Hors-Jeu] APPELEZ UN PNJ SI VOUS VOYEZ ÇA. Invalid owner: {owner}, change URL!</p>
    }



    if (in_battle) {
        return <BattleControl controled={owner} />
    } else {
        return (
            <Flex mt="4em">
                <Spacer />
                <OutOfBattle />
                <Spacer />
            </Flex>
        )
    }
}
