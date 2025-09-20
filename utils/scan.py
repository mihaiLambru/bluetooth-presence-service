import asyncio, time
import logging
from typing import Any, Coroutine
from typing import List
from bleak import BleakScanner
from components.device_tracker import sendDeviceHomeEvent, sendDeviceNotHomeEvent
from mqtt.send_event import DeviceStatusUpdateData

logger = logging.getLogger("scan")

async def scan_device(address: str, timeout: int) -> DeviceStatusUpdateData:
	"""Scan for a single device by address"""
	if (address == ""):
		raise ValueError("Device address cannot be empty")

	logger.info(f"Scanning device {address} with timeout {timeout} seconds")
	try:
		device = await BleakScanner().find_device_by_address(address, timeout)

		if device is None:
			raise Exception("Device not found")

		details = device.details

		try:
			logger.debug(f"Device details: {repr(details)}")
		except Exception as e:
			logger.error(f"Error getting device details: {e}")

		logger.info(f"Found device: {getattr(device, 'name', 'Unknown')}")

		send_device_data = DeviceStatusUpdateData(address=address, device=device, found=True)

		sendDeviceHomeEvent(send_device_data)

		return send_device_data
	except Exception as e:
		logger.error(f"Error scanning device {address}: {e}")
		sendDeviceNotHomeEvent(address)

		return DeviceStatusUpdateData(address=address, device=None, found=False)

async def scan_devices(known_devices: list[str], timeout: int):
	logger.info(f"Scanning for {len(known_devices)} devices with timeout {timeout} seconds")
	# Mark scanning active
	start_time = time.time()
	tasks: List[Coroutine[Any, Any, DeviceStatusUpdateData]] = []

	# connect to known devices
	for address in known_devices:
		tasks.append(scan_device(address, timeout))

	await asyncio.gather(*tasks)

	end_time = time.time()

	# Mark scanning done
	logger.info(f"Scanning done in {end_time - start_time} seconds")
	# print(json.dumps(results))
