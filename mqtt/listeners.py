from components.scan_all_button import on_scan_all_button_press, scan_all_button_command_topic
from components.scan_device_button import get_scan_button_command_topic, on_scan_button_press
from components.scan_timeout_number import get_timeout_command_topic, on_timeout_change
from config import Config
from mqtt.config import mqttc

def init_listeners() -> None:
	timeout_topic = get_timeout_command_topic()
	mqttc.subscribe(timeout_topic)
	mqttc.message_callback_add(timeout_topic, on_timeout_change)

	scan_all_button_topic = scan_all_button_command_topic
	mqttc.subscribe(scan_all_button_topic)
	mqttc.message_callback_add(scan_all_button_topic, on_scan_all_button_press)

	for device_address in Config.get_instance().devices.get_addresses():
		scan_button_topic = get_scan_button_command_topic(device_address)
		mqttc.subscribe(scan_button_topic)
		mqttc.message_callback_add(scan_button_topic, on_scan_button_press)