import logging
from config import Device
from mqtt.discovery.components import Components
from mqtt.discovery.device_payload import device_payload
from mqtt.discovery.discovery_payload import DiscoveryPayload
from mqtt.send_event import send_event
import paho.mqtt.client as mqtt

from utils.scan import BluetoothScanner

logger = logging.getLogger("components.scan_device_button")

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

def publish_discovery_message_for_scan_button(device: Device):
	discovery_topic = get_scan_button_config_topic(device.address)
	safe_device_address = device.address.replace(":", "_")

	device_name = device.name if device.name is not None else safe_device_address
	
	discovery_payload = ScanButtonDiscoveryPayload(
		name=f"Scan {device_name}",
		unique_id=f"scan_button_{safe_device_address}",
		device=device_payload,
		command_topic=get_scan_button_command_topic(device.address),
	)
	send_event(discovery_topic, discovery_payload)


def get_device_address_from_topic(topic: str) -> str:
	"""
	Get the device address from the topic
	scan_device_button_XX_XX_XX_XX_XX_XX/config
	"""
	component_id = topic.split("/")[-2]
	parts = component_id.split("_")[-6:]

	# Join them with ":"
	mac = ":".join(parts)

	return mac
	
def on_scan_button_press(client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage) -> None:
	try:
		device_address = get_device_address_from_topic(msg.topic)
		logger.info(f"Received scan button press for device {device_address}")
		BluetoothScanner.start_scanning()
	except Exception as e:
		logger.error(f"Error processing scan button press: {e}")