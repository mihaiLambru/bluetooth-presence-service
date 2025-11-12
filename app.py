import asyncio
import logging

from config import Config
from mqtt.start_mqtt_loop import start_mqtt_loop, stop_mqtt_loop
from utils.scan import BluetoothScanner
from utils.read_config import read_config

logger = logging.getLogger("app")

async def app_main(): 
	# read devices_list from config.json
	raw_config = read_config()
	if raw_config is None:
		logger.error("Failed to read config. Exiting.")
		return
	logger.info("Raw config read: %s", raw_config)
	config = Config.init(raw_config)
	logger.info("Config initialized: %s", config)
	# Start MQTT client in background
	start_mqtt_loop(config.mqtt_host, config.mqtt_port, config.mqtt_username, config.mqtt_password)

	# Create a shutdown event
	shutdown_event = asyncio.Event()
	
	def signal_handler():
		logger.info("Shutdown signal received")
		shutdown_event.set()

	try:
		await BluetoothScanner().scan_loop(shutdown_event)
	except KeyboardInterrupt:
		logger.info("Shutting down...")
		signal_handler()
	except Exception as e:
		logger.error("Error in app: %s", e)
	finally:
		stop_mqtt_loop()
