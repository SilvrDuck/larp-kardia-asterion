
import { useContext, useEffect, useState } from "react";
import { BattleMap } from "./BattleMap";
import { PlanetSelector } from "./PlanetSelector";
import { SonarContext } from "../lib/sonarProvider";
import { InitMessage, WebsocketContext } from "../lib/websocketProvider";
import { useParams } from "react-router-dom";
import { OwnerContext } from "../lib/ownerContext";

function Captain() {

    const { owner } = useParams<{ owner: string }>()
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

    if (owner !== "players" && owner !== "npcs") {
        return <p>[Hors-Jeu] APPELEZ UN PNJ SI VOUS VOYEZ ÇA. Invalid owner: {owner}, change URL!</p>
    }

    const displayed = in_battle ? <BattleMap /> : <PlanetSelector />

    return (
        <OwnerContext.Provider value={owner}>
            {displayed}
        </OwnerContext.Provider>
    )
}

export default Captain;
