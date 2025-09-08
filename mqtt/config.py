import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Remove the blocking call - we'll handle this in main.py
# mqttc.loop_forever()

def start_mqtt_loop(mqtt_host: str, mqtt_port: int, mqtt_username: str, mqtt_password: str):
    """Start the MQTT client loop in a non-blocking way"""
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.username_pw_set(mqtt_username, mqtt_password)

    mqttc.connect(mqtt_host, mqtt_port, 60)

    mqttc.loop_start()

def stop_mqtt_loop():
    """Stop the MQTT client loop"""
    mqttc.loop_stop()