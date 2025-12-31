from datetime import datetime
from enum import StrEnum
from typing import Dict, Any, Iterator, Optional

from mqtt.types import HomeState

class ScanPreset(StrEnum):
	often = "often"
	balanced = "balanced"
	rarely = "rarely"
	never = "never"
	continuous = "continuous"

SCAN_PRESET_INTERVALS: dict[ScanPreset, int | None] = {
	ScanPreset.often: 30,
	ScanPreset.balanced: 600,
	ScanPreset.rarely: 3600,
	ScanPreset.never: None,
	ScanPreset.continuous: 0,
}

DEFAULT_SCAN_PRESET = ScanPreset.balanced

class Device:
	def __init__(self, address: str, name: str | None = None):
		self.address = address
		self.name = name
		self.rssi: int | None = None
		self.state: HomeState | None = None
		self.last_seen: datetime | None = None

	def mark_home(self, rssi: int, seen_at: datetime) -> None:
		self.rssi = rssi
		self.state = HomeState.home
		self.last_seen = seen_at

	def mark_not_home(self) -> None:
		self.state = HomeState.not_home

class DevicesList:
	def __init__(self, devices: list[Device]):
		self.devices = devices
	def _find_device(self, address: str) -> Device:
		matches = list(filter(lambda device: device.address == address, self.devices))
		if len(matches) == 0:
			raise ValueError(f"Device with address {address} not found")
		return matches[0]
	def get_addresses(self) -> list[str]:
		return [device.address for device in self.devices]
	def __getitem__(self, address: str) -> Device:
		return self._find_device(address)
	def set_device_name(self, address: str, name: str) -> None:
		device = self._find_device(address)
		device.name = name
	def __setitem__(self, address: str, name: str) -> None:
		self.set_device_name(address, name)
	def __iter__(self) -> Iterator[Device]:
		return iter(self.devices)

class Config:

	_instance: 'Config | None' = None
	
	def __new__(cls, configData: Dict[str, Any]) -> 'Config':
		if cls._instance is None:
			cls._instance = super().__new__(cls)  # pyright: ignore[reportAttributeAccessIssue]
		return cls._instance

	def _get_devices_list_from_config(self, config_devices_list: list[dict[str, Any] | str]) -> list[Device]:
		devices_list: list[Device] = []
		for device in config_devices_list:
			if isinstance(device, str):
				devices_list.append(Device(device))
			elif isinstance(device, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
				devices_list.append(Device(device["address"], device["name"]))
			else:
				raise ValueError(f"Invalid device: {device}")
		return devices_list
	
	def __init__(self, configData: Dict[str, Any]) -> None:
		# Only initialize once
		if not hasattr(self, '_initialized'):
			# use only devices
			devices_list = self._get_devices_list_from_config(configData["devices_list"])
			self.devices: DevicesList = DevicesList(devices_list)

			self.automatic_scan_preset: ScanPreset = DEFAULT_SCAN_PRESET
			self.automatic_scan: int | None = self._get_interval_for_preset(self.automatic_scan_preset)
			self.scan_timeout: int = configData.get("scan_timeout", 60)
			self.discovery_interval: int = configData.get("discovery_interval", 3600)  # Default 1 hour
			self.mqtt_host: str = configData["mqtt_host"]
			self.mqtt_port: int = configData["mqtt_port"]
			self.mqtt_username: str = configData["mqtt_username"]
			self.mqtt_password: str = configData["mqtt_password"]
			self._initialized = True

	def _get_interval_for_preset(self, preset: ScanPreset) -> int | None:
		return SCAN_PRESET_INTERVALS.get(preset, SCAN_PRESET_INTERVALS[DEFAULT_SCAN_PRESET])

	def _parse_scan_preset(self, preset_value: Optional[str]) -> ScanPreset | None:
		if preset_value is None:
			return None
		try:
			return ScanPreset(preset_value)
		except ValueError:
			return None

	def _infer_scan_preset_from_seconds(self, interval_seconds: Any) -> ScanPreset:
		if isinstance(interval_seconds, (int, float)):
			if interval_seconds <= 0:
				return ScanPreset.never
			for preset, interval in SCAN_PRESET_INTERVALS.items():
				if interval is not None and interval == int(interval_seconds):
					return preset
		return DEFAULT_SCAN_PRESET

	@staticmethod
	def set_device_name(device_address: str, device_name: str) -> None:
		instance = Config.get_instance()
		instance.devices[device_address] = device_name
	
	@staticmethod
	def get_device_name(device_address: str) -> str | None:
		instance = Config.get_instance()
		device = instance.devices[device_address]
		return device.name

	@staticmethod
	def init(configData: Dict[str, Any]) -> 'Config':
		if Config._instance is not None:
			return Config._instance
		Config._instance = Config(configData)
		return Config._instance

	@staticmethod
	def get_instance() -> 'Config':
		if Config._instance is None:
			raise ValueError("Config not initialized")
		return Config._instance

	@staticmethod
	def set_scan_timeout(scan_timeout: int) -> None:
		instance = Config.get_instance()
		
		if scan_timeout <= 0:
			raise ValueError("Scan timeout must be greater than 0")

		instance.scan_timeout = scan_timeout

	@staticmethod
	def get_scan_timeout() -> int:
		instance = Config.get_instance()
		return instance.scan_timeout

	@staticmethod
	def set_scan_preset(preset_value: str) -> ScanPreset:
		instance = Config.get_instance()

		preset = instance._parse_scan_preset(preset_value)
		if preset is None:
			raise ValueError(f"Invalid scan preset: {preset_value}")

		instance.automatic_scan_preset = preset
		instance.automatic_scan = instance._get_interval_for_preset(preset)
		return preset

	@staticmethod
	def get_scan_preset() -> ScanPreset:
		instance = Config.get_instance()
		return instance.automatic_scan_preset

	@staticmethod
	def get_automatic_scan_interval() -> int | None:
		instance = Config.get_instance()
		return instance.automatic_scan