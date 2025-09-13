

from components.device_tracker import publish_discovery_message_for_device_tracker
from components.scan_device_button import publish_discovery_message_for_scan_button
from components.scan_timeout_number import publish_discovery_message_for_timeout

def runDiscovery(devices: list[str]):
	publish_discovery_message_for_timeout()

	for device in devices:
		publish_discovery_message_for_device_tracker(device)
		publish_discovery_message_for_scan_button(device)