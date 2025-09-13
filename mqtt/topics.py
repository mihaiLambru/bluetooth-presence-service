from mqtt.discovery import Components

def get_device_tracker_core_topic(device_address: str):
	safeDeviceAddress = device_address.replace(":", "_")
	return f"homeassistant/{Components.DeviceTracker.value}/{safeDeviceAddress}"

def get_device_tracker_config_topic(device_address: str):
	coreTopic = get_device_tracker_core_topic(device_address)
	return f"{coreTopic}/config"


def get_device_tracker_state_update_topic(device_address: str):
	coreTopic = get_device_tracker_core_topic(device_address)
	return f"{coreTopic}/state"