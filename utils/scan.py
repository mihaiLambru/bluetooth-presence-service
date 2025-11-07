import pprint
import asyncio, time
import logging
from typing import Any, Coroutine
from typing import List
from bleak import BleakScanner
from bleak.args.bluez import BlueZDiscoveryFilters
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from components.device_tracker import sendDeviceHomeEvent, sendDeviceNotHomeEvent
from config import Config
from mqtt.send_event import DeviceStatusUpdateData

logger = logging.getLogger("scan")

scanner: BleakScanner | None = None
scanner_lock = asyncio.Lock()

def on_device_found(device: BLEDevice, advertisement_data: AdvertisementData):
	logger.info('Device found: %s, %s', device, advertisement_data)
	try:
		if device.name is not None:
			Config.set_device_name(device.address, device.name)
		formattedDevice = pprint.pformat(device, width=100, depth=3)
		formattedAdvertisementData = pprint.pformat(advertisement_data, width=100, depth=3)
		logger.info('%s: %s', 'device', formattedDevice)
		logger.info('%s: %s', 'advertisement_data', formattedAdvertisementData)
	except Exception as e:
		logger.warning('%s: %r (pprint failed: %s)', 'device', e)
		logger.warning('%s: %r (pprint failed: %s)', 'advertisement_data', e)

async def get_scanner():
	global scanner
	async with scanner_lock:
		if scanner is None:
			logger.info("Creating new scanner")
			scanning_filters: BlueZDiscoveryFilters = {
				"Transport": "le",
				"DuplicateData": False,
				"RSSI": -90
			}
			scanner = BleakScanner(discovery_callback=on_device_found, scanning_filters=scanning_filters)
			return scanner
		else: 
			return scanner

async def remove_scanner():
	global scanner
	async with scanner_lock:
		if scanner is not None:
			logger.info("Removing scanner")
			await scanner.stop()
			scanner = None

async def scan_device(address: str, timeout: int) -> None:
	"""Scan for a single device by address"""
	scanner = await get_scanner()
	await _scan_device(address, timeout, scanner)
	await remove_scanner()

async def _scan_device(address: str, timeout: int, scanner: BleakScanner) -> None:
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

			return
		try:
			details = device.details
			logger.debug(f"Device details: {details}")
		except Exception as e:
			logger.error(f"Error getting device details: {e}")

		logger.info(f"Found device: {getattr(device, 'name', 'Unknown')}")

		send_device_data = DeviceStatusUpdateData(address=address, device=device, found=True)
		sendDeviceHomeEvent(send_device_data)
	except asyncio.TimeoutError:
		logger.warning(f"Timeout scanning device {address} after {timeout + 5} seconds")
		sendDeviceNotHomeEvent(address)

	except Exception as e:
		logger.error(f"Error scanning device {address}: {e}")
		sendDeviceNotHomeEvent(address)

async def scan_devices(known_devices: list[str], timeout: int):
	logger.info(f"Scanning for {len(known_devices)} devices with timeout {timeout} seconds")
	
	if not known_devices:
		logger.warning("No devices to scan")
		return
	
	# Mark scanning active
	start_time = time.time()
	tasks: List[Coroutine[Any, Any, None]] = []

	# connect to known devices
	scanner = await get_scanner()
	for address in known_devices:
		# this won't work because we need one scanner for each device
		tasks.append(_scan_device(address, timeout, scanner))

	try:
		results = await asyncio.gather(*tasks, return_exceptions=True)
		await remove_scanner()
		
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
