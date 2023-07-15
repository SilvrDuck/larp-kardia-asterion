
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'

import WebsocketConnection, { ServerContext } from './lib/server.tsx'

import { GameState, RedisChannel } from './definitions.tsx';
import { Outlet } from 'react-router-dom';
import { JsonValue } from 'react-use-websocket/dist/lib/types';
import { Flex, VStack } from '@chakra-ui/react';
import { createContext, useState } from 'react';




function App() {
  //let [gameState, setGameState] = useState<GameState | null>(null)

  const {
    sendJsonMessage,
    loadingGameState,
  } = WebsocketConnection();

  if (loadingGameState === null) {
    return <p>Chargement...</p>
  }

  const [gameState, setGameState] = useState<GameState>(loadingGameState);

  return (
    <>
      <h1>Serenity</h1>

      <Outlet context={{ sendJsonMessage, gameState } satisfies ServerContext} />

    </>
  )
}

export default App
