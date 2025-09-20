import logging
import paho.mqtt.client as mqtt

logger = logging.getLogger("mqtt.on_disconnect")

def on_disconnect(client: mqtt.Client, userdata: None, rc: int) -> None:
	logger.info(f"Disconnected from MQTT broker with result code {rc}")