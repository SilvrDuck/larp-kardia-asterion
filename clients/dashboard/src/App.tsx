import { HStack, Spacer, VStack } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import { PlanetCounter } from './components/planetCounter';

import { useContext } from 'react';
import { SonarContext } from './lib/sonarProvider';
import { BattleInfo } from './components/battleInfo';
import { TravelInfo } from './components/travelInfo';
import { ShipStatus } from './components/shipStatus';




function App() {

  const { in_battle } = useContext(SonarContext)

  const ui = in_battle ? <BattleInfo /> : <TravelInfo />

    return (
    <VStack h={"100vh"} w={"100vw"} align="stretch">
      <VStack align="stretch" pt="1.5em" pl="1.5em" pr="1.5em" >
        <HStack>
          <h1>Serenity</h1>
          <Spacer />
          {ui}
        </HStack>
        <PlanetCounter />
      </VStack>
      <Outlet />
    </VStack >
    )
}

    export default App
