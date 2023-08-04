from __future__ import annotations
from ast import Not
import asyncio
import logging
from typing import Optional
from serenity.common.definitions import MessageType, ServiceType, Topic
from serenity.common.redis_client import RedisMessage

from serenity.common.service import Service
from serenity.sound.definitions import  SoundConfig,  SoundState
from aiomqtt import Client as MQTT, Message
from serenity.sonar.definitions import Damage, SonarState
from serenity.switch.definitions import SwitchTopic

class SoundService(Service[SoundState, SoundConfig]):

    state_type = SoundState
    config_type = SoundConfig

    @classmethod
    def default_service(cls) -> SoundService:
        return SoundService(SoundState(), SoundConfig())

    def _update_state(self, state: SoundState) -> None:
        pass

    def to_state(self) -> SoundState:
        return SoundState()

    def _update_config(self, config: SoundConfig) -> None:
        pass

    def to_config(self) -> SoundConfig:
        return SoundConfig()

    async def _start(self) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._status_subscription())
            tg.create_task(self._command_subscription())

    async def _command_subscription(self) -> None:
        subscription = self.redis.subscription_iterator(Topic.COMMAND)
        async for message in subscription:
            try:
                async with self.get_self_lock():
                    match message:
                        case RedisMessage(type=MessageType.START_BATTLE):
                            await self._start_battle()

            except Exception as err:
                logging.error("SOUND: Error while processing command: %s\n%s", message, err)

    async def _status_subscription(self) -> None:
        subscription = self.redis.subscription_iterator(Topic.BROADCAST_STATUS)
        async for message in subscription:
            try:
                async with self.get_self_lock():
                    match message:
                        case RedisMessage(type=MessageType.DAMAGE, data=data):
                            await self._deal_with_damage(Damage(**data))

            except Exception as err:
                logging.error("SOUND: Error while processing command: %s\n%s", message, err)


    async def _deal_with_damage(self, damage: Damage) -> None:
        raise NotImplementedError()


    async def _start_battle(self) -> None:
        raise NotImplementedError()