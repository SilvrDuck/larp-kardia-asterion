import { Handle, Position } from 'reactflow';
import { Planet } from './planet.tsx';
import { Avatar, Box, Button, Center, Image, useDisclosure } from '@chakra-ui/react';
import {
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    ModalCloseButton,
} from '@chakra-ui/react'


import { useContext, useEffect, useState } from 'react';
import { TravelContext } from '../lib/travelProvider.tsx';




const handleStyle = { marginTop: "12%", opacity: 0 };


function PlanetNode({ data }: { data: PlanetNodeData }) {

    return (
        <>
            <Center>
                <h2>{data.label}</h2>
            </Center>
            <Center>
                <Planet data={data} />
            </Center>
        </>
    );
}

export function PlanetInput({ data }: { data: PlanetNodeData }) {
    return (
        <>
            <PlanetNode data={data} />
            <Handle type="source" position={Position.Right} style={handleStyle} />
        </>
    );
}


export function PlanetDefault({ data }: { data: PlanetNodeData }) {
    return (
        <>
            <Handle type="target" position={Position.Left} style={handleStyle} />
            <PlanetNode data={data} />
            <Handle type="source" position={Position.Right} style={handleStyle} />
        </>
    );
}

export function PlanetOutput({ data }: { data: PlanetNodeData }) {
    return (
        <>
            <Handle type="target" position={Position.Left} style={handleStyle} />
            <PlanetNode data={data} />
        </>
    );
}