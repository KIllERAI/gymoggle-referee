import asyncio
import json
import random
import websockets

SERVER = "ws://localhost:8765"


async def main():
    async with websockets.connect(SERVER) as ws:
        me = None
        reps = 0
        playing = False

        async def sender():
            nonlocal reps
            while True:
                await asyncio.sleep(random.uniform(0.5, 1.5))
                if playing:
                    reps += 1
                    await ws.send(json.dumps({"type": "reps", "reps": reps}))

        asyncio.create_task(sender())

        async for raw in ws:
            data = json.loads(raw)
            t = data.get("type")
            if t == "assigned":
                me = data["you"]
                print(f"I am {me}")
            elif t == "start":
                playing = True
                print(f"Match started! ({data['duration']}s)")
            elif t == "scores":
                print("scores:", data["scores"])
            elif t == "end":
                playing = False
                result = "WIN" if data["winner"] == me else ("TIE" if data["winner"] == "TIE" else "LOSE")
                print(f"MATCH OVER — I am {me}, result: {result}, final: {data['scores']}")
                break
            elif t == "full":
                print("Server full")
                break


asyncio.run(main())