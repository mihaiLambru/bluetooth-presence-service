import asyncio, json, time
from bleak import BleakScanner
from mqtt.sendEvent import DeviceStatusUpdateData, SentEvent, sendDeviceUpdateEvent

async def scan_device(address: str, timeout: int):
	"""Scan for a single device by address"""
	try:
		# timeout 10 minutes
		device = await BleakScanner().find_device_by_address(address, timeout)
		print(f"Found device {device.name} for address {address}")

		send_device_data = DeviceStatusUpdateData(address=address, device=device, found=device is not None)

		sendDeviceUpdateEvent(send_device_data)

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
	results = list(filter(lambda x: x["found"], results))
	result["found_devices"] = list(map(lambda x: x["address"], results))

	end_time = time.time()
	result["run_time"] = end_time - start_time

	# Mark scanning done
	print(json.dumps(result))
