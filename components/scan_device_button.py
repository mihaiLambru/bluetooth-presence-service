import asyncio
from config import Config
from mqtt.discovery.components import Components
from mqtt.discovery.device_payload import device_payload
from mqtt.discovery.discovery_payload import DiscoveryPayload
from mqtt.sendEvent import sendEvent
import paho.mqtt.client as mqtt

from scan import scan_device

def get_scan_button_core_topic(device_address: str):
	safeDeviceAddress = device_address.replace(":", "_")
	return f"homeassistant/{Components.Button.value}/scan_device_button_{safeDeviceAddress}"

def get_scan_button_config_topic(device_address: str):
	scan_button_core_topic = get_scan_button_core_topic(device_address)
	return f"{scan_button_core_topic}/config"

def get_scan_button_command_topic(device_address: str):
	scan_button_core_topic = get_scan_button_core_topic(device_address)
	return f"{scan_button_core_topic}/command"

class ScanButtonDiscoveryPayload(DiscoveryPayload):
	command_topic: str

def publish_discovery_message_for_scan_button(device_address: str):
	discovery_topic = get_scan_button_config_topic(device_address)
	discovery_payload = ScanButtonDiscoveryPayload(
		name=f"Scan {device_address}",
		unique_id=f"scan_button_{device_address}",
		device=device_payload,
		command_topic=get_scan_button_command_topic(device_address),
	)
	sendEvent(discovery_topic, discovery_payload)

def on_scan_button_press(client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage) -> None:
	try:
		device_address = msg.topic.split("/")[-1]
		print(f"Received scan button press for device {device_address}")
		timeout = Config.get_scan_timeout()
		asyncio.run(scan_device(device_address, timeout))
	except Exception as e:
		print(f"Error processing scan button press: {e}")