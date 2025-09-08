import asyncio, json, time
from bleak import BleakClient, BleakScanner
from mqtt.listeners import deinitListeners, initListeners
from mqtt.sendEvent import SentEvent, sendEvent
from mqtt.config import start_mqtt_loop, stop_mqtt_loop
from typing import TypedDict

async def scan_device(address: str, timeout: int):
	"""Scan for a single device by address"""
	try:
		# timeout 10 minutes
		device = await BleakScanner().find_device_by_address(address, timeout)
		print(f"Found device {device.name} for address {address}")

		await sendEvent(SentEvent.DEVICE_FOUND, {"address": address, "device": device, "found": device is not None})

		return {"address": address, "device": device, "found": device is not None}
	except Exception as e:
		print(f"Error scanning device {address}: {e}")
		return {"address": address, "device": None, "found": False, "error": str(e)}

async def scan_devices(known_devices: list[str], timeout: int):
	print(f"Scanning for {len(known_devices)} devices with timeout {timeout} seconds")
	# Mark scanning active
	start_time = time.time()
	result = {"found_devices": [], "run_time": 0}

	tasks = []

	# connect to known devices
	for address in known_devices:
		tasks.append(scan_device(address, timeout))

	results = await asyncio.gather(*tasks)
	result["found_devices"] = list(map(lambda x: x["address"], results))

	end_time = time.time()
	result["run_time"] = end_time - start_time
	print(f"Result: {result}")
	# Mark scanning done
	print(json.dumps(result))

class Config(TypedDict):
	"""
	devices_list: list of device addresses. Can't be empty
	automatic_scan: automatic scan in seconds. False to disable automatic scan
	scan_timeout: scan timeout in seconds. Must be greater than 0
	mqtt_host: MQTT host
	mqtt_port: MQTT port
	mqtt_username: MQTT username
	mqtt_password: MQTT password
	"""
	devices_list: list[str]
	automatic_scan: int | False
	scan_timeout: int
	mqtt_host: str
	mqtt_port: int
	mqtt_username: str
	mqtt_password: str

async def main(): 
	# read devices_list from config.json
	config = await Config.from_json(json.load(open("config.json")))

	# Start MQTT client in background
	start_mqtt_loop(config.mqtt_host, config.mqtt_port, config.mqtt_username, config.mqtt_password)
	
	# Initialize MQTT listeners
	initListeners()

	try:
		if config.automatic_scan:
			while True:
				await asyncio.sleep(config.automatic_scan)
				await scan_devices(config.devices_list, config.scan_timeout)
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



