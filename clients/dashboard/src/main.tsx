import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import Captain from './pages/Captain.tsx'
import { ChakraProvider } from '@chakra-ui/react'
import { GameContext } from './lib/gameContext.tsx';


const router = createBrowserRouter([
  {
    path: "/", element: <App />,
    errorElement: <p><b>[HORS-JEU]</b> Il y à un problème avec le logiciel. Informez un·e PNJ (idéalement Thibault).</p>,
    children: [
      { path: "captain", element: <Captain /> },

    ]
  },
])


ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <GameContext.Provider value={null}>
      <ChakraProvider>
        <RouterProvider router={router} />
      </ChakraProvider>
    </GameContext.Provider>
  </React.StrictMode>,
)
