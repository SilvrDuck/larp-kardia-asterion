import {
    Card, CardHeader, CardBody, CardFooter, Text, Image, Stack, Heading,
    Divider,
    keyframes
} from '@chakra-ui/react'
import { Icon } from '@chakra-ui/react'
import { FaHourglassHalf } from 'react-icons/fa'
import { TbWaveSine } from 'react-icons/tb'
import { AiOutlineScan } from 'react-icons/ai'
import { PiScan } from 'react-icons/pi'



export function OutOfBattle() {

    const hourSize = 40

    const pulseRotate = keyframes`
	0% {
        transform: scale(0.7) rotate(60deg);
    }
    40%,
    50% {
        opacity: .8;
    }
    100% {
        opacity: 0;
    }
	`
    const animation = `2.25s ${pulseRotate} cubic-bezier(0.455, 0.03, 0.515, 0.955) -0.4s infinite`


    return (<Card maxW='sm'>
        <CardBody>
            <Text align={"center"}>
                <Icon as={PiScan} w={hourSize} h={hourSize}
                    animation={animation} margin={"auto"} />
            </Text>
            <Stack mt='6' spacing='3'>
                <Heading size='md'>Environnement pacifique</Heading>
                <Text>
                    Cette console ne s'active qu'en cas de combat.
                </Text>

            </Stack>
        </CardBody>
        <Divider />
        <CardFooter color="blue.800" >
            Radars actifs
        </CardFooter>
    </Card>)
}