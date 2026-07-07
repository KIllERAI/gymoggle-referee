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
# ----------------------Text 2----------------------
# import asyncio
# import json
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# import uvicorn

# DURATION = 60

# app = FastAPI()

# players = {}           # websocket -> {"id":..., "reps":...}
# match_started = False


# async def send(ws, payload):
#     try:
#         await ws.send_text(json.dumps(payload))
#     except Exception:
#         pass


# async def broadcast(payload):
#     await asyncio.gather(
#         *[send(ws, payload) for ws in list(players.keys())],
#         return_exceptions=True,
#     )


# def scores():
#     return {p["id"]: p["reps"] for p in players.values()}


# async def run_match():
#     global match_started

#     print("Both players connected. Starting match.")

#     await broadcast({
#         "type": "start",
#         "duration": DURATION
#     })

#     await asyncio.sleep(DURATION)

#     s = scores()

#     if len(s) == 2:
#         p1 = s.get("P1", 0)
#         p2 = s.get("P2", 0)

#         if p1 == p2:
#             winner = "TIE"
#         elif p1 > p2:
#             winner = "P1"
#         else:
#             winner = "P2"
#     else:
#         winner = "TIE"

#     print("Match finished:", s)

#     await broadcast({
#         "type": "end",
#         "winner": winner,
#         "scores": s
#     })

#     match_started = False


# @app.websocket("/")
# async def referee(ws: WebSocket):
#     global match_started

#     await ws.accept()

#     if len(players) >= 2:
#         await send(ws, {"type": "full"})
#         await ws.close()
#         return

#     pid = "P1" if len(players) == 0 else "P2"

#     players[ws] = {
#         "id": pid,
#         "reps": 0
#     }

#     print(f"{pid} connected ({len(players)}/2)")

#     await send(ws, {
#         "type": "assigned",
#         "you": pid
#     })

#     if len(players) == 2 and not match_started:
#         match_started = True
#         asyncio.create_task(run_match())

#     try:

#         while True:
#             raw = await ws.receive_text()
#             data = json.loads(raw)

#             if data.get("type") == "reps":
#                 players[ws]["reps"] = int(data["reps"])

#                 await broadcast({
#                     "type": "scores",
#                     "scores": scores()
#                 })

#     except WebSocketDisconnect:
#         pass

#     finally:

#         if ws in players:
#             print(players[ws]["id"], "disconnected")
#             del players[ws]


# @app.get("/")
# async def root():
#     return {"status": "GymOggle Referee Running"}


# if __name__ == "__main__":
#     uvicorn.run(
#         "server:app",
#         host="0.0.0.0",
#         port=8000,
# #     )
# Test 3 ------------------------
# import asyncio
# import json
# import random
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# import uvicorn

# DURATION = 60
# # Code alphabet with no easily-confused characters (no O/0, I/1)
# CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
# CODE_LEN = 4

# app = FastAPI()

# # rooms: code -> {
# #   "players": { websocket: {"id": "P1"/"P2", "reps": int, "ready": bool} },
# #   "started": bool,
# #   "task": asyncio.Task | None
# # }
# rooms = {}


# def new_code():
#     while True:
#         c = "".join(random.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
#         if c not in rooms:
#             return c


# async def send(ws, payload):
#     try:
#         await ws.send_text(json.dumps(payload))
#     except Exception:
#         pass


# async def broadcast(room, payload):
#     await asyncio.gather(
#         *[send(ws, payload) for ws in list(room["players"].keys())],
#         return_exceptions=True,
#     )


# def scores(room):
#     return {p["id"]: p["reps"] for p in room["players"].values()}


# async def run_match(code):
#     room = rooms.get(code)
#     if not room:
#         return

#     room["started"] = True
#     for p in room["players"].values():
#         p["reps"] = 0
#         p["ready"] = False

#     print(f"[{code}] match starting")
#     await broadcast(room, {"type": "start", "duration": DURATION})

#     await asyncio.sleep(DURATION)

#     room = rooms.get(code)          # may have been torn down while we slept
#     if not room:
#         return

#     s = scores(room)
#     if len(s) == 2:
#         p1, p2 = s.get("P1", 0), s.get("P2", 0)
#         winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
#     else:
#         winner = "TIE"

