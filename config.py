from typing import Dict, Any, Iterator

class Device:
	def __init__(self, address: str, name: str | None = None):
		self.address = address
		self.name = name

class DevicesList:
	def __init__(self, devices: list[Device]):
		self.devices = devices
	def _find_device(self, address: str) -> Device:
		matches = list(filter(lambda device: device.address == address, self.devices))
		if len(matches) == 0:
			raise ValueError(f"Device with address {address} not found")
		return matches[0]
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
	
	def __init__(self, configData: Dict[str, Any]) -> None:
		# Only initialize once
		if not hasattr(self, '_initialized'):
			# use only devices
			self.devices_list: list[str] = configData["devices_list"] # this should be removed in the future
			self.devices: DevicesList = DevicesList([Device(address) for address in configData["devices_list"]])
			self.automatic_scan: int = configData["automatic_scan"]
			self.scan_timeout: int = configData.get("scan_timeout", 60)
			self.discovery_interval: int = configData.get("discovery_interval", 3600)  # Default 1 hour
			self.mqtt_host: str = configData["mqtt_host"]
			self.mqtt_port: int = configData["mqtt_port"]
			self.mqtt_username: str = configData["mqtt_username"]
			self.mqtt_password: str = configData["mqtt_password"]
			self._initialized = True

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