import { createContext } from "react";

type ReactFlowGraph = {
    nodes: object[];
    edges: object[];
}

export type GameState = {
    current_step_id: string | [string, string];
    is_in_battle: boolean;
    step_completion: number;
    react_flow_graph: ReactFlowGraph;
}

export const GameContext = createContext<GameState | null>(null)
