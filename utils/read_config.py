import json
import logging

logger = logging.getLogger("utils.read_config")

def read_config():
	try:
		with open("config.json", "r", encoding="utf-8") as f:
			config = json.load(f)
			logger.info("Successfully read config: %s", config)

			return config
	except FileNotFoundError:
		logger.error("File not found")
	except json.JSONDecodeError as e:
		logger.error(f"Invalid JSON: {e}")
