import asyncio
from app import app_main
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

async def main(): 
    try:
        await app_main()
    except Exception as e:
        logging.error("Error in main: %s", e)
        sys.exit(1)

if __name__ == "__main__":
	asyncio.run(main())



