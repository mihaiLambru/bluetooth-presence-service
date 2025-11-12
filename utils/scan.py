import asyncio
import logging
import pprint
from dataclasses import dataclass
from typing import Any, Optional

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
    "DuplicateData": False,
    # "RSSI": -90
}

@dataclass
class ScanContext:
    not_found_devices: set[str]
    stop_event: asyncio.Event


class BluetoothScanner:
    def __init__(self):
        self._scanner_kwargs: dict[str, Any] = {}
        self._scanner_kwargs["detection_callback"] = self._on_device_found
        self._scanner_kwargs["scanning_filters"] = scanning_filters
        self._scanner_kwargs["scanning_mode"] = "active"
        self._scanner: BleakScanner = BleakScanner(**self._scanner_kwargs)
        self._current_scan: Optional[ScanContext] = None
        self._lock: Optional[asyncio.Lock] = None

    async def scan_device(self, address: str, timeout: int) -> None:
        await self.scan_devices([address], timeout)

    async def scan_devices(self, known_devices: list[str], timeout: int) -> None:
        logger.info(
            "Scanning for %d devices with timeout %d seconds",
            len(known_devices),
            timeout,
        )

        if not known_devices:
            logger.warning("No devices to scan")
            return

        lock = self._ensure_lock()
        missing_devices: list[str] = []

        async with lock:
            self._scanner_kwargs["detection_callback"] = self._on_device_found
            context = ScanContext(
                not_found_devices=set(known_devices),
                stop_event=asyncio.Event(),
            )
            self._current_scan = context

            try:
                logger.info("Starting scanner")
                await self._start_scanner()
                logger.info("Scanner started")
                try:
                    await asyncio.wait_for(context.stop_event.wait(), timeout=timeout)
                    logger.info("Stopping scanner after devices were found")
                except asyncio.TimeoutError:
                    logger.info("Scan timed out after %d seconds", timeout)
            except Exception as exc:
                logger.error("Error during scanning: %s", exc)
            finally:
                await self._stop_scanner()
                missing_devices = sorted(context.not_found_devices)
                self._current_scan = None

        for address in missing_devices:
            sendDeviceNotHomeEvent(address)

    def _ensure_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def _start_scanner(self) -> None:
        try:
            await self._scanner.start()
        except Exception as exc:
            logger.error("Error starting scanner: %s", exc)

    async def _stop_scanner(self) -> None:
        try:
            logger.info("Stopping scanner")
            await self._scanner.stop()
            logger.info("Scanner stopped")
        except Exception as exc:
            logger.error("Error stopping scanner: %s", exc)

    def _on_device_found(
        self, device: BLEDevice, advertisement_data: AdvertisementData
    ) -> None:
        if self._current_scan is None:
            return

        not_found_devices = self._current_scan.not_found_devices
        stop_event = self._current_scan.stop_event

        if device.address not in not_found_devices:
            return

        try:
            logger.info("Device details: %s, %s", device, advertisement_data)
            if device.name is not None:
                Config.set_device_name(device.address, device.name)

            device_data = DeviceStatusUpdateData(
                address=device.address, device=device, found=True
            )
            sendDeviceHomeEvent(device_data)
            not_found_devices.remove(device.address)

            if not not_found_devices:
                logger.info("All devices found")
                stop_event.set()
                return

            formatted_device = pprint.pformat(device, width=100, depth=3)
            formatted_advertisement_data = pprint.pformat(
                advertisement_data, width=100, depth=3
            )
            logger.info("%s: %s", "device", formatted_device)
            logger.info("%s: %s", "advertisement_data", formatted_advertisement_data)
        except Exception as exc:
            logger.error(
                "Error processing device %s: %s",
                getattr(device, "address", "unknown"),
                exc,
            )


bluetooth_scanner = BluetoothScanner()


scan_device = bluetooth_scanner.scan_device
scan_devices = bluetooth_scanner.scan_devices
