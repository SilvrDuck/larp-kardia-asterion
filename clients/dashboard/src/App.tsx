

import { GameState } from './definitions.tsx';
import { Outlet } from 'react-router-dom';

import { GameContext } from './lib/gameContext.tsx';
import useWebSocket from 'react-use-websocket';




function App() {


  const socketUrl = import.meta.env.VITE_WS_URL as string;
  const {
    sendJsonMessage,
    lastJsonMessage,
  } = useWebSocket(socketUrl, { shouldReconnect: (_closeEvent) => true, reconnectAttempts: 24 * 60 * 60, reconnectInterval: 3000 });

  if (lastJsonMessage === null) {
    return <p>Chargement...</p>
  }

  return (
    <>
      <h1>Serenity</h1>

      <GameContext.Provider value={lastJsonMessage as GameState}>
        <Outlet />
      </GameContext.Provider>

    </>
  )
}

export default App
