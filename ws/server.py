import asyncio
import websockets
import json
import signal
from urllib.parse import urlparse, parse_qs

CLIENTS = set()

SECRET_TOKEN = "my_secure_token"

def log(event, websocket, extra=None):
    print(json.dumps({
        "event": event,
        "client": id(websocket),
        "extra": extra
    }))


async def authenticate(path):
    query = parse_qs(urlparse(path).query)
    token = query.get("token", [None])[0]
    return token == SECRET_TOKEN


async def handler(websocket):
    # ---- AUTH ----
    if not await authenticate(websocket.request.path):
        await websocket.close(code=4401, reason="Unauthorized")
        log("auth_failed", websocket)
        return

    # ---- CONNECT EVENT ----
    CLIENTS.add(websocket)
    log("connect", websocket)

    try:
        async for message in websocket:
            # message event
            log("message", websocket, message)

            await websocket.send(f"echo: {message}")

            others = CLIENTS - {websocket}
            data = json.dumps({
                "from": id(websocket),
                "msg": message
            })
            websockets.broadcast(others, data)

    except websockets.ConnectionClosed:
        pass

    finally:
        CLIENTS.discard(websocket)

        # ---- DISCONNECT EVENT ----
        log("disconnect", websocket)


async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Server running on ws://0.0.0.0:8765")
        await stop


if __name__ == "__main__":
    asyncio.run(main())