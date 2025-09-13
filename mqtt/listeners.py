from components.scan_device_button import get_scan_button_command_topic, on_scan_button_press
from components.scan_timeout_number import get_timeout_command_topic, on_timeout_change
from config import Config
from mqtt.config import mqttc

def initListeners() -> None:
	timeout_topic = get_timeout_command_topic()
	mqttc.subscribe(timeout_topic)
	mqttc.message_callback_add(timeout_topic, on_timeout_change)

	for device_address in Config.get_instance()["devices_list"]:
		scan_button_topic = get_scan_button_command_topic(device_address)
		mqttc.subscribe(scan_button_topic)
		mqttc.message_callback_add(scan_button_topic, on_scan_button_press)