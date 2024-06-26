#!/usr/bin/env python3
"""mapping client"""
import logging
import json
import time
import threading
from typing import Any, List
from paho.mqtt.client import Client, MQTTMessage, MQTTv311
from management.config import Config
from management.topics import health_topic
from management.worker import Worker, Job
from management.messages import JSONMessage
from mapper import Mapper

log = logging.getLogger(__file__)


class MappingClient:
    """Mapping Client

    The mapping client is used to map custom formats to thin-edge.io JSON via MQTT
    """

    __service_name__ = "mapping-service"

    def __init__(self, config: Config) -> None:
        self.mqtt = None
        self.config = config
        self._workers: List[Worker] = []
        self.config.device_id = self.get_id()
        self.on_custom_message = Mapper(config).on_custom_message
        self._subscriptions = []
        self._connected_once = threading.Event()

    def shutdown(self, worker_timeout: float = 10):
        """Shutdown client including any workers in progress

        Args:
            worker_timeout(float): Timeout in seconds to wait for
                each worker (individually). Defaults to 10.
        """
        if self.mqtt and self.mqtt.is_connected():
            self.mqtt.disconnect()
            self.mqtt.loop_stop(True)

        # Stop all workers
        for worker in self._workers:
            worker.join(worker_timeout if worker_timeout and worker_timeout > 0 else 10)

        # Clear workers
        self._workers = []
        self.mqtt = None

    def get_id(self):
        """Get the id to be used for the mapping service"""
        return "main"

    def connect(self):
        """Connect to the thin-edge.io MQTT broker"""
        if self.mqtt is not None:
            log.info(
                "MQTT client already exists. connected=%s", self.mqtt.is_connected()
            )
            return

        if self.mqtt is None:
            # Don't use a clean session so no messages will go missing
            client = Client(
                client_id=self.config.device_id, clean_session=False, protocol=MQTTv311
            )
            client.reconnect_delay_set(10, 120)
            if self.config.device_id:
                client.will_set(
                    health_topic(
                        topic_id=f"device/{self.config.device_id}/service/{self.__service_name__}"
                    ),
                    json.dumps({"status": "down"}),
                )

            def _create_on_connect_callback(done):
                _done = done

                def on_connect(_client, _userdata, _flags, result_code):
                    nonlocal _done
                    if result_code == 0:
                        log.info("Connected to MQTT Broker!")
                        _done.set()
                    else:
                        log.info("Failed to connect. code=%d", result_code)

                return on_connect

            def on_disconnect(_client: Client, _userdata: Any, result_code: int):
                log.info("Client was disconnected. result_code=%d", result_code)

            self._connected_once.clear()
            client.on_connect = _create_on_connect_callback(self._connected_once)
            client.on_disconnect = on_disconnect
            # Enable paho mqtt logs to help with any mqtt connection debugging
            client.enable_logger(log)
            log.info(
                "Trying to connect to the MQTT broker: host=%s:%s, client_id=%s",
                self.config.tedge.host,
                self.config.tedge.port,
                self.config.device_id,
            )

            client.connect(self.config.tedge.host, self.config.tedge.port)
            client.loop_start()

            # Only assign client after .connect call
            # (as it can throw an error if the address is not reachable)
            self.mqtt = client

        if not self._connected_once.wait(30):
            log.warning(
                "Failed to connect successfully after 30 seconds. Continuing anyway"
            )
            # TODO: Should an exception be thrown, or just let paho do the reconnect eventually
            self.shutdown()
            raise RuntimeError("Failed to connect successfully to MQTT broker")

    def bootstrap(self):
        """Register extra services once the mqtt client is up"""

        # wait for registration to be processed
        time.sleep(5)

    def subscribe(self):
        """Subscribe to thin-edge.io child device topics and register
        handlers to respond to different operations.
        """
        # get config handler
        handlers = [
            (
                self.config.configuration.custom_topic,
                self.on_custom_message,
            ),
        ]
        for topic, handler in handlers:
            log.info("Registering worker. topic=%s", topic)
            self.register_worker(topic, target = handler)

        # Only register that the child device is ready now
        # Register health check and bootstrap other plugin settings
        log.info(
            "Publishing health endpoint. device=%s, service=%s",
            self.config.device_id,
            self.__service_name__,
        )
        self.mqtt.publish(
            health_topic(
                topic_id=f"device/{self.config.device_id}/service/{self.__service_name__}"
            ),
            json.dumps({"status": "up"}),
        )

    def register_worker(self, topic: str, target: Job, num_threads: int = 1):
        """Register a worker to handle requests for a specific MQTT topic

        Args:
            topic (str): MQTT topic
            target (Any): Job function to execute for the worker
            num_threads (int, optional): Number of threads. Defaults to 1.
        """
        worker = Worker(target, num_threads=num_threads)
        worker.start()

        def add_job(client, _userdata, message: MQTTMessage):
            # if len(message.payload) == 0:
            #     # Message is being cleared
            # 	return
            try:
                payload = json.loads(message.payload.decode())
                log.info("Adding job")
                worker.put(self.config, client, JSONMessage(message.topic, payload))
            except Exception as e:
                log.error(
                    "Can't parse message, ignoring: payload=%s",
                    message.payload,
                )

        self.mqtt.message_callback_add(topic, add_job)
        self.mqtt.subscribe(topic, qos=2)
        self._workers.append(worker)

    def loop_forever(self):
        """Block infinitely"""
        self.mqtt.loop_forever()
