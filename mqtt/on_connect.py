import paho.mqtt.client as mqtt
import logging
from mqtt.discovery.run_discovery import run_discovery
from config import Config
from mqtt.listeners import initListeners

logger = logging.getLogger("mqtt.on_connect")

def on_connect(client: mqtt.Client, userdata: None, flags: dict[str, str], rc: int):
	logger.info(f"Connected with result code {rc}")
		
	if rc == 0:
		run_discovery(Config.get_instance().devices_list)
		initListeners()
		client.subscribe("$SYS/#")
	else:
		logger.error(f"Failed to connect with result code {rc}")
