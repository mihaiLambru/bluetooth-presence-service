from typing import TypedDict

class ConfigData(TypedDict):
	"""
	Singleton configuration class.
	
	devices_list: list of device addresses. Can't be empty
	automatic_scan: automatic scan in seconds. 0 to disable automatic scan
	scan_timeout: scan timeout in seconds. Must be greater than 0
	mqtt_host: MQTT host
	mqtt_port: MQTT port
	mqtt_username: MQTT username
	mqtt_password: MQTT password
	"""
	devices_list: list[str]
	automatic_scan: int
	scan_timeout: int
	mqtt_host: str
	mqtt_port: int
	mqtt_username: str
	mqtt_password: str

class Config:

	_instance: ConfigData | None = None
	
	def __new__(cls, configData: ConfigData):
		if cls._instance is None:
			cls._instance = super().__new__(cls)  # pyright: ignore[reportAttributeAccessIssue]
		return cls._instance
	
	def __init__(self, configData: ConfigData):
		# Only initialize once
		if not Config._instance:
			self.devices_list: list[str] = configData["devices_list"]
			self.automatic_scan: int = configData["automatic_scan"]
			self.scan_timeout: int = 60
			self.mqtt_host: str = configData["mqtt_host"]
			self.mqtt_port: int = configData["mqtt_port"]
			self.mqtt_username: str = configData["mqtt_username"]
			self.mqtt_password: str = configData["mqtt_password"]

	@staticmethod
	def init(configData: ConfigData) -> ConfigData:
		if (Config._instance is not None):
			return Config._instance
		Config._instance = Config(configData)
		if (Config._instance is not None):
			return Config._instance
		
		raise ValueError("Cannot initialize Config")

	@staticmethod
	def get_instance() -> ConfigData:
		if Config._instance is None:
			raise ValueError("Config not initialized")
		return Config._instance

	@staticmethod
	def set_scan_timeout(scan_timeout: int):
		instance = Config.get_instance()
		
		if scan_timeout <= 0:
			raise ValueError("Scan timeout must be greater than 0")

		instance["scan_timeout"] = scan_timeout

	@staticmethod
	def get_scan_timeout() -> int:
		instance = Config.get_instance()
		return instance["scan_timeout"]