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
import { WebsocketProvider } from './lib/websocketProvider.tsx';
import { TravelProvider } from './lib/travelProvider.tsx'
import { theme } from './theme.tsx'
import { SonarProvider } from './lib/sonarProvider.tsx';
import { Control } from './pages/Control.tsx';
import { SonarConfigProvider } from './lib/sonarConfigProvider.tsx';



const router = createBrowserRouter([
  {
    path: "/", element: <App />,
    errorElement: <p><b>[HORS-JEU]</b> Il y à un problème avec le logiciel. Informez un·e PNJ (idéalement Thibault).</p>,
    children: [
      { path: "captain/:owner", element: <Captain /> },
      { path: "control/:owner", element: <Control /> },
    ]
  },
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <WebsocketProvider>
      <TravelProvider>
        <SonarProvider>
          <SonarConfigProvider>
            <ChakraProvider theme={theme} >
              <RouterProvider router={router} />
            </ChakraProvider>
          </SonarConfigProvider>
        </SonarProvider>
      </TravelProvider>
    </WebsocketProvider>
  </React.StrictMode>,
)
