import { Box, Center, Flex, Grid, GridItem, HStack, VStack, Image, keyframes, Text } from '@chakra-ui/react'
import { SonarContext, Map } from '../lib/sonarProvider'
import { useContext, useEffect, useState } from 'react'
import { pseudoRandomRotationString, rotateAnimation } from './planet'
import { rotate } from 'fp-ts/lib/ReadonlyNonEmptyArray'
import { OwnerContext } from '../lib/ownerContext'

const gridGap = 1.5

export function idxToCol(i: number) {
    return String.fromCharCode(65 + i)
}

export function idxToRow(i: number) {
    return i + 1
}

export function rowToIdx(row: string) {
    const upper = row.toUpperCase()
    return upper.charCodeAt(0) - 65
}

export function colToIdx(col: number) {
    return col - 1
}

function pseudoRandom(x, y) {
    const low = 1
    const high = 11

    const seed = x * 10 + y
    const rand = Math.sin(seed) * 10000

    return Math.floor((rand - Math.floor(rand)) * (high - low) + low)
}

function playerTint(owner: "players" | "npcs", brightness: number = 100) {
    const rotation = owner === "players" ? "0" : "100"
    return { filter: `sepia(50%) saturate(200%) brightness(${brightness}%) hue-rotate(${rotation}deg)` }
}

const dot = <Image src="/assets/sonar/dot.png" />

function imageIfInCell(cell, hidden, type: "ship" | "trail", brightness: number = 100, animation = {}) {
    const maybeShip = cell.content.find((e) => e.type === type)
    if (maybeShip !== undefined && maybeShip.owner !== hidden) {
        return <Image src={`/assets/sonar/${type}.png`}
            animation={animation}
            style={playerTint(maybeShip.owner, brightness)} />
    }
    return null
}


function imageForCell(map: Map, x: number, y: number, hidden: "players" | "npcs") {
    const cell = map.grid[x][y]

    if (cell.has_asteroid) {
        const randAstro = pseudoRandom(x, y)
        const animate = pseudoRandomRotationString((x + y).toString())
        return <Image src={`/assets/sonar/asteroid${randAstro}.png`} animation={animate}
            style={{ filter: `sepia(70%) saturate(100%) brightness(90%) hue-rotate(180deg)` }} />
    }

    const shipImage = imageIfInCell(cell, hidden, "ship", 80)
    if (shipImage !== null) {

        return shipImage
    }

    const trailAnimation = rotateAnimation("cw", 10)
    const trailImage = imageIfInCell(cell, hidden, "trail", 100, trailAnimation)
    if (trailImage !== null) {
        return trailImage
    }

    return dot
}

function Cell({ map, row, col }: { map: Map, row: number, col: number }) {

    const owner = useContext(OwnerContext)
    const hidden = owner == "players" ? "npcs" : "players"

    const image = imageForCell(map, row, col, hidden)

    return (
        <Box height="100%" width="100%" >
            {image}
        </Box>
    )
}

function Row({ map, row }) {

    return (
        <Flex height="100%" width="100%" direction={"row"} gap={gridGap} >
            {[...Array(map.width).keys()].map((index) => (
                <Cell map={map} row={row} col={index} key={"col" + index.toString()} />
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
                        margin="auto" 
                        color="white"
                        key={"nav" + mapFunc(index).toString()}
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
        <>

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
                    `"unk col col unk2"
                    "row grid grid row2"
                    "unk3 col2 col2 unk4"`
                }
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
                    <Header dim={map.width} direction={"row"} mapFunc={idxToCol} area={"col2"} />
                    <Header dim={map.height} direction={"column"} mapFunc={idxToRow} area={"row"} />
                    <Header dim={map.height} direction={"column"} mapFunc={idxToRow} area={"row2"} />
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
                                <Row map={map} row={index} key={"row" + index.toString()} />
                            ))}

                        </Flex>
                    </GridItem>
                </Grid>
            </Flex>
        </>
    )
}