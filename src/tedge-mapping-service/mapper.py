#!/usr/bin/env python3
"""mapping client"""
import logging

from typing import Any, List
from paho.mqtt.client import Client
from management.config import Config
from management.topics import health_topic
from management.worker import Worker, Job
from management.messages import JSONMessage

log = logging.getLogger(__file__)


class Mapper:
    """Mapper

    The mapper client is used to map custom formats to thin-edge.io JSON via MQTT
    """

    def __init__(self, config: Config) -> None:
        self.config = config

        """Shutdown client including any workers in progress

        Args:
            worker_timeout(float): Timeout in seconds to wait for
                each worker (individually). Defaults to 10.
        """

    def on_custom_message(self, config: Config, client: Client, msg: JSONMessage):
        log.info(f"On topic: {msg.topic} new signal: {msg.payload}")
