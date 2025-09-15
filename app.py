import asyncio
import logging
from config import Config
from mqtt.discovery.run_discovery import run_discovery
from mqtt.listeners import initListeners
from mqtt.config import start_mqtt_loop, stop_mqtt_loop
from scan import scan_devices
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
	run_discovery(config.devices_list)
	
	# Initialize MQTT listeners
	initListeners()

	try:
		# Check if automatic_scan exists and is greater than 0
		automatic_scan = config.automatic_scan
		if automatic_scan > 0:
			logger.info(f"Starting automatic scan every {automatic_scan} seconds")
			while True:
				await scan_devices(config.devices_list, config.scan_timeout)
				await asyncio.sleep(automatic_scan)
		else:
			# Keep the app running even without automatic scanning
			logger.info("App is running and listening for MQTT events. Press Ctrl+C to exit.")
			while True:
				await asyncio.sleep(2)  # Keep the event loop alive
	except KeyboardInterrupt:
		logger.info("Shutting down...")
	finally:
		stop_mqtt_loop()
