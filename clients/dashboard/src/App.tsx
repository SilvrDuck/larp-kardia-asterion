import { VStack } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import { PlanetCounter } from './components/planetCounter';
import { PlanetGraph } from './components/planetGraph';




function App() {

  return (
    <VStack h={"100vh"} w={"100vw"} align="stretch">
      <VStack align="stretch" pt="1.5em" pl="1.5em" pr="1.5em" >
        <h1>Serenity</h1>
        <PlanetCounter />
      </VStack>
      <Outlet />
    </VStack>
  )
}

export default App
