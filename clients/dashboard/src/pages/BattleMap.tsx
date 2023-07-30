import bg from "@assets/backgrounds/bg_battle.png";
import { BattleGrid } from "../components/battleGrid";
import { HStack, Spacer } from "@chakra-ui/react";
import { BattleControl } from "../components/battleControl";
import { memo } from "react";


export const BattleMap = memo(function BattleMap() {


    document.body.style.backgroundImage = `url(${bg})`
    document.body.animate([
        { backgroundPositionX: "0px", backgroundPositionY: "0px" },
        { backgroundPositionX: "4096px", backgroundPositionY: "-1024px" },
    ], {
        duration: 700000,
        iterations: Infinity
    }
    )

    return (
        <>
            <HStack height="100%" width="100%" >
                <Spacer />
                <BattleGrid />
                <BattleControl />
                <Spacer />
            </HStack>
        </>
    )
})
