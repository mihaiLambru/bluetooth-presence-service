#!/usr/bin/env python3
"""
Standalone discovery service that runs independently
"""
import asyncio
import logging
import time
from config import Config
from mqtt.discovery.run_discovery import run_discovery
from mqtt.start_mqtt_loop import start_mqtt_loop, stop_mqtt_loop
from utils.read_config import read_config

logger = logging.getLogger("discovery_service")

async def discovery_service_main():
    """Main function for the discovery service"""
    # Read configuration
    raw_config = read_config()
    if raw_config is None:
        logger.error("Failed to read config. Exiting.")
        return
    
    config = Config.init(raw_config)
    logger.info("Discovery service initialized with config: %s", config)
    
    # Start MQTT client
    start_mqtt_loop(config.mqtt_host, config.mqtt_port, config.mqtt_username, config.mqtt_password)
    
    # Wait a bit for MQTT connection
    await asyncio.sleep(2)
    
    discovery_interval = config.discovery_interval
    logger.info(f"Starting discovery service - running every {discovery_interval} seconds")
    
    shutdown_event = asyncio.Event()
    
    try:
        while not shutdown_event.is_set():
            try:
                logger.info("Running discovery...")
                run_discovery(config.devices_list)
                logger.info("Discovery completed")
                
                # Wait for the interval or shutdown
                await asyncio.wait_for(shutdown_event.wait(), timeout=discovery_interval)
                break  # Event was set, exit loop
            except asyncio.TimeoutError:
                continue  # Timeout reached, run discovery again
            except Exception as e:
                logger.error(f"Error during discovery: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
                
    except KeyboardInterrupt:
        logger.info("Discovery service shutting down...")
    finally:
        stop_mqtt_loop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(discovery_service_main())
