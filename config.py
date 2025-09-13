from typing import Dict, Any

class Config:

	_instance: 'Config | None' = None
	
	def __new__(cls, configData: Dict[str, Any]) -> 'Config':
		if cls._instance is None:
			cls._instance = super().__new__(cls)  # pyright: ignore[reportAttributeAccessIssue]
		return cls._instance
	
	def __init__(self, configData: Dict[str, Any]) -> None:
		# Only initialize once
		if not hasattr(self, '_initialized'):
			self.devices_list: list[str] = configData["devices_list"]
			self.automatic_scan: int = configData["automatic_scan"]
			self.scan_timeout: int = configData.get("scan_timeout", 60)
			self.mqtt_host: str = configData["mqtt_host"]
			self.mqtt_port: int = configData["mqtt_port"]
			self.mqtt_username: str = configData["mqtt_username"]
			self.mqtt_password: str = configData["mqtt_password"]
			self._initialized = True

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