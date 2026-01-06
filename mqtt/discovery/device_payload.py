from typing import NotRequired, TypedDict

class DevicePayload(TypedDict):
	identifiers: list[str]
	name: NotRequired[str]
	manufacturer: NotRequired[str]
	model: NotRequired[str]
	sw_version: NotRequired[str]
	connections: NotRequired[list[tuple[str, str]]]


device_payload: DevicePayload = {
  "identifiers": ["bt-scan-service"],
  "name": "Bluetooth Presence Service",
  "manufacturer": "Lambru",
  "model": "bt-presence",
  "sw_version": "0.1.0"
}
