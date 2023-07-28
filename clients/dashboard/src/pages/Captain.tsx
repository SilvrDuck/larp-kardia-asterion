
import { BattleMap } from "./BattleMap";
import { PlanetSelector } from "./PlanetSelector";

function Captain() {

    const is_in_battle = false

    if (is_in_battle) {
        return <BattleMap />
    } else {
        return <PlanetSelector />
    }
}

export default Captain;
