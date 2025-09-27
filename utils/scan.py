import asyncio, time
import logging
from typing import Any, Coroutine
from typing import List
from bleak import BleakScanner
from components.device_tracker import sendDeviceHomeEvent, sendDeviceNotHomeEvent
from mqtt.send_event import DeviceStatusUpdateData

logger = logging.getLogger("scan")

scanner: BleakScanner = BleakScanner()

async def scan_device(address: str, timeout: int) -> DeviceStatusUpdateData:
	"""Scan for a single device by address"""
	if (address == ""):
		raise ValueError("Device address cannot be empty")

	logger.info(f"Scanning device {address} with timeout {timeout} seconds")
	try:
		# Add extra timeout protection to prevent hanging
		device = await asyncio.wait_for(
			scanner.find_device_by_address(address, timeout),
			timeout=timeout + 5  # Add 5 seconds buffer
		)

		if device is None:
			logger.info(f"Device {address} not found")
			sendDeviceNotHomeEvent(address)
			return DeviceStatusUpdateData(address=address, device=None, found=False)

		try:
			details = device.details
			logger.debug(f"Device details: {details}")
		except Exception as e:
			logger.error(f"Error getting device details: {e}")

		logger.info(f"Found device: {getattr(device, 'name', 'Unknown')}")

		send_device_data = DeviceStatusUpdateData(address=address, device=device, found=True)
		sendDeviceHomeEvent(send_device_data)

		return send_device_data
	except asyncio.TimeoutError:
		logger.warning(f"Timeout scanning device {address} after {timeout + 5} seconds")
		sendDeviceNotHomeEvent(address)
		return DeviceStatusUpdateData(address=address, device=None, found=False)
	except Exception as e:
		logger.error(f"Error scanning device {address}: {e}")
		sendDeviceNotHomeEvent(address)
		return DeviceStatusUpdateData(address=address, device=None, found=False)

async def scan_devices(known_devices: list[str], timeout: int):
	logger.info(f"Scanning for {len(known_devices)} devices with timeout {timeout} seconds")
	
	if not known_devices:
		logger.warning("No devices to scan")
		return
	
	# Mark scanning active
	start_time = time.time()
	tasks: List[Coroutine[Any, Any, DeviceStatusUpdateData]] = []

	# connect to known devices
	for address in known_devices:
		tasks.append(scan_device(address, timeout))

	try:
		results = await asyncio.gather(*tasks, return_exceptions=True)
		
		# Log any exceptions that occurred
		for i, result in enumerate(results):
			if isinstance(result, Exception):
				logger.error(f"Exception scanning device {known_devices[i]}: {result}")
		
		end_time = time.time()
		logger.info(f"Scanning done in {end_time - start_time:.2f} seconds")
		
	except Exception as e:
		end_time = time.time()
		logger.error(f"Critical error during scanning after {end_time - start_time:.2f} seconds: {e}")
		raise
