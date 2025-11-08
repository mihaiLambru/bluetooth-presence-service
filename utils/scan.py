import pprint
import asyncio
import logging
from bleak import BleakScanner
from bleak.args.bluez import BlueZDiscoveryFilters
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from components.device_tracker import sendDeviceHomeEvent, sendDeviceNotHomeEvent
from config import Config
from mqtt.send_event import DeviceStatusUpdateData

logger = logging.getLogger("scan")

def on_device_found(device: BLEDevice, advertisement_data: AdvertisementData):
	logger.info('Device found: %s, %s', device, advertisement_data)
	try:
		if device.name is not None:
			Config.set_device_name(device.address, device.name)
		deviceData = DeviceStatusUpdateData(address=device.address, device=device, found=True)
		sendDeviceHomeEvent(deviceData)

		# logs
		formattedDevice = pprint.pformat(device, width=100, depth=3)
		formattedAdvertisementData = pprint.pformat(advertisement_data, width=100, depth=3)
		logger.info('%s: %s', 'device', formattedDevice)
		logger.info('%s: %s', 'advertisement_data', formattedAdvertisementData)
	except Exception as e:
		logger.warning('%s: %r (pprint failed: %s)', 'device', e)
		logger.warning('%s: %r (pprint failed: %s)', 'advertisement_data', e)

async def create_scanner():
	logger.debug("Creating new scanner")
	scanning_filters: BlueZDiscoveryFilters = {
		"Transport": "le",
		"DuplicateData": False,
		"RSSI": -90
	}
	scanner = BleakScanner(discovery_callback=on_device_found, scanning_filters=scanning_filters)
	await scanner.start()

	return scanner

async def scan_device(address: str, timeout: int) -> None:
	"""Scan for a single device by address"""
	await _scan_device(address, timeout)

async def _scan_device(address: str, timeout: int) -> None:
	"""Scan for a single device by address"""
	if (address == ""):
		raise ValueError("Device address cannot be empty")

	logger.info(f"Scanning device {address} with timeout {timeout} seconds")
	try:
		# Add extra timeout protection to prevent hanging
		device = await asyncio.wait_for(
			BleakScanner.find_device_by_address(address, timeout),
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
	
	scanning_filters: BlueZDiscoveryFilters = {
		"Transport": "le",
		"DuplicateData": False,
		"RSSI": -90
	}

	not_found_devices = known_devices.copy()
	stop_event = asyncio.Event()

	def on_device_found(device: BLEDevice, advertisement_data: AdvertisementData):
		if device.address not in not_found_devices:
			return
		try:
			logger.info('Device found: %s, %s', device, advertisement_data)
			if device.name is not None:
				Config.set_device_name(device.address, device.name)
			deviceData = DeviceStatusUpdateData(address=device.address, device=device, found=True)
			sendDeviceHomeEvent(deviceData)
			not_found_devices.remove(device.address)
			if len(not_found_devices) == 0:
				logger.info("All devices found")
				stop_event.set()
				return
			# logs
			formattedDevice = pprint.pformat(device, width=100, depth=3)
			formattedAdvertisementData = pprint.pformat(advertisement_data, width=100, depth=3)
			logger.info('%s: %s', 'device', formattedDevice)
			logger.info('%s: %s', 'advertisement_data', formattedAdvertisementData)
		except Exception as e:
			logger.error(f"Error processing device {device.address}: {e}")

	logger.info("Starting scanner")
	async with BleakScanner(detection_callback=on_device_found, scanning_filters=scanning_filters):
		logger.info("Scanner started")
		stop_event_after_timeout = asyncio.create_task(stop_event.wait())
		try:
			await asyncio.wait_for(stop_event_after_timeout, timeout=timeout)
		except asyncio.TimeoutError:
			logger.info("Timeout reached")
			stop_event.set()
		except Exception as e:
			logger.error(f"Error waiting for stop event: {e}")
		logger.info("Stopping scanner")

	logger.info("Scanner stopped")

	for address in not_found_devices:
		sendDeviceNotHomeEvent(address)
			
