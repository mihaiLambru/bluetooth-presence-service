from typing import TypedDict

class DevicePayload(TypedDict):
	identifiers: list[str]
	name: str
	manufacturer: str
	model: str
	sw_version: str

device_payload: DevicePayload = {
  "identifiers": ["bt-scan-service"],
  "name": "Bluetooth Presence Service",
  "manufacturer": "Lambru",
  "model": "bt-presence",
  "sw_version": "0.1.0"
}
