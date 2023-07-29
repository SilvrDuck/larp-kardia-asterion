import { VStack } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';


function App() {

  return (
    <VStack h={"100vh"} w={"100vw"} align="stretch">
      <h1>Serenity</h1>
      <Outlet />
    </VStack>
  )
}

export default App
