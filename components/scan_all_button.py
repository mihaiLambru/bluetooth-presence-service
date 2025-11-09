import asyncio
import logging
import threading
from config import Config
from mqtt.discovery.components import Components
from mqtt.discovery.device_payload import device_payload
from mqtt.discovery.discovery_payload import DiscoveryPayload
from mqtt.send_event import send_event
import paho.mqtt.client as mqtt

from utils.scan import scan_devices

logger = logging.getLogger("components.scan_all_button")

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
	send_event(discovery_topic, discovery_payload)

def _run_scan_in_thread(devices_list: list[str], timeout: int):
	"""Run scan in a separate thread to avoid blocking MQTT"""
	try:
		asyncio.run(scan_devices(devices_list, timeout))
	except Exception as e:
		logger.error(f"Error in scan thread: {e}")

def on_scan_all_button_press(client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage) -> None:
	try:
		logger.info(f"Received scan all button press")
		timeout = Config.get_scan_timeout()
		devices_list = Config.get_instance().devices.get_addresses()
		
		# Run scan in a separate thread to avoid blocking MQTT callback
		scan_thread = threading.Thread(
			target=_run_scan_in_thread,
			args=(devices_list, timeout),
			daemon=True
		)
		scan_thread.start()
		logger.debug("Scan thread started")
	except Exception as e:
		logger.error(f"Error processing scan button press: {e}")