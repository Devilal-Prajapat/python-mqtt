import asyncio
import websockets
import json
import random
import time

SERVER_URI = "ws://localhost:8765/?token=my_secure_token"
DEVICE_ID = "stm32-01"

def log(event, websocket, extra=None):
    print(json.dumps({
        "event": event,
        "client": id(websocket),
        "extra": extra
    }))

async def handle_command(ws, msg):
    data = json.loads(msg)
    if data["type"] == "command":
        cmd = data["cmd"]
        print(f"[COMMAND RECEIVED] {cmd}")

        # ---- simulate device action ----
        if cmd == "ping":
            await ws.send(json.dumps({
                "type": "pull",
                "cmd": "ping_response",
                "status": "ok"
            }))

        elif cmd == "led_toggle":
            print("Toggling LED (simulated)")
            await ws.send(json.dumps({
                "type": "pull",
                "cmd": "led_toggle_ack",
                "status": "done"
            }))

    elif data["type"] == "attached":
        print(f"[ATTACHED] {data['device_id']}")

async def heartbeat(ws, device_id):
    try:
        while True:
            log("heartbeat", ws)
            await ws.send(json.dumps({
                "type": "heartbeat",
                "device_id": device_id,
                "timestamp": int(time.time())
            }))
            await asyncio.sleep(5)
    except (websockets.ConnectionClosed, asyncio.CancelledError):
        pass

async def device_client():
    while True:
        try:
            async with websockets.connect(SERVER_URI) as ws:
                log("connected",ws)
                # ---- ATTACH DEVICE ----
                await ws.send(json.dumps({
                    "type": "attach",
                    "device_id": DEVICE_ID
                }))
                
                # ---- LISTEN LOOP ----
                attached = False
                try:
                    async for message in ws:
                        data = json.loads(message)
                        if data["type"] == "attached":
                            if not attached:
                                attached = True
                                hb_task = asyncio.create_task(
                                    heartbeat(ws, DEVICE_ID)
                                )
                        else:
                            await handle_command(ws, message)
                finally:
                    hb_task.cancel()

        except Exception as e:
            log("dsiconnected",ws)
            wait = random.uniform(1, 3)
            print(f"[DISCONNECTED] {e}, retrying in {wait:.1f}s")
            await asyncio.sleep(wait)

if __name__ == "__main__":
    asyncio.run(device_client())