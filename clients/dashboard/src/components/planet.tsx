import { Avatar, Badge, Box, ButtonGroup, Divider, Heading, keyframes, Spacer, Stat, StatLabel, StatNumber, Tooltip } from '@chakra-ui/react'

import { Button, useDisclosure } from '@chakra-ui/react';
import {
    Text,
    Image,
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    ModalCloseButton,
    Stack,
} from '@chakra-ui/react'
import { useCallback, useContext } from 'react';
import { TravelContext } from '../lib/travelProvider';
import { WebsocketContext, WebsocketMessage } from '../lib/websocketProvider';
import { Card, CardHeader, CardBody, CardFooter } from '@chakra-ui/react'
import image from '@assets/plan_2.png';
import { getPlanetImage } from '../lib/planetImage';
import { get } from 'fp-ts/lib/FromState';


export type PlanetNodeData = {
    id: string,
    label: string,
    description: string,
    min_step_minutes: number,
    max_step_minutes: number,
    is_current: boolean,
    is_next_step: boolean,
    visited: boolean,
    radius: string,
    period: string,
    satellites: string,
}



function PlanetModal({ isOpen, onClose, data, sendMessage }) {


    const takeoff = () => {
        sendMessage({
            topic: "command",
            type: "takeoff",
            concerns: "travel",
            data: data.id,
        } as WebsocketMessage)
    }

    const planetCard = (<Card maxW='sm' backgroundColor="#def">
        <CardBody>
            <Image
                src={getPlanetImage(data.id)}
                borderRadius='lg'
            />
            <Stack mt='6' spacing='3'>
                <Heading size='md' color="blue.800" >{data.label}</Heading>
                <h3 >Rayon équatorial</h3>
                <Badge >{data.radius}</Badge>
                <h3>Période de révolution</h3>
                <Badge>{data.period}</Badge>
                <h3>Satellites connus</h3>
                <Badge >{data.satellites}</Badge>
                <Text mt='3'>
                    <p>{data.description}</p>
                </Text>
            </Stack>
        </CardBody>
    </Card >)

    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <ModalOverlay />
            <ModalContent backgroundColor="blue.800" >
                <ModalHeader>Décollage</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    {planetCard}
                    <Box mt="1em">
                        <p>Êtes-vous sûr de vouloir décoller vers {data.label} ?</p>
                    </Box>
                </ModalBody>

                <ModalFooter>
                    <Button
                        colorScheme='blue'
                        mr={3}
                        onClick={takeoff}
                        _hover={{
                            bg: "blue.300",
                        }}
                    >
                        Décoller !
                    </Button>
                    <Button
                        variant='ghost'
                        onClick={onClose}
                        color="white"
                        _hover={{
                            bg: "blue.700",
                        }}
                    >
                        Annuler
                    </Button>
                </ModalFooter>
            </ModalContent>
        </Modal>
    )
}

export function pseudoRandomRotationString(label: string) {
    const randInt = label.charCodeAt(17 % label.length)
    const min = "A".charCodeAt(0)
    const max = "z".charCodeAt(0)
    // there might be other chars than letters, but that will be spatial anomalies
    const norm = (randInt - min) / (max - min)

    const lower = 40
    const upper = 80
    const speed = lower + (norm * (upper - lower))


    const sign = label.charCodeAt(11 % label.length) % 2 == 0 ? "" : "-"
    const animationKeyframes = keyframes`
    100% { transform: rotate(${sign}360deg); }
    `;

    return `${animationKeyframes} ${speed}s infinite linear`
}



function PlanetButton({ data }: { data: PlanetNodeData }) {
    const { ship_state } = useContext(TravelContext)
    const { isOpen, onOpen, onClose } = useDisclosure()
    const { sendMessage } = useContext(WebsocketContext)

    const modal = data.is_next_step && ship_state == "landed" && sendMessage != null ? PlanetModal(
        { isOpen, onClose, data, sendMessage }
    ) : <div></div>


    const animation = pseudoRandomRotationString(data.label)

    const greyedOut = !data.is_next_step && !data.visited

    return (
        <>
            <Box as="button" onClick={onOpen}>
                <Tooltip label={data.description}>

                    <Avatar
                        src={getPlanetImage(data.id)}
                        size="full"
                        position="absolute"
                        top="0"
                        _hover={{
                            transform: 'scale(1.1)',
                            transition: 'transform .2s',
                        }}
                        animation={animation}
                        style={greyedOut ? { filter: "brightness(30%)" } : {}}

                    />

                </Tooltip>
            </Box>
            {modal}
        </>
    )
}


export function Planet({ data }: { data: PlanetNodeData }) {

    const size = '80px'
    const color = 'blue.500'

    const baseOpacity = data.is_current ? 1 : 0

    const pulseRing = keyframes`
	0% {
        opacity: ${baseOpacity};
        transform: scale(0.33);
    }
    40%,
    50% {
        opacity: 0;
    }
    100% {
        opacity: 0;
    }
	`

    const planetButton = PlanetButton({ data })

    return (
        <Box
            as="div"
            position="relative"
            w={size}
            h={size}
            _before={{
                content: "''",
                position: 'relative',
                display: 'block',
                width: '300%',
                height: '300%',
                boxSizing: 'border-box',
                marginLeft: '-100%',
                marginTop: '-100%',
                borderRadius: '50%',
                bgColor: color,
                animation: `2.25s ${pulseRing} cubic-bezier(0.455, 0.03, 0.515, 0.955) -0.4s infinite`,
            }}
        >
            {planetButton}
        </Box>
    )
}


