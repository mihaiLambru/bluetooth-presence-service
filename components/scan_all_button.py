import asyncio
from config import Config
from mqtt.discovery.components import Components
from mqtt.discovery.device_payload import device_payload
from mqtt.discovery.discovery_payload import DiscoveryPayload
from mqtt.sendEvent import sendEvent
import paho.mqtt.client as mqtt

from scan import scan_devices

scan_all_button_core_topic = f"homeassistant/{Components.Button.value}/scan_all_button"

scan_all_button_config_topic = f"{scan_all_button_core_topic}/config"

scan_all_button_command_topic = f"{scan_all_button_core_topic}/command"

class ScanButtonDiscoveryPayload(DiscoveryPayload):
	command_topic: str

def publish_discovery_message_for_scan_all_button():
	discovery_topic = scan_all_button_config_topic
	discovery_payload = ScanButtonDiscoveryPayload(
		name=f"Scan All",
		unique_id=f"scan_all_button",
		device=device_payload,
		command_topic=scan_all_button_command_topic,
	)
	sendEvent(discovery_topic, discovery_payload)

def on_scan_all_button_press(client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage) -> None:
	try:
		print(f"Received scan all button press")
		timeout = Config.get_scan_timeout()
		asyncio.run(scan_devices(Config.get_instance().devices_list, timeout))
	except Exception as e:
		print(f"Error processing scan button press: {e}")