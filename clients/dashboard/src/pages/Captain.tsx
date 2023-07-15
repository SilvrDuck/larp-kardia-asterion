
import { useContext } from "react";
import { BattleMap } from "./BattleMap";
import { PlanetSelector } from "./PlanetSelector";
import { GameContext } from "../lib/gameContext";

function Captain() {

    const gameState = useContext(GameContext)

    if (gameState.is_in_battle) {
        return (
            <BattleMap />
        )
    }
    else {
        return (
            <PlanetSelector />
        )
    }
}

export default Captain;
