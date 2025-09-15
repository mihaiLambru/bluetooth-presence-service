import logging
from config import Config
from mqtt.discovery.components import Components
from mqtt.discovery.device_payload import device_payload
from mqtt.discovery.discovery_payload import DiscoveryPayload
from mqtt.send_event import send_event
import paho.mqtt.client as mqtt

logger = logging.getLogger("components.scan_timeout_number")

timeout_core_topic = f"homeassistant/{Components.Number.value}/timeout"

def get_timeout_config_topic():
	return f"{timeout_core_topic}/config"

def get_timeout_state_topic():
	return f"{timeout_core_topic}/state"

def get_timeout_command_topic():
	return f"{timeout_core_topic}/command"

class TimeoutNumberDiscoveryPayload(DiscoveryPayload):
	min: int
	max: int
	command_topic: str
	state_topic: str


def publish_discovery_message_for_timeout():
	discovery_topic = get_timeout_config_topic()
	discovery_payload = TimeoutNumberDiscoveryPayload(
		name="Timeout",
		unique_id="timeout",
		device=device_payload,
		unit_of_measurement="s",
		command_topic=get_timeout_command_topic(),
		state_topic=get_timeout_state_topic(),
		min=0,
		max=3600
	)
	send_event(discovery_topic, discovery_payload)

def on_timeout_change(client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage) -> None:
	try:
		payload_str = msg.payload.decode('utf-8')
		new_timeout = int(payload_str)
		logger.info(f"Received timeout change: {new_timeout}")
		Config.set_scan_timeout(new_timeout)
	except Exception as e:
		logger.error(f"Error processing timeout change: {e}")