#     print(f"[{code}] match over {s} winner={winner}")
#     await broadcast(room, {"type": "end", "winner": winner, "scores": s})
#     room["started"] = False
#     room["task"] = None


# async def try_start(code):
#     room = rooms.get(code)
#     if room and len(room["players"]) == 2 and not room["started"]:
#         room["task"] = asyncio.create_task(run_match(code))


# @app.websocket("/")
# async def referee(ws: WebSocket):
#     await ws.accept()
#     code = None                     # which room this socket belongs to

#     try:
#         while True:
#             raw = await ws.receive_text()
#             data = json.loads(raw)
#             t = data.get("type")

#             # ---- create a private room ----
#             if t == "create":
#                 if code:
#                     continue        # already in a room
#                 code = new_code()
#                 rooms[code] = {
#                     "players": {ws: {"id": "P1", "reps": 0, "ready": False}},
#                     "started": False,
#                     "task": None,
#                 }
#                 await send(ws, {"type": "created", "code": code, "you": "P1"})
#                 print(f"[{code}] created")

#             # ---- join a room by code ----
#             elif t == "join":
#                 want = (data.get("code") or "").strip().upper()
#                 room = rooms.get(want)
#                 if not room:
#                     await send(ws, {"type": "error", "reason": "no_room"})
#                 elif len(room["players"]) >= 2:
#                     await send(ws, {"type": "error", "reason": "room_full"})
#                 else:
#                     code = want
#                     room["players"][ws] = {"id": "P2", "reps": 0, "ready": False}
#                     await send(ws, {"type": "joined", "you": "P2", "code": code})
#                     await broadcast(room, {"type": "opponent_here"})
#                     print(f"[{code}] P2 joined")
#                     await try_start(code)

#             # ---- live rep updates ----
#             elif t == "reps":
#                 if code and code in rooms and ws in rooms[code]["players"]:
#                     rooms[code]["players"][ws]["reps"] = int(data.get("reps", 0))
#                     await broadcast(rooms[code],
#                                     {"type": "scores", "scores": scores(rooms[code])})

#             # ---- rematch: both must ask before it restarts ----
#             elif t == "rematch":
#                 if code and code in rooms and ws in rooms[code]["players"]:
#                     room = rooms[code]
#                     room["players"][ws]["ready"] = True
#                     both_ready = (len(room["players"]) == 2 and
#                                   all(p["ready"] for p in room["players"].values()))
#                     if both_ready:
#                         await try_start(code)
#                     else:
#                         await broadcast(room, {"type": "rematch_wait"})

#     except WebSocketDisconnect:
#         pass
#     except Exception as e:
#         print("socket error:", e)

#     finally:
#         # clean up this player's room membership
#         if code and code in rooms and ws in rooms[code]["players"]:
#             pid = rooms[code]["players"][ws]["id"]
#             del rooms[code]["players"][ws]
#             print(f"[{code}] {pid} left")

#             if rooms[code]["players"]:
#                 # someone's still here — tell them, stop any running match
#                 task = rooms[code].get("task")
#                 if task:
#                     task.cancel()
#                 rooms[code]["started"] = False
#                 for p in rooms[code]["players"].values():
#                     p["ready"] = False
#                 await broadcast(rooms[code], {"type": "opponent_left"})
#             else:
#                 # empty room — delete it
#                 task = rooms[code].get("task")
#                 if task:
#                     task.cancel()
#                 del rooms[code]
#                 print(f"[{code}] closed")


# @app.get("/")
# async def root():
#     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# if __name__ == "__main__":
#     uvicorn.run("server:app", host="0.0.0.0", port=8000)
    # TEST 4----------------------------

import asyncio
import json
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

DURATION = 35
# Code alphabet with no easily-confused characters (no O/0, I/1)
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_LEN = 4

app = FastAPI()

# rooms: code -> {
#   "players": { websocket: {"id": "P1"/"P2", "reps": int, "ready": bool} },
#   "started": bool,
#   "task": asyncio.Task | None
# }
rooms = {}


