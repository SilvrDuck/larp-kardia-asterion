
enum RedisChannel {
    DASHBOARDS = 'dashboards',
}

type GameState = {
    current_step_id: string | [string, string];
    is_in_battle: boolean;
    step_completion: number;
}

export type { GameState };
export { RedisChannel };
