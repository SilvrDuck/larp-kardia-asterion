
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import WebsocketConnection from './lib/server.tsx'

import { GameState, RedisChannel } from './definitions.tsx';


function App() {
  //let [gameState, setGameState] = useState<GameState | null>(null)

  const {
    sendJsonMessage,
    lastJsonMessage,
  } = WebsocketConnection();

  const gameState = lastJsonMessage as GameState;

  if (gameState === null) {
    return (
      <p>[HORS-JEU] Il y à un problème avec le logiciel, informez un·e PNJ (idéalement Thibault).</p>
    )
  }

  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <p>message: {gameState.current_step_id}</p>
      <div className="card">
        <button onClick={() => {
          sendJsonMessage({ channel: RedisChannel.DASHBOARDS, data: 'hello' });
        }}>
          count is gone.
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
