import asyncio, json, time
from typing import Any, Coroutine
from typing import List
from bleak import BleakScanner
from components.device_tracker import sendDeviceHomeEvent, sendDeviceNotHomeEvent
from mqtt.sendEvent import DeviceStatusUpdateData

async def scan_device(address: str, timeout: int) -> DeviceStatusUpdateData:
	"""Scan for a single device by address"""
	if (address == ""):
		raise ValueError("Device address cannot be empty")

	print(f"Scanning device {address} with timeout {timeout} seconds")
	try:
		# timeout 10 minutes
		device = await BleakScanner().find_device_by_address(address, timeout)

		if device is None:
			raise Exception("Device not found")
		
		print(f"Found device {getattr(device, 'name', 'Unknown')} for address {address}")

		send_device_data = DeviceStatusUpdateData(address=address, device=device, found=True)

		sendDeviceHomeEvent(send_device_data)

		return send_device_data
	except Exception as e:
		print(f"Error scanning device {address}: {e}")
		sendDeviceNotHomeEvent(address)

		return DeviceStatusUpdateData(address=address, device=None, found=False)

async def scan_devices(known_devices: list[str], timeout: int):
	print(f"Scanning for {len(known_devices)} devices with timeout {timeout} seconds")
	# Mark scanning active
	start_time = time.time()
	tasks: List[Coroutine[Any, Any, DeviceStatusUpdateData]] = []

	# connect to known devices
	for address in known_devices:
		tasks.append(scan_device(address, timeout))

	results = await asyncio.gather(*tasks)

	end_time = time.time()

	# Mark scanning done
	print(f"Scanning done in {end_time - start_time} seconds")
	print(json.dumps(results))
