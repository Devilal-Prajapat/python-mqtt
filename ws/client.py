import asyncio
import websockets
import random
import signal

async def connect_with_backoff(uri):
    delay = 1

    while True:
        try:
            async with websockets.connect(uri) as ws:
                print("Connected")
                delay = 1

                async for message in ws:
                    print(f"Received: {message}")

        except (websockets.ConnectionClosed, OSError) as e:
            jitter = random.uniform(0, delay * 0.5)
            wait = min(delay + jitter, 30)
            print(f"Disconnected ({e}), retry in {wait:.1f}s")
            await asyncio.sleep(wait)
            delay = min(delay * 2, 30)


async def main():
    task = asyncio.create_task(
        connect_with_backoff("ws://localhost:8765/?token=my_secure_token")
    )

    try:
        await task
    except asyncio.CancelledError:
        print("Shutting down...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped")