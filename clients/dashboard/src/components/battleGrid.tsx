import { Box, Center, Flex, Grid, GridItem, HStack, VStack, Image, keyframes } from '@chakra-ui/react'
import { SonarContext, Map } from '../lib/sonarProvider'
import { useContext, useEffect, useState } from 'react'
import { pseudoRandomRotationString } from './planet'

const gridGap = 1.5

function idxToCol(i: number) {
    return String.fromCharCode(65 + i)
}

function idxToRow(i: number) {
    return i + 1
}

function pseudoRandom(x, y) {
    const low = 1
    const high = 11

    const seed = x * 10 + y
    const rand = Math.sin(seed) * 10000

    return Math.floor((rand - Math.floor(rand)) * (high - low) + low)
}

function imageForCell(map, x, y) {
    const cell = map.grid[x][y]

    if (cell.has_asteroid) {
        const randAstro = pseudoRandom(x, y)
        const animate = pseudoRandomRotationString((x + y).toString())
        return <Image src={`src/assets/sonar/asteroid${randAstro}.png`} animation={animate}
            style={{ filter: "sepia(70%) saturate(100%) brightness(90%) hue-rotate(180deg)" }} />
    }
    if (cell.content.length > 0) {
        return <Image src="src/assets/sonar/ship.png" />
    }

    return <Image src="src/assets/sonar/dot.png" />
}

function Cell({ map, row, col }: { map: Map }) {

    const image = imageForCell(map, row, col)

    return (
        <Box color="white" height="100%" width="100%" >
            {image}
        </Box>
    )
}

function Row({ map, row }) {

    return (
        <Flex height="100%" width="100%" direction={"row"} gap={gridGap} >
            {[...Array(map.width).keys()].map((index) => (
                <Cell map={map} row={row} col={index} />
            ))}
        </Flex>
    )
}

function Header({ dim, direction, mapFunc, area }) {
    return (
        <GridItem area={area} >
            <Flex height="100%" width="100%" direction={direction} gap={gridGap} >
                {[...Array(dim).keys()].map((index) => (
                    <Box
                        height="100%" width="100%"
                        align="center" justify="center" color="white"
                    >
                        {mapFunc(index)}
                    </Box>
                ))}
            </Flex>
        </GridItem>
    )
}



export function BattleGrid() {

    const { map } = useContext(SonarContext)

    if (map === null) {
        return (
            <Center>
                <Box height="100%" width="100%">
                    Chargement...
                </Box>
            </Center>
        )
    }

    return (

        <Flex
            justify="center"
            align="center"
            height="100%"
            width="90vh"
            direction="column"
            margin="auto"
        >
            <Grid
                templateAreas={
                    `"unk col col"
                    "row grid grid"`}
                gridTemplateRows={'3em 1fr'}
                gridTemplateColumns={'3em 1fr'}
                gap={gridGap}
                color='blackAlpha.700'
                fontWeight='bold'
                pl="1.5em"
                pr="1.5em"
                pb="1.5em"
                height="100%"
                width="100%"
            >
                <Header dim={map.width} direction={"row"} mapFunc={idxToCol} area={"col"} />
                <Header dim={map.height} direction={"column"} mapFunc={idxToRow} area={"row"} />
                <GridItem area={'grid'}>
                    <Flex
                        align="center"
                        justify="center"
                        width="100%"
                        height="100%"
                        margin="auto"
                        grow="1"
                        direction="column"
                        gap={gridGap}
                    >
                        {[...Array(map.height).keys()].map((index) => (
                            <Row map={map} row={index} />
                        ))}

                    </Flex>
                </GridItem>
            </Grid>
        </Flex>

    )
}