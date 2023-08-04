from __future__ import annotations
from asyncio import taskgroups
import stat
from typing import Dict
import orjson
import asyncio


from serenity.common.definitions import MessageType, Owner, ServiceType, Topic
from serenity.common.redis_client import RedisClient, RedisMessage
from serenity.common.service import Service
from serenity.sonar.definitions import Damage
from serenity.switch.definitions import Group, Switch, SwitchConfig, SwitchState, SwitchTopic
import logging
from serenity.common.config import settings
from aiomqtt import Client as MQTT, Message


class SwitchService(Service[SwitchState, SwitchConfig]):
    state_type = SwitchState
    config_type = SwitchConfig

    _switches: Dict[Switch, bool]

    def __init__(self, state: SwitchState, config: SwitchConfig) -> None:
        super().__init__(state, config)

    @classmethod
    def default_service(cls) -> SwitchService:
        default_state = SwitchState(switches=cls._default_switches())
        default_config = SwitchConfig()
        return cls(default_state, default_config)

    @staticmethod
    def _default_switches() -> Dict[Switch, bool]:
        with open(settings.switches_path, "r", encoding="utf-8") as file:
            uids = orjson.loads(file.read())["uids"]
        return {Switch.from_message(uid): False for uid in uids}

    def _update_state(self, state: SwitchState) -> None:
        self._switches = state.switches

    def to_state(self) -> SwitchState:
        return SwitchState(switches=self._switches)

    def _update_config(self, config: SwitchConfig) -> None:
        pass

    def to_config(self) -> SwitchConfig:
        return SwitchConfig()

    async def _start(self) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._command_subscription())
            tg.create_task(self._start_mqtt())

    async def _command_subscription(self) -> None:
        subscription = self.redis.subscription_iterator(Topic.COMMAND)
        async for message in subscription:
            try:
                async with self.get_self_lock():
                    match message:
                        case RedisMessage(type=MessageType.SURFACE):
                            await self._reset_switches()
                        case RedisMessage(type=MessageType.START_BATTLE):
                            await self._reset_switches()

            except Exception as err:
                logging.error("SWITCH: Error while processing command: %s\n%s", message, err)

    async def _start_mqtt(self) -> None:
        async with MQTT("localhost") as client:
            async with client.messages() as messages:
                await client.subscribe(SwitchTopic.SWITCH.value)
                logging.info("Starting mqqtt for switches")
                async for message in messages:
                    try:
                        await self._on_mqtt_message(message)
                    except Exception as err:
                        logging.error("Error in mqtt message: %s", err)

    async def _on_mqtt_message(self, message: Message):
        message = message.payload.decode("utf-8")

        if message != "__init__":
            try:
                switch = Switch.from_message(message)
            except ValueError:
                logging.error("Invalid switch UID: %s", message)
                return

            assert switch in self._switches, f"missing switch in config {switch}"
            await self._deal_with_switch(switch)

        await self._publish_mqtt_state()

    async def _publish_mqtt_state(self):
        async with MQTT("localhost") as client:
            for switch, state in self._switches.items():
                await client.publish(SwitchTopic.LED.value, switch.to_message(state))

    async def _deal_with_switch(self, switch: Switch):
        if self._switches[switch]:
            self._switches[switch] = False
            await self.redis.publish(self._move_message(switch))

        same_group = [other for other in self._switches if other.group == switch.group]

        if all([not self._switches[sw] for sw in same_group]):
            # if nuclear, damage
            if switch.group == Group.NEUTRAL:
                await self.redis.publish(
                    RedisMessage(
                        topic=Topic.COMMAND, type=MessageType.DIRECT_DAMAGE, data=Damage(owner=Owner.PLAYERS, amount=1)
                    )
                )
                self._reset_switches()

            # if all of group on, turn all off
            for sw in same_group:
                self._switches[sw] = True

    async def _reset_switches(self):
        for switch in self._switches:
            self._switches[switch] = True


        await self._publish_mqtt_state()

    @staticmethod
    def _move_message(switch: Switch) -> RedisMessage:
        return RedisMessage(
            topic=Topic.COMMAND,
            type=MessageType.MOVE,
            concerns=ServiceType.SONAR,
            data={
                "owner": "players",
                "direction": switch.heading.value,
            },
        )