def new_code():
    while True:
        c = "".join(random.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
        if c not in rooms:
            return c


async def send(ws, payload):
    try:
        await ws.send_text(json.dumps(payload))
    except Exception:
        pass


async def broadcast(room, payload):
    await asyncio.gather(
        *[send(ws, payload) for ws in list(room["players"].keys())],
        return_exceptions=True,
    )


def scores(room):
    return {p["id"]: p["reps"] for p in room["players"].values()}


async def run_match(code):
    room = rooms.get(code)
    if not room:
        return

    room["started"] = True
    for p in room["players"].values():
        p["reps"] = 0
        p["ready"] = False

    print(f"[{code}] match starting")
    await broadcast(room, {"type": "start", "duration": DURATION})

    await asyncio.sleep(DURATION)

    room = rooms.get(code)          # may have been torn down while we slept
    if not room:
        return

    s = scores(room)
    if len(s) == 2:
        p1, p2 = s.get("P1", 0), s.get("P2", 0)
        winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
    else:
        winner = "TIE"

    print(f"[{code}] match over {s} winner={winner}")
    await broadcast(room, {"type": "end", "winner": winner, "scores": s})
    room["started"] = False
    room["task"] = None


async def try_start(code):
    room = rooms.get(code)
    if room and len(room["players"]) == 2 and not room["started"]:
        room["task"] = asyncio.create_task(run_match(code))


@app.websocket("/")
async def referee(ws: WebSocket):
    await ws.accept()
    code = None                     # which room this socket belongs to

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            t = data.get("type")

            # ---- create a private room ----
            if t == "create":
                if code:
                    continue        # already in a room
                code = new_code()
                rooms[code] = {
                    "players": {ws: {"id": "P1", "reps": 0, "ready": False}},
                    "started": False,
                    "task": None,
                }
                await send(ws, {"type": "created", "code": code, "you": "P1"})
                print(f"[{code}] created")

            # ---- join a room by code ----
            elif t == "join":
                want = (data.get("code") or "").strip().upper()
                room = rooms.get(want)
                if not room:
                    await send(ws, {"type": "error", "reason": "no_room"})
                elif len(room["players"]) >= 2:
                    await send(ws, {"type": "error", "reason": "room_full"})
                else:
                    code = want
                    room["players"][ws] = {"id": "P2", "reps": 0, "ready": False}
                    await send(ws, {"type": "joined", "you": "P2", "code": code})
                    await broadcast(room, {"type": "opponent_here"})
                    print(f"[{code}] P2 joined")
                    await try_start(code)

            # ---- live rep updates ----
            elif t == "reps":
                if code and code in rooms and ws in rooms[code]["players"]:
                    rooms[code]["players"][ws]["reps"] = int(data.get("reps", 0))
                    await broadcast(rooms[code],
                                    {"type": "scores", "scores": scores(rooms[code])})

            # ---- rematch: both must ask before it restarts ----
            elif t == "rematch":
                if code and code in rooms and ws in rooms[code]["players"]:
                    room = rooms[code]
                    room["players"][ws]["ready"] = True
                    both_ready = (len(room["players"]) == 2 and
                                  all(p["ready"] for p in room["players"].values()))
                    if both_ready:
                        await try_start(code)
                    else:
                        # tell the requester they're waiting, and tell the
                        # opponent that a rematch has been offered
                        for w in room["players"]:
                            if w is ws:
                                await send(w, {"type": "rematch_pending"})
                            else:
                                await send(w, {"type": "rematch_offer"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print("socket error:", e)

    finally:
        # clean up this player's room membership
        if code and code in rooms and ws in rooms[code]["players"]:
            pid = rooms[code]["players"][ws]["id"]
            del rooms[code]["players"][ws]
            print(f"[{code}] {pid} left")

            if rooms[code]["players"]:
                # someone's still here — tell them, stop any running match
                task = rooms[code].get("task")
                if task:
                    task.cancel()
                rooms[code]["started"] = False
                for p in rooms[code]["players"].values():
                    p["ready"] = False
                await broadcast(rooms[code], {"type": "opponent_left"})
            else:
                # empty room — delete it
                task = rooms[code].get("task")
                if task:
                    task.cancel()
                del rooms[code]
                print(f"[{code}] closed")


@app.get("/")
async def root():
    return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)