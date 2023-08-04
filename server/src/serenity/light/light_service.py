from __future__ import annotations
import asyncio
import logging
from typing import Optional
from serenity.common.definitions import MessageType, ServiceType, Topic
from serenity.common.redis_client import RedisMessage

from serenity.common.service import Service
from serenity.light.definitions import Color, LightConfig, Light, LightState, Mode
from aiomqtt import Client as MQTT, Message
from serenity.sonar.definitions import Damage, SonarState
from serenity.switch.definitions import SwitchTopic

class LightService(Service[LightState, LightConfig]):

    state_type = LightState
    config_type = LightConfig

    @classmethod
    def default_service(cls) -> LightService:
        return LightService(LightState(light=Light(color=Color.BLUE, mode=Mode.SET, secondary=None)), LightConfig())

    def _update_state(self, state: LightState) -> None:
        self._light = state.light

    def to_state(self) -> LightState:
        return LightState(light=self._light)

    def _update_config(self, config: LightConfig) -> None:
        pass

    def to_config(self) -> LightConfig:
        pass

    async def _start(self) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._status_subscription())

    async def _status_subscription(self) -> None:
        subscription = self.redis.subscription_iterator(Topic.BROADCAST_STATUS)
        async for message in subscription:
            try:
                async with self.get_self_lock():
                    match message:
                        case RedisMessage(type=MessageType.STATE, concerns=ServiceType.SONAR, data=data):
                            await self._deal_with_sonar(SonarState(**data))
                        case RedisMessage(type=MessageType.DAMAGE, data=data):
                            await self._deal_with_damage(Damage(**data))

            except Exception as err:
                logging.error("LIGHT: Error while processing command: %s\n%s", message, err)

    async def _deal_with_sonar(self, state: SonarState) -> None:
        current_color = self._light.color

        if state.in_battle:
            if current_color != Color.RED:
                await self._blink_and_set(Color.RED, Color.RED)
            else:
                await self._set_color(Color.RED)  # in case it was unset and we don't know

        else:  # not in_battle
            if current_color == Color.RED:
                await self._blink_and_set(Color.GREEN, Color.BLUE)
            else:
                await self._set_color(Color.BLUE)

    async def _deal_with_damage(self, damage: Damage) -> None:
        current_color = self._light.color
        if damage.owner == "players":
            await self._blink_and_set(Color.YELLOW, current_color)

    async def _blink_and_set(self, blink_color: Color, set_color: Color) -> None:
        await self._set_lights(Mode.BLINK, blink_color, set_color)

    async def _set_color(self, color: Color) -> None:
        await self._set_lights(Mode.SET, color, None)

    async def _set_lights(self, mode: Mode, color: Color, secondary: Optional[Color]) -> None:
        light = Light(color=color, mode=mode, secondary=secondary)
        await self.update_state(LightState(light=light))

        async with MQTT("localhost") as client:
            await client.publish(SwitchTopic.SWITCH.value, light.to_mqtt_message())