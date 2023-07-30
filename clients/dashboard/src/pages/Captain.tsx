
import { useContext, useEffect, useState } from "react";
import { BattleMap } from "./BattleMap";
import { PlanetSelector } from "./PlanetSelector";
import { SonarContext } from "../lib/sonarProvider";
import { InitMessage, WebsocketContext } from "../lib/websocketProvider";

function Captain() {

    const { in_battle } = useContext(SonarContext)
    const { sendMessage } = useContext(WebsocketContext)

    useEffect(() => {
        if (in_battle === null && sendMessage !== null) {
            console.log("sending init message")
            sendMessage(InitMessage({ concerns: "sonar" }))

        }
    }, [in_battle, sendMessage])

    if (in_battle === null) {
        return <p>Chargement...</p>
    }

    if (in_battle) {
        return <BattleMap />
    } else {
        return <PlanetSelector />
    }
}

export default Captain;
