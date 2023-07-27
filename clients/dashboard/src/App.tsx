
import { TravelState, TravelContext } from './lib/travelState.tsx';


import { Outlet } from 'react-router-dom';

import useWebSocket from 'react-use-websocket';
import { useEffect } from 'react';


function App() {


  const socketUrl = import.meta.env.VITE_WS_URL as string;
  const {
    sendJsonMessage,
    lastJsonMessage,
  } = useWebSocket(socketUrl, {
    shouldReconnect: (_closeEvent) => true, reconnectAttempts: 24 * 60 * 60, reconnectInterval: 3000,
    onOpen: () => { console.log("Connection opened") },
    onClose: (_closeEvent) => { console.log("Connection closed") },
  });

  useEffect(() => {
    sendJsonMessage({
      topic: "propose_state",
      type: "init",
      concerns: "travel",
      data: null,
    })
  }, [sendJsonMessage])

  console.log(lastJsonMessage)
  if (lastJsonMessage === null) {
    return <p>Chargement...</p>
  }


  return (
    <>
      <h1>Serenity</h1>
      <TravelContext.Provider value={lastJsonMessage as TravelState}>
        <Outlet />
      </TravelContext.Provider>
    </>
  )
}

export default App
