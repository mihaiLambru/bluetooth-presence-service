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

scanning_filters: BlueZDiscoveryFilters = {
	# "Transport": "le",
	"DuplicateData": True,
	"RSSI": -90
}

async def scan_device(address: str, timeout: int) -> None:
	await scan_devices([address], timeout)

async def scan_devices(known_devices: list[str], timeout: int):
	logger.info(f"Scanning for {len(known_devices)} devices with timeout {timeout} seconds")
	
	if not known_devices:
		logger.warning("No devices to scan")
		return

	not_found_devices = known_devices.copy()
	stop_event = asyncio.Event()

	def on_device_found(device: BLEDevice, advertisement_data: AdvertisementData):
		if device.address not in not_found_devices:
			return
		try:
			logger.info('Device details: %s, %s', device, advertisement_data)
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
	scanner = BleakScanner(detection_callback=on_device_found, scanning_filters=scanning_filters, scanning_mode='active')
	try: 
		logger.info("Starting scanner")
		await scanner.start()
		logger.info("Scanner started")
		await asyncio.sleep(timeout)
		logger.info("Stopping scanner")
		await scanner.stop()
	except Exception as e:
		logger.error(f"Error starting scanner: {e}")
	finally:
		await scanner.stop()

	logger.info("Scanner stopped")

	for address in not_found_devices:
		sendDeviceNotHomeEvent(address)
			
