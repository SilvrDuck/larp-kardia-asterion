import { Handle, Position } from 'reactflow';
import { Planet } from './planet.tsx';
import { Avatar, Box, Button, Image, useDisclosure } from '@chakra-ui/react';
import {
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    ModalCloseButton,
} from '@chakra-ui/react'

import image from '@assets/plan_2.png';
import { useContext, useEffect, useState } from 'react';
import { TravelContext } from '../lib/travelProvider.tsx';




const handleStyle = { background: '#555', top: "200" };




function PlanetNode({ data }: { data: PlanetNodeData }) {

    return (
        <>
            <p>{data.label}</p>
            <Planet data={data} src={image} />
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