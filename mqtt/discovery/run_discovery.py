

from components.device_tracker import publish_discovery_message_for_device_tracker
from components.scan_all_button import publish_discovery_message_for_scan_all_button
from components.scan_device_button import publish_discovery_message_for_scan_button
from components.scan_timeout_number import publish_discovery_message_for_timeout
import threading
from config import DevicesList

def run_discovery(devices: DevicesList):
	publish_discovery_message_for_timeout()
	publish_discovery_message_for_scan_all_button()

	for device in devices:
		publish_discovery_message_for_device_tracker(device)
		publish_discovery_message_for_scan_button(device)

def run_discovery_every_hour(devices: DevicesList):
    # Your function here
    run_discovery(devices)
    
    # Schedule next execution
    timer = threading.Timer(3600, run_discovery)
    timer.daemon = True  # Dies when main thread dies
    timer.start()
