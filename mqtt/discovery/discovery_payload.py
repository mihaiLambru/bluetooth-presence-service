from typing import NotRequired, TypedDict
from mqtt.discovery.device_payload import DevicePayload

class AvailabilityPayload(TypedDict):
	topic: str

class DiscoveryPayload(TypedDict):
	device: DevicePayload
	name: str
	unique_id: str
	unit_of_measurement: NotRequired[str]
	availability: NotRequired[AvailabilityPayload]
	payload_available: NotRequired[str]
	payload_not_available: NotRequired[str]
	value_template: NotRequired[str]