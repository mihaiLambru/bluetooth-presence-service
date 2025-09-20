from mqtt.on_connect import on_connect
from mqtt.config import mqttc
from mqtt.on_disconnect import on_disconnect


def start_mqtt_loop(mqtt_host: str, mqtt_port: int, mqtt_username: str, mqtt_password: str):
	"""Start the MQTT client loop in a non-blocking way"""
	mqttc.on_connect = on_connect
	mqttc.on_disconnect = on_disconnect

	mqttc.username_pw_set(mqtt_username, mqtt_password)

	mqttc.connect(mqtt_host, mqtt_port, 60)

	mqttc.loop_start()

def stop_mqtt_loop():
	"""Stop the MQTT client loop"""
	mqttc.loop_stop()
