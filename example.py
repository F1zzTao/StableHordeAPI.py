import asyncio

from stablehorde_api import StableHordeAPI

async def main():
    client = StableHordeAPI("Your Stable Horde token here")
    await client.generate_from_txt(
        "Futuristic cyberpunk landscape, 8k, hyper realistic, cinematic"
    )

asyncio.run(main())
