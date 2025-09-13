import asyncio, json
from mqtt.discovery import runDiscovery
from mqtt.listeners import deinitListeners, initListeners
from mqtt.config import start_mqtt_loop, stop_mqtt_loop
from typing import TypedDict
from scan import scan_devices

class Config(TypedDict):
	"""
	devices_list: list of device addresses. Can't be empty
	automatic_scan: automatic scan in seconds. 0 to disable automatic scan
	scan_timeout: scan timeout in seconds. Must be greater than 0
	mqtt_host: MQTT host
	mqtt_port: MQTT port
	mqtt_username: MQTT username
	mqtt_password: MQTT password
	"""
	devices_list: list[str]
	automatic_scan: int
	scan_timeout: int
	mqtt_host: str
	mqtt_port: int
	mqtt_username: str
	mqtt_password: str

def read_config():
	try:
			with open("config.json", "r", encoding="utf-8") as f:
					config = json.load(f)
					print("Successfully read config", config)

					return config
	except FileNotFoundError:
			print("File not found")
	except json.JSONDecodeError as e:
			print(f"Invalid JSON: {e}")

async def main(): 
	# read devices_list from config.json
	raw_config = read_config()
	if raw_config is None:
		print("Failed to read config. Exiting.")
		return
	config: Config = raw_config  # type: ignore

	# Start MQTT client in background
	start_mqtt_loop(config["mqtt_host"], config["mqtt_port"], config["mqtt_username"], config["mqtt_password"])
	runDiscovery(config["devices_list"])
	
	# Initialize MQTT listeners
	initListeners()

	try:
		# Check if automatic_scan exists and is greater than 0
		automatic_scan = config.get("automatic_scan", 0)
		if automatic_scan > 0:
			print(f"Starting automatic scan every {automatic_scan} seconds")
			while True:
				await scan_devices(config["devices_list"], config["scan_timeout"])
				await asyncio.sleep(automatic_scan)
		else:
			# Keep the app running even without automatic scanning
			print("App is running and listening for MQTT events. Press Ctrl+C to exit.")
			while True:
				await asyncio.sleep(2)  # Keep the event loop alive
	except KeyboardInterrupt:
		print("Shutting down...")
	finally:
		deinitListeners()
		stop_mqtt_loop()

if __name__ == "__main__":
	asyncio.run(main())



