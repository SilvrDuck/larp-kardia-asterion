import { useContext } from "react"
import { SonarContext } from "../lib/sonarProvider"
import { ShipStatus } from "./shipStatus"
import { Badge, Card, CardBody, HStack, Stack, Text, VStack } from "@chakra-ui/react"
import { SonarConfigContext } from "../lib/sonarConfigProvider"

function WeaponInfo({ name, reach, radius, damage }) {

    return <>
        <Stack direction='row' >
            <Card>
                <CardBody p="0" pr="1" pl="1">
                    {name}:
                    <Badge ml="2" colorScheme='green'>Portée: {reach}</Badge>
                    <Badge ml="2" colorScheme='purple'>Rayon: {radius}</Badge>
                    <Badge ml="2" colorScheme='red'>Dégats: {damage}</Badge>
                </CardBody>
            </Card>
        </Stack>
    </>
}

export function BattleInfo() {

    const { map } = useContext(SonarContext)
    const { torpedo_reach, mine_reach, torpedo_radius, mine_radius, mine_damage, torpedo_damage } = useContext(SonarConfigContext)

    return (
        <>
            <VStack align={"right"}  mr="2em">
                <WeaponInfo name="Torpilles" reach={torpedo_reach} radius={torpedo_radius} damage={torpedo_damage} />
                <WeaponInfo name="Mines" reach={mine_reach} radius={mine_radius} damage={mine_damage} />
            </VStack>
            <ShipStatus ship={map!.npc_ship} />
            <Text fontSize="2xl" color="blue.300" pl="1.5em" pr="1.5em" >VS</Text>
            <ShipStatus ship={map!.player_ship} />
        </>
    )
}