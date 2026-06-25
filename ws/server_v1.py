import asyncio
import websockets
import json
import signal
from urllib.parse import urlparse, parse_qs
import time

SESSIONS = {}

device_registry = {
    "stm32-01": {
        "model": "STM32H7",
        "owner": "lab"
    },
    "esp32-dev": {
        "model": "ESP32-S3",
        "owner": "qa"
    }
}
 
SECRET_TOKEN = "my_secure_token"

def log(event, websocket, extra=None):
    print(json.dumps({
        "event": event,
        "client": id(websocket),
        "extra": extra
    }))

# ---- external device registry (mock) ----
async def device_exists(device_id):
    # replace with DB / API call
    return device_id in device_registry


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
    # CLIENTS.add(websocket)
    log("connect", websocket)

    device_id = None

    try:
        async for message in websocket:
            log("message",websocket, message)
            data = json.loads(message)
            msg_type = data.get("type")

            # ---- DEVICE ATTACH ----
            if msg_type == "attach":

                device_id = data["device_id"]

                # 1. verify registry
                if not await device_exists(device_id):
                    await websocket.close(code=4404, reason="Device not found")
                    return

                # 2. attach session
                old = SESSIONS.get(device_id)
                if old:
                    await old.close(code=4000, reason="Replaced session")

                SESSIONS[device_id] = websocket

                await websocket.send(json.dumps({
                    "type": "attached",
                    "device_id": device_id
                }))

                print(f"[ATTACH] {device_id}")

            # ---- DEVICE PULL REQUEST ----
            elif msg_type == "pull":
                print(f"[PULL] {device_id}: {data}")

                await websocket.send(json.dumps({
                    "type": "response",
                    "data": "ok"
                }))

    finally:
        if device_id and SESSIONS.get(device_id) == websocket:
            del SESSIONS[device_id]
            print(f"[DISCONNECT] {device_id}")
            log("disconnect", websocket)


"""
{
  "type": "command",
  "cmd": "led_toggle",
  "payload": {
    "led": 1
  }
}
"""

async def send_command(device_id, command, payload=None):
    ws = SESSIONS.get(device_id)
    if ws is None:
        return False

    await ws.send(json.dumps({
        "type": "command",
        "cmd": command,
        "payload": payload or {}
    }))
    return True

async def command_loop(device_id):
    while True:
        await asyncio.sleep(10)  # every 30 seconds
        await send_command(device_id,"led_toggle",{"led":1})
       
async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Server running on ws://0.0.0.0:8765")
        asyncio.create_task(command_loop("stm32-01"))
    
        await stop


if __name__ == "__main__":
    asyncio.run(main())