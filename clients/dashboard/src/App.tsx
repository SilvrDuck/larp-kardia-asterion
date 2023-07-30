import { VStack } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import bg from "@assets/backgrounds/bg_battle.png";

function App() {

  return (
    <VStack h={"100vh"} w={"100vw"} align="stretch">
      <VStack align="stretch" pt="1.5em" pl="1.5em" pr="1.5em" >
        <h1>Serenity</h1>
      </VStack>
      <Outlet />
    </VStack>
  )
}

export default App
