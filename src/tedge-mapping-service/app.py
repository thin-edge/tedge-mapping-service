"""Connector application"""
import logging
import queue
import threading
import os
import time
import sys
from pathlib import Path
from client import MappingClient
from management.config import Config

# Set sensible logging defaults
log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

class App:
    """Connection Application"""

    # pylint: disable=too-few-public-methods
    def run(self):
        """Main application loop"""
        # pylint: disable=broad-except
        config = Config()

        client = MappingClient(config)

        while True:
            try:
                client.connect()
                client.bootstrap()
                client.subscribe()
                while True:
                    time.sleep(1)
                # client.loop_forever()
            except ConnectionRefusedError:
                log.info("MQTT broker is not ready yet")
            except KeyboardInterrupt:
                log.info("Exiting...")
                if client:
                    client.shutdown()
                sys.exit(0)
            except Exception as ex:
                log.info("Unexpected error. %s", ex)

            # Wait before trying again
            time.sleep(5)
            