from __future__ import annotations
import stat
from typing import Dict
import orjson
import asyncio


from serenity.common.definitions import MessageType, ServiceType, Topic
from serenity.common.redis_client import RedisClient, RedisMessage
from serenity.common.service import Service
from serenity.switch.definitions import Switch, SwitchConfig, SwitchState, SwitchTopic
import logging
from serenity.common.config import settings
from aiomqtt import Client as MQTT, Message


class SwitchService(Service[SwitchState, SwitchConfig]):
    state_type = SwitchState
    config_type = SwitchConfig

    _switches: Dict[Switch, bool]

    def __init__(self, state: SwitchState, config: SwitchConfig) -> None:
        super().__init__(state, config)

        self._other_redis = RedisClient()

        # self._mqtt = MQTTClient()
        # self._mqtt.connect("localhost", 1883, 60)
        # self._mqtt.on_message = self._on_mqtt_message
        # self._mqtt.subscribe(SwitchTopic.SWITCH)
        # self._mqtt.loop_start()
        # self._publish_mqtt_state()

        # self._sync_redis = StrictRedis(host=settings.redis_host, port=settings.redis_port)

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

    def _to_state(self) -> SwitchState:
        return SwitchState(switches=self._switches)

    def _update_config(self, config: SwitchConfig) -> None:
        pass

    def _to_config(self) -> SwitchConfig:
        pass

    async def _start(self) -> None:
        async with MQTT("localhost") as client:
            async with client.messages() as messages:
                await client.subscribe(SwitchTopic.SWITCH.value)
                logging.info("Starting mqqtt for switches") 
                async for message in messages:
                    try:
                        await self._on_mqtt_message(message, client)
                    except Exception as err:
                        logging.error("Error in mqtt message: %s", err)

    async def _on_mqtt_message(self, message: Message, client: MQTT):
        message = message.payload.decode("utf-8")

        async with MQTT("localhost"):
            if message == "__init__":
                logging.info("recieved init from switch")
                await self._publish_mqtt_state(client)
                return

        try:
            switch = Switch.from_message(message)
        except ValueError:
            logging.error("Invalid switch UID: %s", message)
            return

        await self._deal_with_switch(switch)

    async def _publish_mqtt_state(self, client: MQTT):
        for switch, state in self._switches.items():
            await client.publish(SwitchTopic.LED.value, switch.to_message(state))

    async def _deal_with_switch(self, switch: Switch):
        await self.redis.publish(self._move_message(switch))

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
