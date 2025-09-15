import enum, json
import logging
from typing import TypedDict
from bleak.backends.device import BLEDevice
from mqtt.config import mqttc

logger = logging.getLogger("mqtt.sendEvent")

class SentEvent(enum.StrEnum): 
	DEVICE_UPDATE = "device_update"

def sendEvent(eventType: str, data: object | str) -> None:
	logger.info(f"Sending event: {eventType} {data}")
	if isinstance(data, dict):
		logger.debug("It's a dict object")
		mqttc.publish(eventType, json.dumps(data))
	if isinstance(data, str):
		mqttc.publish(eventType, data)
	else:
		logger.warning('Unknown data while sending event')

class DeviceStatusUpdateData(TypedDict):
	address: str
	device: BLEDevice | None
	found: bool

