
import { TravelContext } from '../lib/travelProvider.tsx';

import { useContext } from 'react';

import { WebsocketContext } from '../lib/websocketProvider.tsx';
import { Button } from '@chakra-ui/react';


export default function Test() {

    const { sendJsonMessage } = useContext(WebsocketContext)
    const travelState = useContext(TravelContext)

    return (
        <>
            <h1>Serenity</h1>
            <p>{JSON.stringify(travelState.planetary_config)}</p>
            <Button onClick={() => {
                sendJsonMessage({ topic: "coucou" })
            }
            }>Coucou</Button>
        </>
    )
}
