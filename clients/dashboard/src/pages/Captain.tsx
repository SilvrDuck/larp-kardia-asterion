
import { useServerContext } from "../lib/server";
import { BattleMap } from "./BattleMap";
import { PlanetSelector } from "./PlanetSelector";

function Captain() {

    const { gameState } = useServerContext();

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
