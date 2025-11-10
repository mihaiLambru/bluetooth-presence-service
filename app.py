import asyncio
import logging
from config import Config
from mqtt.start_mqtt_loop import start_mqtt_loop, stop_mqtt_loop
from utils.scan import scan_devices
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
		# Check if automatic_scan exists and is greater than 0
		automatic_scan = config.automatic_scan
		
		if automatic_scan > 0:
			logger.info(f"Starting automatic scan every {automatic_scan} seconds")
			
			while not shutdown_event.is_set():
				
				# Run regular scan
				# config timeout can be changed. 10 seconds it's a safe temporary value
				await scan_devices(config.devices.get_addresses(), 10) # 10 seconds timeout
				
				try:
					await asyncio.wait_for(shutdown_event.wait(), timeout=automatic_scan)
					break  # Event was set, exit loop
				except asyncio.TimeoutError:
					continue  # Timeout reached, continue scanning
		else:
			# Keep the app running even without automatic scanning, but still run discovery
			logger.info("App is running and listening for MQTT events. Press Ctrl+C to exit.")
			
			await shutdown_event.wait()  # Wait indefinitely until shutdown
	except KeyboardInterrupt:
		logger.info("Shutting down...")
		signal_handler()
	finally:
		stop_mqtt_loop()
