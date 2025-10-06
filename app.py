import asyncio
import logging
import time
from config import Config
from mqtt.start_mqtt_loop import start_mqtt_loop, stop_mqtt_loop
from utils.scan import scan_devices
from utils.read_config import read_config
from mqtt.discovery.run_discovery import run_discovery

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
		discovery_interval = config.discovery_interval
		last_discovery_time = 0
		
		if automatic_scan > 0:
			logger.info(f"Starting automatic scan every {automatic_scan} seconds")
			logger.info(f"Running discovery every {discovery_interval} seconds")
			
			while not shutdown_event.is_set():
				current_time = time.time()
				
				# Run discovery every hour
				if current_time - last_discovery_time >= discovery_interval:
					logger.info("Running periodic discovery...")
					run_discovery(config.devices_list)
					last_discovery_time = current_time
				
				# Run regular scan
				await scan_devices(config.devices_list, config.scan_timeout)
				
				try:
					await asyncio.wait_for(shutdown_event.wait(), timeout=automatic_scan)
					break  # Event was set, exit loop
				except asyncio.TimeoutError:
					continue  # Timeout reached, continue scanning
		else:
			# Keep the app running even without automatic scanning, but still run discovery
			logger.info("App is running and listening for MQTT events. Press Ctrl+C to exit.")
			logger.info(f"Running discovery every {discovery_interval} seconds")
			
			# Run discovery periodically even without scanning
			async def periodic_discovery():
				while not shutdown_event.is_set():
					try:
						await asyncio.sleep(discovery_interval)
						if not shutdown_event.is_set():
							logger.info("Running periodic discovery...")
							run_discovery(config.devices_list)
					except Exception as e:
						logger.error(f"Error in periodic discovery: {e}")
			
			# Start periodic discovery task
			discovery_task = asyncio.create_task(periodic_discovery())
			
			try:
				await shutdown_event.wait()  # Wait indefinitely until shutdown
			finally:
				discovery_task.cancel()
				try:
					await discovery_task
				except asyncio.CancelledError:
					pass
	except KeyboardInterrupt:
		logger.info("Shutting down...")
		signal_handler()
	finally:
		stop_mqtt_loop()
