import { Avatar, Box, keyframes, Tooltip } from '@chakra-ui/react'
import { PlanetNodeData } from './planetNode';
import { Button, useDisclosure } from '@chakra-ui/react';
import {
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    ModalCloseButton,
} from '@chakra-ui/react'
import { useCallback, useContext } from 'react';
import { TravelContext } from '../lib/travelProvider';
import { WebsocketContext, WebsocketMessage } from '../lib/websocketProvider';


export type PlanetNodeData = {
    id: string,
    label: string,
    description: string,
    min_step_minutes: number,
    max_step_minutes: number,
    is_current: boolean,
    is_next_step: boolean,
}



function PlanetModal({ isOpen, onClose, planetId, sendMessage }) {


    const takeoff = () => {
        sendMessage({
            topic: "command",
            type: "takeoff",
            concerns: "travel",
            data: planetId,
        } as WebsocketMessage)
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <ModalOverlay />
            <ModalContent>
                <ModalHeader>Modal Title</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    Lolilol
                </ModalBody>

                <ModalFooter>
                    <Button colorScheme='blue' mr={3} onClick={takeoff}>
                        Décoller !
                    </Button>
                    <Button variant='ghost' onClick={onClose} >Annuler</Button>
                </ModalFooter>
            </ModalContent>
        </Modal>
    )
}


function PlanetButton({ data, src, size }: { data: PlanetNodeData, src: string, size: string }) {
    const { ship_state } = useContext(TravelContext)
    const { isOpen, onOpen, onClose } = useDisclosure()
    const { sendMessage } = useContext(WebsocketContext)

    console.log("rendering planet node", data.is_next_step)
    console.log("ship state", ship_state)

    const modal = data.is_next_step && ship_state == "landed" && sendMessage != null ? PlanetModal(
        { isOpen, onClose, planetId: data.id, sendMessage }
    ) : <div></div>

    return (
        <>
            <Box as="button" onClick={onOpen}>
                <Tooltip label={data.description}>
                    <Avatar
                        src={src}
                        size="full"
                        position="absolute"
                        top={size}
                        _hover={{
                            transform: 'scale(1.1)',
                            transition: 'transform .2s',
                        }}
                    />
                </Tooltip>
            </Box>
            {modal}
        </>
    )
}


export function Planet({ data, src }: { data: PlanetNodeData, src: string }) {

    const size = '80px'
    const color = 'teal'

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

    const planetButton = PlanetButton({ data, src, size })

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


