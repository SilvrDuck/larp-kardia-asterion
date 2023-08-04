from __future__ import annotations
from ast import Not
import asyncio
import logging
from re import T
from typing import Optional
from serenity.common.definitions import MessageType, ServiceType, Topic
from serenity.common.redis_client import RedisMessage

from serenity.common.service import Service
from serenity.sound.definitions import  SoundConfig,  SoundState
from aiomqtt import Client as MQTT, Message
from serenity.sonar.definitions import Damage, SonarState
from serenity.switch.definitions import SwitchTopic
from playsound import playsound
from threading import Thread
from pathlib import Path

class SoundService(Service[SoundState, SoundConfig]):

    state_type = SoundState
    config_type = SoundConfig

    @classmethod
    def default_service(cls) -> SoundService:
        return SoundService(SoundState(
            background_sound=None
        ), SoundConfig())

    def _update_state(self, state: SoundState) -> None:
        self._background_sound = state.background_sound
        self.start_background(self._background_sound)

    def to_state(self) -> SoundState:
        return SoundState(background_sound=self._background_sound)

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
                        case RedisMessage(type=MessageType.DAMAGE):
                            self.play_damage()

            except Exception as err:
                logging.error("SOUND: Error while processing command: %s\n%s", message, err)



    async def start_background(self, sound: str) -> None:
        await self.redis.publish(
            RedisMessage(topic=Topic.SOUND, type=MessageType.BACKGROUND_SOUND, data=sound)
        )

    def play_damage(self) -> None:
        self.play_sound("explosion_1")
    
    def play_sound(self, sound: str) -> None:
        this_dir = Path(__file__).parent
        path = this_dir / f"assets/{sound}.mp3"
        Thread(target=playsound, args=(str(path),)).start()


    async def _start_battle(self) -> None:
        raise NotImplementedError()