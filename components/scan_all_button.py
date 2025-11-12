import logging
from mqtt.discovery.components import Components
from mqtt.discovery.device_payload import device_payload
from mqtt.discovery.discovery_payload import DiscoveryPayload
from mqtt.send_event import send_event
import paho.mqtt.client as mqtt
from utils.scan import BluetoothScanner

logger = logging.getLogger("components.scan_all_button")

scan_all_button_core_topic = f"homeassistant/{Components.Button.value}/scan_all_button"

scan_all_button_config_topic = f"{scan_all_button_core_topic}/config"

scan_all_button_command_topic = f"{scan_all_button_core_topic}/command"

class ScanButtonDiscoveryPayload(DiscoveryPayload):
	command_topic: str

def publish_discovery_message_for_scan_all_button():
	discovery_topic = scan_all_button_config_topic
	discovery_payload = ScanButtonDiscoveryPayload(
		name="Scan All",
		unique_id="scan_all_button",
		device=device_payload,
		command_topic=scan_all_button_command_topic,
	)
	send_event(discovery_topic, discovery_payload)

def on_scan_all_button_press(client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage) -> None:
	try:
		BluetoothScanner.start_scanning()
		logger.info("Received scan all button press")
	except Exception as e:
		logger.error(f"Error processing scan button press: {e}")