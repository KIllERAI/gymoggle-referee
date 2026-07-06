# import asyncio
# import json
# import websockets

# DURATION = 20          # match length in seconds  (set to 10 for quick testing)

# players = {}           # websocket -> {"id": "P1"/"P2", "reps": 0}
# match_started = False


# async def send(ws, payload):
#     try:
#         await ws.send(json.dumps(payload))
#     except Exception:
#         pass


# async def broadcast(payload):
#     await asyncio.gather(*[send(ws, payload) for ws in players])


# def scores_dict():
#     return {p["id"]: p["reps"] for p in players.values()}


# async def run_match():
#     print("Both players in — match starting!")
#     await broadcast({"type": "start", "duration": DURATION})
#     await asyncio.sleep(DURATION)

#     s = scores_dict()
#     if len(s) == 2:
#         p1, p2 = s["P1"], s["P2"]
#         winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
#     else:
#         winner = "TIE"
#     print(f"Match over. Scores: {s}  Winner: {winner}")
#     await broadcast({"type": "end", "winner": winner, "scores": s})


# async def handler(websocket, *args):        # *args keeps it compatible across websockets versions
#     global match_started
#     if len(players) >= 2:
#         await send(websocket, {"type": "full"})   # already 2 players, reject a third
#         return

#     pid = "P1" if len(players) == 0 else "P2"
#     players[websocket] = {"id": pid, "reps": 0}
#     print(f"{pid} connected ({len(players)}/2)")
#     await send(websocket, {"type": "assigned", "you": pid})

#     try:
#         # start the match once both are in
#         if len(players) == 2 and not match_started:
#             match_started = True
#             asyncio.create_task(run_match())

#         async for raw in websocket:
#             data = json.loads(raw)
#             if data.get("type") == "reps":
#                 players[websocket]["reps"] = int(data["reps"])
#                 await broadcast({"type": "scores", "scores": scores_dict()})
#     finally:
#         pid = players.get(websocket, {}).get("id", "?")
#         players.pop(websocket, None)
#         print(f"{pid} disconnected")


# async def main():
#     async with websockets.serve(handler, "0.0.0.0", 8765):
#         print("Referee running on port 8765. Waiting for 2 players…")
#         await asyncio.Future()    # run forever


# asyncio.run(main())
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

DURATION = 20

app = FastAPI()

players = {}           # websocket -> {"id":..., "reps":...}
match_started = False


async def send(ws, payload):
    try:
        await ws.send_text(json.dumps(payload))
    except Exception:
        pass


async def broadcast(payload):
    await asyncio.gather(
        *[send(ws, payload) for ws in list(players.keys())],
        return_exceptions=True,
    )


def scores():
    return {p["id"]: p["reps"] for p in players.values()}


async def run_match():
    global match_started

    print("Both players connected. Starting match.")

    await broadcast({
        "type": "start",
        "duration": DURATION
    })

    await asyncio.sleep(DURATION)

    s = scores()

    if len(s) == 2:
        p1 = s.get("P1", 0)
        p2 = s.get("P2", 0)

        if p1 == p2:
            winner = "TIE"
        elif p1 > p2:
            winner = "P1"
        else:
            winner = "P2"
    else:
        winner = "TIE"

    print("Match finished:", s)

    await broadcast({
        "type": "end",
        "winner": winner,
        "scores": s
    })

    match_started = False


@app.websocket("/")
async def referee(ws: WebSocket):
    global match_started

    await ws.accept()

    if len(players) >= 2:
        await send(ws, {"type": "full"})
        await ws.close()
        return

    pid = "P1" if len(players) == 0 else "P2"

    players[ws] = {
        "id": pid,
        "reps": 0
    }

    print(f"{pid} connected ({len(players)}/2)")

    await send(ws, {
        "type": "assigned",
        "you": pid
    })

    if len(players) == 2 and not match_started:
        match_started = True
        asyncio.create_task(run_match())

    try:

        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)

            if data.get("type") == "reps":
                players[ws]["reps"] = int(data["reps"])

                await broadcast({
                    "type": "scores",
                    "scores": scores()
                })

    except WebSocketDisconnect:
        pass

    finally:

        if ws in players:
            print(players[ws]["id"], "disconnected")
            del players[ws]


@app.get("/")
async def root():
    return {"status": "GymOggle Referee Running"}


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
    )