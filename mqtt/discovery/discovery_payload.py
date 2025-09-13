from typing import NotRequired, TypedDict
from mqtt.discovery.device_payload import DevicePayload

class DiscoveryPayload(TypedDict):
	device: DevicePayload
	name: str
	unique_id: str
	unit_of_measurement: NotRequired[str]