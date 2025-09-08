from enum import Enum
from config import mqttc
from bt_scan import scan_devices
from mqtt.sendEvent import SentEvent
from typing import TypedDict

class ReceivedEvent(Enum):
	SCAN_REQUEST = "scan_request"

class ScanRequest(TypedDict):
	devices: list[str]
	timeout: int

async def on_scan_request(client, userdata, msg):
	scan_request = ScanRequest.from_json(msg.payload)
	await scan_devices(scan_request.devices, scan_request.timeout)

def initListeners():
	mqttc.subscribe(ReceivedEvent.SCAN_REQUEST, on_scan_request)

def deinitListeners():
	mqttc.unsubscribe(ReceivedEvent.SCAN_REQUEST)