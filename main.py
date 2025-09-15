import asyncio
from app import app_main
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

async def main(): 
	await app_main()

if __name__ == "__main__":
	asyncio.run(main())



