import {
    Box,
    Step,
    StepDescription,
    StepIcon,
    StepIndicator,
    StepNumber,
    StepSeparator,
    StepStatus,
    StepTitle,
    Stepper,
    useSteps,
} from '@chakra-ui/react'
import { TravelContext } from '../lib/travelProvider'
import { useContext, useEffect, useState } from 'react'

export function PlanetCounter() {

    const { flow_graph, num_steps } = useContext(TravelContext)
    const [numSteps, setNumSteps] = useState(8)
    const { activeStep, setActiveStep } = useSteps({ index: 0, count: numSteps })

    useEffect(() => {
        const index = flow_graph.nodes.filter((node) => node.data.visited).length
        setActiveStep(index)
    }, [flow_graph])

    useEffect(() => {
        setNumSteps(num_steps)
    }, [num_steps])

    return (

        <Stepper index={activeStep}>
            {[...Array(numSteps).keys()].map((index) => (
                <Step key={index}>
                    <StepIndicator>
                        <StepStatus
                            complete={<StepIcon />}
                            incomplete={<StepNumber />}
                            active={<StepNumber />}
                        />
                    </StepIndicator>
                    <StepSeparator />
                </Step>
            ))}
        </Stepper>


    )
}

