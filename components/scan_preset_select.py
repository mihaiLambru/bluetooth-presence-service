import logging
import paho.mqtt.client as mqtt
from typing import List

from config import Config, ScanPreset
from mqtt.discovery.components import Components
from mqtt.discovery.device_payload import device_payload
from mqtt.discovery.discovery_payload import DiscoveryPayload
from mqtt.send_event import send_event

logger = logging.getLogger("components.scan_preset_select")

scan_preset_core_topic = f"homeassistant/{Components.Select.value}/scan_preset"

def get_scan_preset_config_topic() -> str:
	return f"{scan_preset_core_topic}/config"

def get_scan_preset_state_topic() -> str:
	return f"{scan_preset_core_topic}/state"

def get_scan_preset_command_topic() -> str:
	return f"{scan_preset_core_topic}/command"

class ScanPresetSelectDiscoveryPayload(DiscoveryPayload):
	options: List[str]
	command_topic: str
	state_topic: str

SCAN_PRESET_ORDER: list[ScanPreset] = [
	ScanPreset.often,
	ScanPreset.balanced,
	ScanPreset.rarely,
	ScanPreset.never,
	ScanPreset.continuous,
]

def publish_discovery_message_for_scan_preset():
	discovery_topic = get_scan_preset_config_topic()
	discovery_payload = ScanPresetSelectDiscoveryPayload(
		name="Scan preset",
		unique_id="scan_preset",
		device=device_payload,
		command_topic=get_scan_preset_command_topic(),
		state_topic=get_scan_preset_state_topic(),
		options=[preset.value for preset in SCAN_PRESET_ORDER],
	)
	send_event(discovery_topic, discovery_payload)
	publish_scan_preset_state()

def publish_scan_preset_state():
	current_preset = Config.get_scan_preset()
	send_event(get_scan_preset_state_topic(), current_preset.value)

def on_scan_preset_change(client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage) -> None:
	payload_str = msg.payload.decode("utf-8").strip()
	logger.info("Received scan preset change: %s", payload_str)
	try:
		preset = Config.set_scan_preset(payload_str)
		logger.info("Scan preset updated to %s", preset.value)
		publish_scan_preset_state()
	except Exception as exc:
		logger.error("Error processing scan preset change: %s", exc)
		# Re-publish the current state to keep HA in sync
		publish_scan_preset_state()

