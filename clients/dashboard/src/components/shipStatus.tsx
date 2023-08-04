import { HStack, Progress, Text, VStack } from "@chakra-ui/react";
import { Ship } from "../lib/sonarProvider";

export function ShipStatus({ ship }: { ship: Ship }) {

    const color = ship.owner === "players" ? "white" : "tomato"

    const lowHp = ship.hp > 1 ? "orange" : "red"
    const colorScheme = ship.hp > 2 ? "green" : lowHp

    return (
        <HStack>
            <Text fontWeight={"bold"}
                fontSize="2xl" pr="0.5em" color={color}>{ship.name}</Text>
            <Progress colorScheme={colorScheme}
                value={ship.hp} max={ship.total_hp} width="100px" height="20px" />
            <Text fontSize="2xl">{ship.hp} PV</Text>
        </HStack>
    )
}