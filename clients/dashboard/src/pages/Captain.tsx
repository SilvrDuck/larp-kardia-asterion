
import { useContext } from "react";
import { BattleMap } from "./BattleMap";
import { PlanetSelector } from "./PlanetSelector";
import { TravelContext } from "../lib/travelState";

function Captain() {

    const travelState = useContext(TravelContext)

    if (travelState.is_in_battle) {
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
