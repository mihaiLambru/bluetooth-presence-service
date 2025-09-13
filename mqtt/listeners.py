import json
from enum import Enum
from typing import TypedDict, Any
import paho.mqtt.client as mqtt
from mqtt.config import mqttc

class ReceivedEvent(Enum):
	SCAN_REQUEST = "scan_request"

class ScanRequest(TypedDict):
	devices: list[str]
	timeout: int

def on_scan_request(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
	try:
		payload_str = msg.payload.decode('utf-8')
		payload_data = json.loads(payload_str)
		scan_request: ScanRequest = {
			'devices': payload_data['devices'],
			'timeout': payload_data['timeout']
		}
		print(f"Received scan request: {scan_request}")
	except Exception as e:
		print(f"Error processing scan request: {e}")

def initListeners() -> None:
	mqttc.subscribe(ReceivedEvent.SCAN_REQUEST.value)
	mqttc.message_callback_add(ReceivedEvent.SCAN_REQUEST.value, on_scan_request)

def deinitListeners() -> None:
	mqttc.message_callback_remove(ReceivedEvent.SCAN_REQUEST.value)
	mqttc.unsubscribe(ReceivedEvent.SCAN_REQUEST.value)