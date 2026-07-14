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

# import asyncio
# import json
# import random
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# import uvicorn

# DURATION = 35
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
#                         # tell the requester they're waiting, and tell the
#                         # opponent that a rematch has been offered
#                         for w in room["players"]:
#                             if w is ws:
#                                 await send(w, {"type": "rematch_pending"})
#                             else:
#                                 await send(w, {"type": "rematch_offer"})

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
# TEST 5----------------------------
# import asyncio
# import json
# import random
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# import uvicorn

# DURATION = 35
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
#     await broadcast(room, {"type": "start", "duration": DURATION,
#                            "exercise": room.get("exercise", "squats")})

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
#                 exercise = data.get("exercise", "squats")
#                 rooms[code] = {
#                     "players": {ws: {"id": "P1", "reps": 0, "ready": False}},
#                     "started": False,
#                     "task": None,
#                     "exercise": exercise,
#                 }
#                 await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
#                 print(f"[{code}] created ({exercise})")

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
#                     await send(ws, {"type": "joined", "you": "P2", "code": code,
#                                     "exercise": room.get("exercise", "squats")})
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
#                         # tell the requester they're waiting, and tell the
#                         # opponent that a rematch has been offered
#                         for w in room["players"]:
#                             if w is ws:
#                                 await send(w, {"type": "rematch_pending"})
#                             else:
#                                 await send(w, {"type": "rematch_offer"})

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
# Test 6----------------------------
# import asyncio
# import json
# import random
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# import uvicorn
# import os
# from supabase import create_client

# DURATION = 35
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

# # --- Supabase connection (reads the env vars you set on Render) ---
# SUPABASE_URL = os.environ.get("project_url")
# SUPABASE_KEY = os.environ.get("service_role_key")
# supabase = None
# if SUPABASE_URL and SUPABASE_KEY:
#     try:
#         supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
#         print("Supabase connected")
#     except Exception as e:
#         print("Supabase connect failed:", e)
# else:
#     print("Supabase env vars missing")

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
#     await broadcast(room, {"type": "start", "duration": DURATION,
#                            "exercise": room.get("exercise", "squats")})

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


# waiting = {}   # exercise -> list of websockets waiting for a random match


# def room_of(ws):
#     for c, room in rooms.items():
#         if ws in room["players"]:
#             return c, room
#     return None, None


# def enqueue(ws, exercise):
#     waiting.setdefault(exercise, []).append(ws)


# def dequeue(ws):
#     for lst in waiting.values():
#         if ws in lst:
#             lst.remove(ws)


# async def leave_room(ws):
#     """Remove a player from the matchmaking queue and/or their room,
#     and notify the opponent. Safe to call on explicit leave or disconnect."""
#     dequeue(ws)
#     c, room = room_of(ws)
#     if not room:
#         return
#     pid = room["players"][ws]["id"]
#     del room["players"][ws]
#     print(f"[{c}] {pid} left")
#     task = room.get("task")
#     if task:
#         task.cancel()
#     if room["players"]:
#         room["started"] = False
#         for p in room["players"].values():
#             p["ready"] = False
#         await broadcast(room, {"type": "opponent_left"})
#     else:
#         del rooms[c]
#         print(f"[{c}] closed")


# @app.websocket("/")
# async def referee(ws: WebSocket):
#     await ws.accept()

#     try:
#         while True:
#             raw = await ws.receive_text()
#             data = json.loads(raw)
#             t = data.get("type")

#             # ---- create a private room ----
#             if t == "create":
#                 if room_of(ws)[1]:
#                     continue
#                 code = new_code()
#                 exercise = data.get("exercise", "squats")
#                 rooms[code] = {
#                     "players": {ws: {"id": "P1", "reps": 0, "ready": False}},
#                     "started": False,
#                     "task": None,
#                     "exercise": exercise,
#                 }
#                 await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
#                 print(f"[{code}] created ({exercise})")

#             # ---- join a private room by code ----
#             elif t == "join":
#                 want = (data.get("code") or "").strip().upper()
#                 room = rooms.get(want)
#                 if not room:
#                     await send(ws, {"type": "error", "reason": "no_room"})
#                 elif len(room["players"]) >= 2:
#                     await send(ws, {"type": "error", "reason": "room_full"})
#                 else:
#                     room["players"][ws] = {"id": "P2", "reps": 0, "ready": False}
#                     await send(ws, {"type": "joined", "you": "P2", "code": want,
#                                     "exercise": room.get("exercise", "squats")})
#                     await broadcast(room, {"type": "opponent_here"})
#                     print(f"[{want}] P2 joined")
#                     await try_start(want)

#             # ---- quick match: pair with a waiting stranger (same exercise) ----
#             elif t == "quick":
#                 if room_of(ws)[1]:
#                     continue
#                 exercise = data.get("exercise", "squats")
#                 dequeue(ws)                       # never queue the same socket twice
#                 q = waiting.get(exercise, [])
#                 opponent = None
#                 while q:                          # find a still-waiting opponent
#                     cand = q.pop(0)
#                     if cand is not ws:
#                         opponent = cand
#                         break
#                 if opponent is not None:
#                     code = new_code()
#                     rooms[code] = {
#                         "players": {opponent: {"id": "P1", "reps": 0, "ready": False},
#                                     ws:       {"id": "P2", "reps": 0, "ready": False}},
#                         "started": False,
#                         "task": None,
#                         "exercise": exercise,
#                     }
#                     await send(opponent, {"type": "matched", "you": "P1", "exercise": exercise})
#                     await send(ws,       {"type": "matched", "you": "P2", "exercise": exercise})
#                     print(f"[{code}] quick match ({exercise})")
#                     await try_start(code)
#                 else:
#                     enqueue(ws, exercise)
#                     await send(ws, {"type": "searching", "exercise": exercise})
#                     print(f"[queue] {exercise}: {len(waiting.get(exercise, []))} waiting")

#             # ---- cancel searching ----
#             elif t == "cancel":
#                 dequeue(ws)
#                 await send(ws, {"type": "cancelled"})

#             # ---- live rep updates ----
#             elif t == "reps":
#                 c, room = room_of(ws)
#                 if room:
#                     room["players"][ws]["reps"] = int(data.get("reps", 0))
#                     await broadcast(room, {"type": "scores", "scores": scores(room)})

#             # ---- rematch: both must ask before it restarts ----
#             elif t == "rematch":
#                 c, room = room_of(ws)
#                 if room:
#                     room["players"][ws]["ready"] = True
#                     both_ready = (len(room["players"]) == 2 and
#                                   all(p["ready"] for p in room["players"].values()))
#                     if both_ready:
#                         await try_start(c)
#                     else:
#                         for w in room["players"]:
#                             if w is ws:
#                                 await send(w, {"type": "rematch_pending"})
#                             else:
#                                 await send(w, {"type": "rematch_offer"})

#             # ---- explicit leave (reliable — doesn't wait for disconnect) ----
#             elif t == "leave":
#                 await leave_room(ws)

#     except WebSocketDisconnect:
#         pass
#     except Exception as e:
#         print("socket error:", e)

#     finally:
#         await leave_room(ws)


# @app.get("/")
# async def root():
#     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# if __name__ == "__main__":
#     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# # Test 7----------------------------
# import asyncio
# import json
# import random
# import os
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# import uvicorn

# # --- Supabase connection (reads the env vars set on Render) ---
# try:
#     from supabase import create_client
#     SUPABASE_URL = os.environ.get("project_url")
#     SUPABASE_KEY = os.environ.get("service_role_key")
#     supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None
#     print("Supabase connected" if supabase else "Supabase env vars missing")
# except Exception as e:
#     supabase = None
#     print("Supabase setup failed:", e)

# DURATION = 35
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
#     await broadcast(room, {"type": "start", "duration": DURATION,
#                            "exercise": room.get("exercise", "squats")})

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


# waiting = {}   # exercise -> list of websockets waiting for a random match


# def room_of(ws):
#     for c, room in rooms.items():
#         if ws in room["players"]:
#             return c, room
#     return None, None


# def enqueue(ws, exercise):
#     waiting.setdefault(exercise, []).append(ws)


# def dequeue(ws):
#     for lst in waiting.values():
#         if ws in lst:
#             lst.remove(ws)


# async def leave_room(ws):
#     """Remove a player from the matchmaking queue and/or their room,
#     and notify the opponent. Safe to call on explicit leave or disconnect."""
#     dequeue(ws)
#     c, room = room_of(ws)
#     if not room:
#         return
#     pid = room["players"][ws]["id"]
#     del room["players"][ws]
#     print(f"[{c}] {pid} left")
#     task = room.get("task")
#     if task:
#         task.cancel()
#     if room["players"]:
#         room["started"] = False
#         for p in room["players"].values():
#             p["ready"] = False
#         await broadcast(room, {"type": "opponent_left"})
#     else:
#         del rooms[c]
#         print(f"[{c}] closed")


# @app.websocket("/")
# async def referee(ws: WebSocket):
#     await ws.accept()

#     try:
#         while True:
#             raw = await ws.receive_text()
#             data = json.loads(raw)
#             t = data.get("type")

#             # ---- create a private room ----
#             if t == "create":
#                 if room_of(ws)[1]:
#                     continue
#                 code = new_code()
#                 exercise = data.get("exercise", "squats")
#                 rooms[code] = {
#                     "players": {ws: {"id": "P1", "reps": 0, "ready": False}},
#                     "started": False,
#                     "task": None,
#                     "exercise": exercise,
#                 }
#                 await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
#                 print(f"[{code}] created ({exercise})")

#             # ---- join a private room by code ----
#             elif t == "join":
#                 want = (data.get("code") or "").strip().upper()
#                 room = rooms.get(want)
#                 if not room:
#                     await send(ws, {"type": "error", "reason": "no_room"})
#                 elif len(room["players"]) >= 2:
#                     await send(ws, {"type": "error", "reason": "room_full"})
#                 else:
#                     room["players"][ws] = {"id": "P2", "reps": 0, "ready": False}
#                     await send(ws, {"type": "joined", "you": "P2", "code": want,
#                                     "exercise": room.get("exercise", "squats")})
#                     await broadcast(room, {"type": "opponent_here"})
#                     print(f"[{want}] P2 joined")
#                     await try_start(want)

#             # ---- quick match: pair with a waiting stranger (same exercise) ----
#             elif t == "quick":
#                 if room_of(ws)[1]:
#                     continue
#                 exercise = data.get("exercise", "squats")
#                 dequeue(ws)                       # never queue the same socket twice
#                 q = waiting.get(exercise, [])
#                 opponent = None
#                 while q:                          # find a still-waiting opponent
#                     cand = q.pop(0)
#                     if cand is not ws:
#                         opponent = cand
#                         break
#                 if opponent is not None:
#                     code = new_code()
#                     rooms[code] = {
#                         "players": {opponent: {"id": "P1", "reps": 0, "ready": False},
#                                     ws:       {"id": "P2", "reps": 0, "ready": False}},
#                         "started": False,
#                         "task": None,
#                         "exercise": exercise,
#                     }
#                     await send(opponent, {"type": "matched", "you": "P1", "exercise": exercise})
#                     await send(ws,       {"type": "matched", "you": "P2", "exercise": exercise})
#                     print(f"[{code}] quick match ({exercise})")
#                     await try_start(code)
#                 else:
#                     enqueue(ws, exercise)
#                     await send(ws, {"type": "searching", "exercise": exercise})
#                     print(f"[queue] {exercise}: {len(waiting.get(exercise, []))} waiting")

#             # ---- cancel searching ----
#             elif t == "cancel":
#                 dequeue(ws)
#                 await send(ws, {"type": "cancelled"})

#             # ---- live rep updates ----
#             elif t == "reps":
#                 c, room = room_of(ws)
#                 if room:
#                     room["players"][ws]["reps"] = int(data.get("reps", 0))
#                     await broadcast(room, {"type": "scores", "scores": scores(room)})

#             # ---- rematch: both must ask before it restarts ----
#             elif t == "rematch":
#                 c, room = room_of(ws)
#                 if room:
#                     room["players"][ws]["ready"] = True
#                     both_ready = (len(room["players"]) == 2 and
#                                   all(p["ready"] for p in room["players"].values()))
#                     if both_ready:
#                         await try_start(c)
#                     else:
#                         for w in room["players"]:
#                             if w is ws:
#                                 await send(w, {"type": "rematch_pending"})
#                             else:
#                                 await send(w, {"type": "rematch_offer"})

#             # ---- explicit leave (reliable — doesn't wait for disconnect) ----
#             elif t == "leave":
#                 await leave_room(ws)

#     except WebSocketDisconnect:
#         pass
#     except Exception as e:
#         print("socket error:", e)

#     finally:
#         await leave_room(ws)


# @app.get("/")
# async def root():
#     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# @app.get("/dbtest")
# async def dbtest():
#     if not supabase:
#         return {"ok": False, "error": "no supabase client (check env vars)"}
#     try:
#         supabase.table("pings").insert({"note": "hello from render"}).execute()
#         rows = supabase.table("pings").select("*").order("created_at", desc=True).limit(3).execute()
#         return {"ok": True, "recent_pings": rows.data}
#     except Exception as e:
#         return {"ok": False, "error": str(e)}


# if __name__ == "__main__":
#     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# Test 8----------------------------
# import asyncio
# import json
# import random
# import os
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# import uvicorn

# # --- Supabase connection (reads the env vars set on Render) ---
# try:
#     from supabase import create_client
#     SUPABASE_URL = os.environ.get("project_url")
#     SUPABASE_KEY = os.environ.get("service_role_key")
#     supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None
#     print("Supabase connected" if supabase else "Supabase env vars missing")
# except Exception as e:
#     supabase = None
#     print("Supabase setup failed:", e)

# DURATION = 35
# # Code alphabet with no easily-confused characters (no O/0, I/1)
# CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
# CODE_LEN = 4

# app = FastAPI()

# # allow the browser (Netlify origin) to fetch the leaderboard over HTTP
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
# )

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


# # --- player identity (lightweight browser id + name, sent by the client) ---
# ident = {}   # websocket -> {"pid": str, "name": str}

# def remember(ws, data):
#     ident[ws] = {"pid": (data.get("pid") or "anon"), "name": (data.get("name") or "Player")}

# def pdict(ws, role):
#     i = ident.get(ws, {})
#     return {"id": role, "pid": i.get("pid", "anon"), "name": i.get("name", "Player"),
#             "reps": 0, "ready": False}


# # --- persistence: record a finished match + update player summaries ---
# def record_match_sync(exercise, p1, p2, winner):
#     if not supabase:
#         return
#     try:
#         supabase.table("matches").insert({
#             "exercise": exercise,
#             "p1_id": p1["pid"], "p1_name": p1["name"], "p1_reps": p1["reps"],
#             "p2_id": p2["pid"], "p2_name": p2["name"], "p2_reps": p2["reps"],
#             "winner": "tie" if winner == "TIE" else ("p1" if winner == "P1" else "p2"),
#         }).execute()
#         _update_player(p1, exercise, won=(winner == "P1"), drew=(winner == "TIE"))
#         _update_player(p2, exercise, won=(winner == "P2"), drew=(winner == "TIE"))
#     except Exception as e:
#         print("record_match failed:", e)

# def _update_player(p, exercise, won, drew):
#     pid = p.get("pid")
#     if not pid or pid == "anon":
#         return
#     try:
#         res = supabase.table("players").select("*").eq("id", pid).execute()
#         row = res.data[0] if res.data else {}
#         cur = (row.get("current_streak", 0) + 1) if won else 0
#         payload = {
#             "id": pid, "name": p.get("name", "Player"),
#             "wins":   row.get("wins", 0)   + (1 if won else 0),
#             "losses": row.get("losses", 0) + (0 if (won or drew) else 1),
#             "draws":  row.get("draws", 0)  + (1 if drew else 0),
#             "current_streak": cur,
#             "best_streak": max(row.get("best_streak", 0), cur),
#         }
#         if exercise in ("squats", "pushups", "situps"):
#             col = "best_" + exercise
#             payload[col] = max(row.get(col, 0), p.get("reps", 0))
#         supabase.table("players").upsert(payload).execute()
#     except Exception as e:
#         print("update_player failed:", e)


# async def run_match(code):
#     room = rooms.get(code)
#     if not room:
#         return

#     room["started"] = True
#     for p in room["players"].values():
#         p["reps"] = 0
#         p["ready"] = False

#     print(f"[{code}] match starting")
#     await broadcast(room, {"type": "start", "duration": DURATION,
#                            "exercise": room.get("exercise", "squats")})

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

#     # save the result to the database (in a thread so it never blocks the game)
#     p1p = next((p for p in room["players"].values() if p["id"] == "P1"), None)
#     p2p = next((p for p in room["players"].values() if p["id"] == "P2"), None)
#     if p1p and p2p and len(s) == 2:
#         asyncio.get_event_loop().run_in_executor(
#             None, record_match_sync, room.get("exercise", "squats"),
#             dict(p1p), dict(p2p), winner)

#     room["started"] = False
#     room["task"] = None


# async def try_start(code):
#     room = rooms.get(code)
#     if room and len(room["players"]) == 2 and not room["started"]:
#         room["task"] = asyncio.create_task(run_match(code))


# waiting = {}   # exercise -> list of websockets waiting for a random match


# def room_of(ws):
#     for c, room in rooms.items():
#         if ws in room["players"]:
#             return c, room
#     return None, None


# def enqueue(ws, exercise):
#     waiting.setdefault(exercise, []).append(ws)


# def dequeue(ws):
#     for lst in waiting.values():
#         if ws in lst:
#             lst.remove(ws)


# async def leave_room(ws):
#     """Remove a player from the matchmaking queue and/or their room,
#     and notify the opponent. Safe to call on explicit leave or disconnect."""
#     dequeue(ws)
#     ident.pop(ws, None)
#     c, room = room_of(ws)
#     if not room:
#         return
#     pid = room["players"][ws]["id"]
#     del room["players"][ws]
#     print(f"[{c}] {pid} left")
#     task = room.get("task")
#     if task:
#         task.cancel()
#     if room["players"]:
#         room["started"] = False
#         for p in room["players"].values():
#             p["ready"] = False
#         await broadcast(room, {"type": "opponent_left"})
#     else:
#         del rooms[c]
#         print(f"[{c}] closed")


# @app.websocket("/")
# async def referee(ws: WebSocket):
#     await ws.accept()

#     try:
#         while True:
#             raw = await ws.receive_text()
#             data = json.loads(raw)
#             t = data.get("type")

#             # ---- create a private room ----
#             if t == "create":
#                 if room_of(ws)[1]:
#                     continue
#                 remember(ws, data)
#                 code = new_code()
#                 exercise = data.get("exercise", "squats")
#                 rooms[code] = {
#                     "players": {ws: pdict(ws, "P1")},
#                     "started": False,
#                     "task": None,
#                     "exercise": exercise,
#                 }
#                 await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
#                 print(f"[{code}] created ({exercise})")

#             # ---- join a private room by code ----
#             elif t == "join":
#                 want = (data.get("code") or "").strip().upper()
#                 room = rooms.get(want)
#                 if not room:
#                     await send(ws, {"type": "error", "reason": "no_room"})
#                 elif len(room["players"]) >= 2:
#                     await send(ws, {"type": "error", "reason": "room_full"})
#                 else:
#                     remember(ws, data)
#                     room["players"][ws] = pdict(ws, "P2")
#                     await send(ws, {"type": "joined", "you": "P2", "code": want,
#                                     "exercise": room.get("exercise", "squats")})
#                     await broadcast(room, {"type": "opponent_here"})
#                     print(f"[{want}] P2 joined")
#                     await try_start(want)

#             # ---- quick match: pair with a waiting stranger (same exercise) ----
#             elif t == "quick":
#                 if room_of(ws)[1]:
#                     continue
#                 remember(ws, data)
#                 exercise = data.get("exercise", "squats")
#                 dequeue(ws)                       # never queue the same socket twice
#                 q = waiting.get(exercise, [])
#                 opponent = None
#                 while q:                          # find a still-waiting opponent
#                     cand = q.pop(0)
#                     if cand is not ws:
#                         opponent = cand
#                         break
#                 if opponent is not None:
#                     code = new_code()
#                     rooms[code] = {
#                         "players": {opponent: pdict(opponent, "P1"),
#                                     ws:       pdict(ws, "P2")},
#                         "started": False,
#                         "task": None,
#                         "exercise": exercise,
#                     }
#                     await send(opponent, {"type": "matched", "you": "P1", "exercise": exercise})
#                     await send(ws,       {"type": "matched", "you": "P2", "exercise": exercise})
#                     print(f"[{code}] quick match ({exercise})")
#                     await try_start(code)
#                 else:
#                     enqueue(ws, exercise)
#                     await send(ws, {"type": "searching", "exercise": exercise})
#                     print(f"[queue] {exercise}: {len(waiting.get(exercise, []))} waiting")

#             # ---- cancel searching ----
#             elif t == "cancel":
#                 dequeue(ws)
#                 await send(ws, {"type": "cancelled"})

#             # ---- live rep updates ----
#             elif t == "reps":
#                 c, room = room_of(ws)
#                 if room:
#                     room["players"][ws]["reps"] = int(data.get("reps", 0))
#                     await broadcast(room, {"type": "scores", "scores": scores(room)})

#             # ---- rematch: both must ask before it restarts ----
#             elif t == "rematch":
#                 c, room = room_of(ws)
#                 if room:
#                     room["players"][ws]["ready"] = True
#                     both_ready = (len(room["players"]) == 2 and
#                                   all(p["ready"] for p in room["players"].values()))
#                     if both_ready:
#                         await try_start(c)
#                     else:
#                         for w in room["players"]:
#                             if w is ws:
#                                 await send(w, {"type": "rematch_pending"})
#                             else:
#                                 await send(w, {"type": "rematch_offer"})

#             # ---- explicit leave (reliable — doesn't wait for disconnect) ----
#             elif t == "leave":
#                 await leave_room(ws)

#     except WebSocketDisconnect:
#         pass
#     except Exception as e:
#         print("socket error:", e)

#     finally:
#         await leave_room(ws)


# @app.get("/")
# async def root():
#     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# @app.get("/dbtest")
# async def dbtest():
#     if not supabase:
#         return {"ok": False, "error": "no supabase client (check env vars)"}
#     try:
#         supabase.table("pings").insert({"note": "hello from render"}).execute()
#         rows = supabase.table("pings").select("*").order("created_at", desc=True).limit(3).execute()
#         return {"ok": True, "recent_pings": rows.data}
#     except Exception as e:
#         return {"ok": False, "error": str(e)}


# # sync def -> FastAPI runs it in a threadpool, so DB reads don't block the game loop
# @app.get("/leaderboard")
# def leaderboard():
#     if not supabase:
#         return {"ok": False, "error": "no db"}
#     out = {"ok": True, "scores": {}, "wins": []}
#     try:
#         for ex in ("squats", "pushups", "situps"):
#             col = "best_" + ex
#             r = (supabase.table("players").select("name," + col)
#                  .gt(col, 0).order(col, desc=True).limit(10).execute())
#             out["scores"][ex] = [{"name": row["name"], "value": row[col]} for row in r.data]
#         w = (supabase.table("players").select("name,wins")
#              .gt("wins", 0).order("wins", desc=True).limit(10).execute())
#         out["wins"] = [{"name": row["name"], "value": row["wins"]} for row in w.data]
#         return out
#     except Exception as e:
#         return {"ok": False, "error": str(e)}


# if __name__ == "__main__":
#     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# Test 9----------------------------
# import asyncio
# import json
# import random
# import os
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# import uvicorn

# # --- Supabase connection (reads the env vars set on Render) ---
# try:
#     from supabase import create_client
#     SUPABASE_URL = os.environ.get("project_url")
#     SUPABASE_KEY = os.environ.get("service_role_key")
#     supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None
#     print("Supabase connected" if supabase else "Supabase env vars missing")
# except Exception as e:
#     supabase = None
#     print("Supabase setup failed:", e)

# DURATION = 35
# # Code alphabet with no easily-confused characters (no O/0, I/1)
# CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
# CODE_LEN = 4

# app = FastAPI()

# # allow the browser (Netlify origin) to fetch the leaderboard over HTTP
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
# )

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


# # --- player identity (lightweight browser id + name, sent by the client) ---
# ident = {}   # websocket -> {"pid": str, "name": str}

# def remember(ws, data):
#     ident[ws] = {"pid": (data.get("pid") or "anon"), "name": (data.get("name") or "Player")}

# def pdict(ws, role):
#     i = ident.get(ws, {})
#     return {"id": role, "pid": i.get("pid", "anon"), "name": i.get("name", "Player"),
#             "reps": 0, "ready": False}


# # --- persistence: record a finished match + update player summaries ---
# def record_match_sync(exercise, p1, p2, winner):
#     if not supabase:
#         return
#     try:
#         supabase.table("matches").insert({
#             "exercise": exercise,
#             "p1_id": p1["pid"], "p1_name": p1["name"], "p1_reps": p1["reps"],
#             "p2_id": p2["pid"], "p2_name": p2["name"], "p2_reps": p2["reps"],
#             "winner": "tie" if winner == "TIE" else ("p1" if winner == "P1" else "p2"),
#         }).execute()
#         _update_player(p1, exercise, won=(winner == "P1"), drew=(winner == "TIE"))
#         _update_player(p2, exercise, won=(winner == "P2"), drew=(winner == "TIE"))
#     except Exception as e:
#         print("record_match failed:", e)

# def _update_player(p, exercise, won, drew):
#     pid = p.get("pid")
#     if not pid or pid == "anon":
#         return
#     try:
#         res = supabase.table("players").select("*").eq("id", pid).execute()
#         row = res.data[0] if res.data else {}
#         cur = (row.get("current_streak", 0) + 1) if won else 0
#         payload = {
#             "id": pid, "name": p.get("name", "Player"),
#             "wins":   row.get("wins", 0)   + (1 if won else 0),
#             "losses": row.get("losses", 0) + (0 if (won or drew) else 1),
#             "draws":  row.get("draws", 0)  + (1 if drew else 0),
#             "current_streak": cur,
#             "best_streak": max(row.get("best_streak", 0), cur),
#         }
#         if exercise in ("squats", "pushups", "situps"):
#             col = "best_" + exercise
#             payload[col] = max(row.get(col, 0), p.get("reps", 0))
#         supabase.table("players").upsert(payload).execute()
#     except Exception as e:
#         print("update_player failed:", e)


# async def run_match(code):
#     room = rooms.get(code)
#     if not room:
#         return

#     room["started"] = True
#     for p in room["players"].values():
#         p["reps"] = 0
#         p["ready"] = False

#     print(f"[{code}] match starting")
#     await broadcast(room, {"type": "start", "duration": DURATION,
#                            "exercise": room.get("exercise", "squats")})

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

#     # save the result to the database (in a thread so it never blocks the game)
#     p1p = next((p for p in room["players"].values() if p["id"] == "P1"), None)
#     p2p = next((p for p in room["players"].values() if p["id"] == "P2"), None)
#     if p1p and p2p and len(s) == 2:
#         asyncio.get_event_loop().run_in_executor(
#             None, record_match_sync, room.get("exercise", "squats"),
#             dict(p1p), dict(p2p), winner)

#     room["started"] = False
#     room["task"] = None


# async def try_start(code):
#     room = rooms.get(code)
#     if room and len(room["players"]) == 2 and not room["started"]:
#         room["task"] = asyncio.create_task(run_match(code))


# LOBBY_SECS = 15   # pre-match ready-up + trash-talk window

# async def start_lobby(code):
#     room = rooms.get(code)
#     if not room or room.get("started") or len(room["players"]) != 2:
#         return
#     room["in_lobby"] = True
#     for p in room["players"].values():
#         p["lobby_ready"] = False
#     names = {p["id"]: p["name"] for p in room["players"].values()}
#     await broadcast(room, {"type": "lobby", "duration": LOBBY_SECS, "names": names})
#     room["lobby_task"] = asyncio.create_task(lobby_timer(code))

# async def lobby_timer(code):
#     try:
#         await asyncio.sleep(LOBBY_SECS)
#     except asyncio.CancelledError:
#         return
#     room = rooms.get(code)
#     if room and room.get("in_lobby"):
#         await begin_match(code)

# async def begin_match(code):
#     room = rooms.get(code)
#     if not room or room.get("started"):
#         return
#     room["in_lobby"] = False
#     t = room.get("lobby_task")
#     if t:
#         t.cancel()
#     await try_start(code)


# waiting = {}   # exercise -> list of websockets waiting for a random match


# def room_of(ws):
#     for c, room in rooms.items():
#         if ws in room["players"]:
#             return c, room
#     return None, None


# def enqueue(ws, exercise):
#     waiting.setdefault(exercise, []).append(ws)


# def dequeue(ws):
#     for lst in waiting.values():
#         if ws in lst:
#             lst.remove(ws)


# async def leave_room(ws):
#     """Remove a player from the matchmaking queue and/or their room,
#     and notify the opponent. Safe to call on explicit leave or disconnect."""
#     dequeue(ws)
#     ident.pop(ws, None)
#     c, room = room_of(ws)
#     if not room:
#         return
#     pid = room["players"][ws]["id"]
#     del room["players"][ws]
#     print(f"[{c}] {pid} left")
#     task = room.get("task")
#     if task:
#         task.cancel()
#     lt = room.get("lobby_task")
#     if lt:
#         lt.cancel()
#     room["in_lobby"] = False
#     if room["players"]:
#         room["started"] = False
#         for p in room["players"].values():
#             p["ready"] = False
#         await broadcast(room, {"type": "opponent_left"})
#     else:
#         del rooms[c]
#         print(f"[{c}] closed")


# @app.websocket("/")
# async def referee(ws: WebSocket):
#     await ws.accept()

#     try:
#         while True:
#             raw = await ws.receive_text()
#             data = json.loads(raw)
#             t = data.get("type")

#             # ---- create a private room ----
#             if t == "create":
#                 if room_of(ws)[1]:
#                     continue
#                 remember(ws, data)
#                 code = new_code()
#                 exercise = data.get("exercise", "squats")
#                 rooms[code] = {
#                     "players": {ws: pdict(ws, "P1")},
#                     "started": False,
#                     "task": None,
#                     "exercise": exercise,
#                 }
#                 await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
#                 print(f"[{code}] created ({exercise})")

#             # ---- join a private room by code ----
#             elif t == "join":
#                 want = (data.get("code") or "").strip().upper()
#                 room = rooms.get(want)
#                 if not room:
#                     await send(ws, {"type": "error", "reason": "no_room"})
#                 elif len(room["players"]) >= 2:
#                     await send(ws, {"type": "error", "reason": "room_full"})
#                 else:
#                     remember(ws, data)
#                     room["players"][ws] = pdict(ws, "P2")
#                     await send(ws, {"type": "joined", "you": "P2", "code": want,
#                                     "exercise": room.get("exercise", "squats")})
#                     await broadcast(room, {"type": "opponent_here"})
#                     print(f"[{want}] P2 joined")
#                     await start_lobby(want)

#             # ---- quick match: pair with a waiting stranger (same exercise) ----
#             elif t == "quick":
#                 if room_of(ws)[1]:
#                     continue
#                 remember(ws, data)
#                 exercise = data.get("exercise", "squats")
#                 dequeue(ws)                       # never queue the same socket twice
#                 q = waiting.get(exercise, [])
#                 opponent = None
#                 while q:                          # find a still-waiting opponent
#                     cand = q.pop(0)
#                     if cand is not ws:
#                         opponent = cand
#                         break
#                 if opponent is not None:
#                     code = new_code()
#                     rooms[code] = {
#                         "players": {opponent: pdict(opponent, "P1"),
#                                     ws:       pdict(ws, "P2")},
#                         "started": False,
#                         "task": None,
#                         "exercise": exercise,
#                     }
#                     await send(opponent, {"type": "matched", "you": "P1", "exercise": exercise})
#                     await send(ws,       {"type": "matched", "you": "P2", "exercise": exercise})
#                     print(f"[{code}] quick match ({exercise})")
#                     await start_lobby(code)
#                 else:
#                     enqueue(ws, exercise)
#                     await send(ws, {"type": "searching", "exercise": exercise})
#                     print(f"[queue] {exercise}: {len(waiting.get(exercise, []))} waiting")

#             # ---- cancel searching ----
#             elif t == "cancel":
#                 dequeue(ws)
#                 await send(ws, {"type": "cancelled"})

#             # ---- live rep updates ----
#             elif t == "reps":
#                 c, room = room_of(ws)
#                 if room:
#                     room["players"][ws]["reps"] = int(data.get("reps", 0))
#                     await broadcast(room, {"type": "scores", "scores": scores(room)})

#             # ---- rematch: both must ask before it restarts ----
#             elif t == "rematch":
#                 c, room = room_of(ws)
#                 if room:
#                     room["players"][ws]["ready"] = True
#                     both_ready = (len(room["players"]) == 2 and
#                                   all(p["ready"] for p in room["players"].values()))
#                     if both_ready:
#                         await try_start(c)
#                     else:
#                         for w in room["players"]:
#                             if w is ws:
#                                 await send(w, {"type": "rematch_pending"})
#                             else:
#                                 await send(w, {"type": "rematch_offer"})

#             # ---- lobby: player hit READY (skip the timer if both are ready) ----
#             elif t == "ready":
#                 c, room = room_of(ws)
#                 if room and room.get("in_lobby"):
#                     room["players"][ws]["lobby_ready"] = True
#                     await broadcast(room, {"type": "ready_state",
#                                            "who": room["players"][ws]["id"]})
#                     if (len(room["players"]) == 2 and
#                             all(p.get("lobby_ready") for p in room["players"].values())):
#                         await begin_match(c)

#             # ---- lobby chat: relay a message to both players ----
#             elif t == "chat":
#                 c, room = room_of(ws)
#                 if room:
#                     txt = str(data.get("text", ""))[:200].strip()
#                     if txt:
#                         p = room["players"][ws]
#                         await broadcast(room, {"type": "chat", "from": p["name"],
#                                                "who": p["id"], "text": txt})

#             # ---- explicit leave (reliable — doesn't wait for disconnect) ----
#             elif t == "leave":
#                 await leave_room(ws)

#     except WebSocketDisconnect:
#         pass
#     except Exception as e:
#         print("socket error:", e)

#     finally:
#         await leave_room(ws)


# @app.get("/")
# async def root():
#     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# @app.get("/dbtest")
# async def dbtest():
#     if not supabase:
#         return {"ok": False, "error": "no supabase client (check env vars)"}
#     try:
#         supabase.table("pings").insert({"note": "hello from render"}).execute()
#         rows = supabase.table("pings").select("*").order("created_at", desc=True).limit(3).execute()
#         return {"ok": True, "recent_pings": rows.data}
#     except Exception as e:
#         return {"ok": False, "error": str(e)}


# # sync def -> FastAPI runs it in a threadpool, so DB reads don't block the game loop
# @app.get("/leaderboard")
# def leaderboard():
#     if not supabase:
#         return {"ok": False, "error": "no db"}
#     out = {"ok": True, "scores": {}, "wins": []}
#     try:
#         for ex in ("squats", "pushups", "situps"):
#             col = "best_" + ex
#             r = (supabase.table("players").select("name," + col)
#                  .gt(col, 0).order(col, desc=True).limit(10).execute())
#             out["scores"][ex] = [{"name": row["name"], "value": row[col]} for row in r.data]
#         w = (supabase.table("players").select("name,wins")
#              .gt("wins", 0).order("wins", desc=True).limit(10).execute())
#         out["wins"] = [{"name": row["name"], "value": row["wins"]} for row in w.data]
#         return out
#     except Exception as e:
#         return {"ok": False, "error": str(e)}


# # ============================ DAILY TASKS ============================
# # Three tasks a day, the SAME for everyone in the world, derived from the date.

# import datetime, hashlib

# DAILY_POOL = [
#     ("squats",   [15, 20, 25, 30]),
#     ("pushups",  [8, 10, 12, 15]),
#     ("jacks",    [20, 25, 30, 40]),
#     ("situps",   [10, 15, 20]),
# ]
# COINS_PER_TASK = 10
# COINS_ALL_DONE = 25          # bonus for clearing all three


# def todays_tasks(day: str):
#     """Deterministic from the date -> everyone on earth gets the same 3 tasks."""
#     seed = int(hashlib.sha256(day.encode()).hexdigest(), 16)
#     picks, pool = [], list(DAILY_POOL)
#     for i in range(3):
#         ex, targets = pool.pop(seed % len(pool))
#         seed //= max(1, len(pool) + 1)
#         target = targets[seed % len(targets)]
#         seed //= len(targets)
#         picks.append({"idx": i, "exercise": ex, "target": target,
#                       "coins": COINS_PER_TASK})
#     return picks


# @app.get("/daily")
# def daily(pid: str = ""):
#     day = datetime.date.today().isoformat()
#     tasks = todays_tasks(day)
#     out = {"ok": True, "day": day, "tasks": tasks, "done": [],
#            "coins": 0, "streak": 0, "all_done": False}
#     if not supabase or not pid:
#         return out
#     try:
#         d = supabase.table("daily_done").select("task_idx") \
#             .eq("pid", pid).eq("day", day).execute()
#         out["done"] = sorted({r["task_idx"] for r in d.data})
#         p = supabase.table("players").select("coins,daily_streak").eq("id", pid).execute()
#         if p.data:
#             out["coins"] = p.data[0].get("coins") or 0
#             out["streak"] = p.data[0].get("daily_streak") or 0
#         out["all_done"] = len(out["done"]) >= 3
#         return out
#     except Exception as e:
#         out["error"] = str(e)
#         return out


# @app.post("/daily/complete")
# def daily_complete(payload: dict):
#     """Body: {pid, name, task_idx, exercise, reps}"""
#     if not supabase:
#         return {"ok": False, "error": "no db"}
#     pid = (payload.get("pid") or "").strip()
#     if not pid:
#         return {"ok": False, "error": "no pid"}
#     day = datetime.date.today().isoformat()
#     tasks = todays_tasks(day)
#     try:
#         idx = int(payload.get("task_idx", -1))
#         task = next((t for t in tasks if t["idx"] == idx), None)
#         if not task:
#             return {"ok": False, "error": "bad task"}
#         reps = int(payload.get("reps", 0))
#         # server-side sanity: must actually hit the target
#         if reps < task["target"]:
#             return {"ok": False, "error": "target not met"}

#         # already done today? (unique constraint also protects us)
#         prev = supabase.table("daily_done").select("task_idx") \
#             .eq("pid", pid).eq("day", day).execute()
#         done_idx = {r["task_idx"] for r in prev.data}
#         if idx in done_idx:
#             return {"ok": True, "already": True}

#         supabase.table("daily_done").insert({
#             "pid": pid, "day": day, "task_idx": idx,
#             "exercise": task["exercise"], "reps": reps}).execute()
#         done_idx.add(idx)

#         # ---- coins + streak ----
#         row = supabase.table("players").select("*").eq("id", pid).execute()
#         p = row.data[0] if row.data else {}
#         coins = (p.get("coins") or 0) + COINS_PER_TASK
#         streak = p.get("daily_streak") or 0
#         best = p.get("best_daily_streak") or 0
#         last = p.get("last_daily")
#         all_done = len(done_idx) >= 3

#         if all_done:
#             coins += COINS_ALL_DONE
#             yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
#             if last == day:
#                 pass                      # streak already counted today
#             elif last == yesterday:
#                 streak += 1
#             else:
#                 streak = 1
#             best = max(best, streak)

#         upd = {"id": pid, "name": payload.get("name") or p.get("name") or "Player",
#                "coins": coins, "daily_streak": streak, "best_daily_streak": best}
#         if all_done:
#             upd["last_daily"] = day
#         supabase.table("players").upsert(upd).execute()

#         return {"ok": True, "coins": coins, "streak": streak,
#                 "all_done": all_done, "done": sorted(done_idx),
#                 "earned": COINS_PER_TASK + (COINS_ALL_DONE if all_done else 0)}
#     except Exception as e:
#         return {"ok": False, "error": str(e)}


# if __name__ == "__main__":
#     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# Test 10----------------------------
import asyncio
import json
import random
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

# --- Supabase connection (reads the env vars set on Render) ---
try:
    from supabase import create_client
    SUPABASE_URL = os.environ.get("project_url")
    SUPABASE_KEY = os.environ.get("service_role_key")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None
    print("Supabase connected" if supabase else "Supabase env vars missing")
except Exception as e:
    supabase = None
    print("Supabase setup failed:", e)

DURATION = 35
PLANK_MAX = 300     # safety cap for Plank Chicken (5 min) so a match can't run forever
# Code alphabet with no easily-confused characters (no O/0, I/1)
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_LEN = 4

app = FastAPI()

# allow the browser (Netlify origin) to fetch the leaderboard over HTTP
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

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


# --- player identity (lightweight browser id + name, sent by the client) ---
ident = {}   # websocket -> {"pid": str, "name": str}

def remember(ws, data):
    ident[ws] = {"pid": (data.get("pid") or "anon"), "name": (data.get("name") or "Player")}

def pdict(ws, role):
    i = ident.get(ws, {})
    return {"id": role, "pid": i.get("pid", "anon"), "name": i.get("name", "Player"),
            "reps": 0, "ready": False}


# --- persistence: record a finished match + update player summaries ---
def record_match_sync(exercise, p1, p2, winner):
    if not supabase:
        return
    try:
        supabase.table("matches").insert({
            "exercise": exercise,
            "p1_id": p1["pid"], "p1_name": p1["name"], "p1_reps": p1["reps"],
            "p2_id": p2["pid"], "p2_name": p2["name"], "p2_reps": p2["reps"],
            "winner": "tie" if winner == "TIE" else ("p1" if winner == "P1" else "p2"),
        }).execute()
        _update_player(p1, exercise, won=(winner == "P1"), drew=(winner == "TIE"))
        _update_player(p2, exercise, won=(winner == "P2"), drew=(winner == "TIE"))
    except Exception as e:
        print("record_match failed:", e)

def _update_player(p, exercise, won, drew):
    pid = p.get("pid")
    if not pid or pid == "anon":
        return
    try:
        res = supabase.table("players").select("*").eq("id", pid).execute()
        row = res.data[0] if res.data else {}
        cur = (row.get("current_streak", 0) + 1) if won else 0
        payload = {
            "id": pid, "name": p.get("name", "Player"),
            "wins":   row.get("wins", 0)   + (1 if won else 0),
            "losses": row.get("losses", 0) + (0 if (won or drew) else 1),
            "draws":  row.get("draws", 0)  + (1 if drew else 0),
            "current_streak": cur,
            "best_streak": max(row.get("best_streak", 0), cur),
        }
        if exercise in ("squats", "pushups", "situps", "jacks", "plank"):
            col = "best_" + exercise
            payload[col] = max(row.get(col, 0), p.get("reps", 0))
        supabase.table("players").upsert(payload).execute()
    except Exception as e:
        print("update_player failed:", e)


async def run_match(code):
    room = rooms.get(code)
    if not room:
        return

    room["started"] = True
    for p in room["players"].values():
        p["reps"] = 0
        p["ready"] = False

    ex = room.get("exercise", "squats")
    is_plank = (ex == "plank")
    for p in room["players"].values():
        p["broke"] = False

    print(f"[{code}] match starting ({ex})")
    await broadcast(room, {"type": "start",
                           "duration": (PLANK_MAX if is_plank else DURATION),
                           "mode": ("hold" if is_plank else "reps"),
                           "exercise": ex})

    if is_plank:
        # PLANK CHICKEN: no countdown. Hold until someone's form breaks.
        # The first to break loses. A safety cap stops an eternal match.
        waited = 0.0
        while waited < PLANK_MAX:
            await asyncio.sleep(0.2)
            waited += 0.2
            room = rooms.get(code)
            if not room or len(room["players"]) < 2:
                return
            broken = [p for p in room["players"].values() if p.get("broke")]
            if broken:
                break
    else:
        await asyncio.sleep(DURATION)

    room = rooms.get(code)          # may have been torn down while we slept
    if not room:
        return

    s = scores(room)
    if is_plank:
        broken = [p for p in room["players"].values() if p.get("broke")]
        if len(broken) == 1:
            loser = broken[0]["id"]
            winner = "P2" if loser == "P1" else "P1"
        elif len(broken) >= 2:
            winner = "TIE"                       # both cracked in the same instant
        else:
            # hit the safety cap with both still holding -> longest hold wins
            p1, p2 = s.get("P1", 0), s.get("P2", 0)
            winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
    elif len(s) == 2:
        p1, p2 = s.get("P1", 0), s.get("P2", 0)
        winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
    else:
        winner = "TIE"

    print(f"[{code}] match over {s} winner={winner}")
    await broadcast(room, {"type": "end", "winner": winner, "scores": s})

    # save the result to the database (in a thread so it never blocks the game)
    p1p = next((p for p in room["players"].values() if p["id"] == "P1"), None)
    p2p = next((p for p in room["players"].values() if p["id"] == "P2"), None)
    if p1p and p2p and len(s) == 2:
        asyncio.get_event_loop().run_in_executor(
            None, record_match_sync, room.get("exercise", "squats"),
            dict(p1p), dict(p2p), winner)

    room["started"] = False
    room["task"] = None


async def try_start(code):
    room = rooms.get(code)
    if room and len(room["players"]) == 2 and not room["started"]:
        room["task"] = asyncio.create_task(run_match(code))


LOBBY_SECS = 15   # pre-match ready-up + trash-talk window

async def start_lobby(code):
    room = rooms.get(code)
    if not room or room.get("started") or len(room["players"]) != 2:
        return
    room["in_lobby"] = True
    for p in room["players"].values():
        p["lobby_ready"] = False
    names = {p["id"]: p["name"] for p in room["players"].values()}
    await broadcast(room, {"type": "lobby", "duration": LOBBY_SECS, "names": names})
    room["lobby_task"] = asyncio.create_task(lobby_timer(code))

async def lobby_timer(code):
    try:
        await asyncio.sleep(LOBBY_SECS)
    except asyncio.CancelledError:
        return
    room = rooms.get(code)
    if room and room.get("in_lobby"):
        await begin_match(code)

async def begin_match(code):
    room = rooms.get(code)
    if not room or room.get("started"):
        return
    room["in_lobby"] = False
    t = room.get("lobby_task")
    if t:
        t.cancel()
    await try_start(code)


waiting = {}   # exercise -> list of websockets waiting for a random match


def room_of(ws):
    for c, room in rooms.items():
        if ws in room["players"]:
            return c, room
    return None, None


def enqueue(ws, exercise):
    waiting.setdefault(exercise, []).append(ws)


def dequeue(ws):
    for lst in waiting.values():
        if ws in lst:
            lst.remove(ws)


async def leave_room(ws):
    """Remove a player from the matchmaking queue and/or their room,
    and notify the opponent. Safe to call on explicit leave or disconnect."""
    dequeue(ws)
    ident.pop(ws, None)
    c, room = room_of(ws)
    if not room:
        return
    pid = room["players"][ws]["id"]
    del room["players"][ws]
    print(f"[{c}] {pid} left")
    task = room.get("task")
    if task:
        task.cancel()
    lt = room.get("lobby_task")
    if lt:
        lt.cancel()
    room["in_lobby"] = False
    if room["players"]:
        room["started"] = False
        for p in room["players"].values():
            p["ready"] = False
        await broadcast(room, {"type": "opponent_left"})
    else:
        del rooms[c]
        print(f"[{c}] closed")


@app.websocket("/")
async def referee(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            t = data.get("type")

            # ---- create a private room ----
            if t == "create":
                if room_of(ws)[1]:
                    continue
                remember(ws, data)
                code = new_code()
                exercise = data.get("exercise", "squats")
                rooms[code] = {
                    "players": {ws: pdict(ws, "P1")},
                    "started": False,
                    "task": None,
                    "exercise": exercise,
                }
                await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
                print(f"[{code}] created ({exercise})")

            # ---- join a private room by code ----
            elif t == "join":
                want = (data.get("code") or "").strip().upper()
                room = rooms.get(want)
                if not room:
                    await send(ws, {"type": "error", "reason": "no_room"})
                elif len(room["players"]) >= 2:
                    await send(ws, {"type": "error", "reason": "room_full"})
                else:
                    remember(ws, data)
                    room["players"][ws] = pdict(ws, "P2")
                    await send(ws, {"type": "joined", "you": "P2", "code": want,
                                    "exercise": room.get("exercise", "squats")})
                    await broadcast(room, {"type": "opponent_here"})
                    print(f"[{want}] P2 joined")
                    await start_lobby(want)

            # ---- quick match: pair with a waiting stranger (same exercise) ----
            elif t == "quick":
                if room_of(ws)[1]:
                    continue
                remember(ws, data)
                exercise = data.get("exercise", "squats")
                dequeue(ws)                       # never queue the same socket twice
                q = waiting.get(exercise, [])
                opponent = None
                while q:                          # find a still-waiting opponent
                    cand = q.pop(0)
                    if cand is not ws:
                        opponent = cand
                        break
                if opponent is not None:
                    code = new_code()
                    rooms[code] = {
                        "players": {opponent: pdict(opponent, "P1"),
                                    ws:       pdict(ws, "P2")},
                        "started": False,
                        "task": None,
                        "exercise": exercise,
                    }
                    await send(opponent, {"type": "matched", "you": "P1", "exercise": exercise})
                    await send(ws,       {"type": "matched", "you": "P2", "exercise": exercise})
                    print(f"[{code}] quick match ({exercise})")
                    await start_lobby(code)
                else:
                    enqueue(ws, exercise)
                    await send(ws, {"type": "searching", "exercise": exercise})
                    print(f"[queue] {exercise}: {len(waiting.get(exercise, []))} waiting")

            # ---- cancel searching ----
            elif t == "cancel":
                dequeue(ws)
                await send(ws, {"type": "cancelled"})

            # ---- live rep updates ----
            elif t == "reps":
                c, room = room_of(ws)
                if room:
                    room["players"][ws]["reps"] = int(data.get("reps", 0))
                    await broadcast(room, {"type": "scores", "scores": scores(room)})

            # ---- rematch: both must ask before it restarts ----
            elif t == "rematch":
                c, room = room_of(ws)
                if room:
                    room["players"][ws]["ready"] = True
                    both_ready = (len(room["players"]) == 2 and
                                  all(p["ready"] for p in room["players"].values()))
                    if both_ready:
                        await try_start(c)
                    else:
                        for w in room["players"]:
                            if w is ws:
                                await send(w, {"type": "rematch_pending"})
                            else:
                                await send(w, {"type": "rematch_offer"})

            # ---- plank chicken: this player's form broke ----
            elif t == "broke":
                c, room = room_of(ws)
                if room and room.get("started"):
                    room["players"][ws]["broke"] = True
                    print(f"[{c}] {room['players'][ws]['id']} broke form")

            # ---- lobby: player hit READY (skip the timer if both are ready) ----
            elif t == "ready":
                c, room = room_of(ws)
                if room and room.get("in_lobby"):
                    room["players"][ws]["lobby_ready"] = True
                    await broadcast(room, {"type": "ready_state",
                                           "who": room["players"][ws]["id"]})
                    if (len(room["players"]) == 2 and
                            all(p.get("lobby_ready") for p in room["players"].values())):
                        await begin_match(c)

            # ---- lobby chat: relay a message to both players ----
            elif t == "chat":
                c, room = room_of(ws)
                if room:
                    txt = str(data.get("text", ""))[:200].strip()
                    if txt:
                        p = room["players"][ws]
                        await broadcast(room, {"type": "chat", "from": p["name"],
                                               "who": p["id"], "text": txt})

            # ---- explicit leave (reliable — doesn't wait for disconnect) ----
            elif t == "leave":
                await leave_room(ws)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print("socket error:", e)

    finally:
        await leave_room(ws)


@app.get("/")
async def root():
    return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


@app.get("/dbtest")
async def dbtest():
    if not supabase:
        return {"ok": False, "error": "no supabase client (check env vars)"}
    try:
        supabase.table("pings").insert({"note": "hello from render"}).execute()
        rows = supabase.table("pings").select("*").order("created_at", desc=True).limit(3).execute()
        return {"ok": True, "recent_pings": rows.data}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# sync def -> FastAPI runs it in a threadpool, so DB reads don't block the game loop
@app.get("/leaderboard")
def leaderboard():
    if not supabase:
        return {"ok": False, "error": "no db"}
    out = {"ok": True, "scores": {}, "wins": []}
    try:
        for ex in ("squats", "pushups", "situps"):
            col = "best_" + ex
            r = (supabase.table("players").select("name," + col)
                 .gt(col, 0).order(col, desc=True).limit(10).execute())
            out["scores"][ex] = [{"name": row["name"], "value": row[col]} for row in r.data]
        w = (supabase.table("players").select("name,wins")
             .gt("wins", 0).order("wins", desc=True).limit(10).execute())
        out["wins"] = [{"name": row["name"], "value": row["wins"]} for row in w.data]
        return out
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ============================ DAILY TASKS ============================
# Three tasks a day, the SAME for everyone in the world, derived from the date.

import datetime, hashlib

DAILY_POOL = [
    ("squats",   [15, 20, 25, 30]),
    ("pushups",  [8, 10, 12, 15]),
    ("jacks",    [20, 25, 30, 40]),
    ("situps",   [10, 15, 20]),
    ("plank",    [30, 45, 60]),        # seconds held, not reps
]
COINS_PER_TASK = 10
COINS_ALL_DONE = 25          # bonus for clearing all three


def todays_tasks(day: str):
    """Deterministic from the date -> everyone on earth gets the same 3 tasks."""
    seed = int(hashlib.sha256(day.encode()).hexdigest(), 16)
    picks, pool = [], list(DAILY_POOL)
    for i in range(3):
        ex, targets = pool.pop(seed % len(pool))
        seed //= max(1, len(pool) + 1)
        target = targets[seed % len(targets)]
        seed //= len(targets)
        picks.append({"idx": i, "exercise": ex, "target": target,
                      "coins": COINS_PER_TASK})
    return picks


@app.get("/daily")
def daily(pid: str = ""):
    day = datetime.date.today().isoformat()
    tasks = todays_tasks(day)
    out = {"ok": True, "day": day, "tasks": tasks, "done": [],
           "coins": 0, "streak": 0, "all_done": False}
    if not supabase or not pid:
        return out
    try:
        d = supabase.table("daily_done").select("task_idx") \
            .eq("pid", pid).eq("day", day).execute()
        out["done"] = sorted({r["task_idx"] for r in d.data})
        p = supabase.table("players").select("coins,daily_streak").eq("id", pid).execute()
        if p.data:
            out["coins"] = p.data[0].get("coins") or 0
            out["streak"] = p.data[0].get("daily_streak") or 0
        out["all_done"] = len(out["done"]) >= 3
        return out
    except Exception as e:
        out["error"] = str(e)
        return out


@app.post("/daily/complete")
def daily_complete(payload: dict):
    """Body: {pid, name, task_idx, exercise, reps}"""
    if not supabase:
        return {"ok": False, "error": "no db"}
    pid = (payload.get("pid") or "").strip()
    if not pid:
        return {"ok": False, "error": "no pid"}
    day = datetime.date.today().isoformat()
    tasks = todays_tasks(day)
    try:
        idx = int(payload.get("task_idx", -1))
        task = next((t for t in tasks if t["idx"] == idx), None)
        if not task:
            return {"ok": False, "error": "bad task"}
        reps = int(payload.get("reps", 0))
        # server-side sanity: must actually hit the target
        if reps < task["target"]:
            return {"ok": False, "error": "target not met"}

        # already done today? (unique constraint also protects us)
        prev = supabase.table("daily_done").select("task_idx") \
            .eq("pid", pid).eq("day", day).execute()
        done_idx = {r["task_idx"] for r in prev.data}
        if idx in done_idx:
            return {"ok": True, "already": True}

        supabase.table("daily_done").insert({
            "pid": pid, "day": day, "task_idx": idx,
            "exercise": task["exercise"], "reps": reps}).execute()
        done_idx.add(idx)

        # ---- coins + streak ----
        row = supabase.table("players").select("*").eq("id", pid).execute()
        p = row.data[0] if row.data else {}
        coins = (p.get("coins") or 0) + COINS_PER_TASK
        streak = p.get("daily_streak") or 0
        best = p.get("best_daily_streak") or 0
        last = p.get("last_daily")
        all_done = len(done_idx) >= 3

        if all_done:
            coins += COINS_ALL_DONE
            yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
            if last == day:
                pass                      # streak already counted today
            elif last == yesterday:
                streak += 1
            else:
                streak = 1
            best = max(best, streak)

        upd = {"id": pid, "name": payload.get("name") or p.get("name") or "Player",
               "coins": coins, "daily_streak": streak, "best_daily_streak": best}
        if all_done:
            upd["last_daily"] = day
        supabase.table("players").upsert(upd).execute()

        return {"ok": True, "coins": coins, "streak": streak,
                "all_done": all_done, "done": sorted(done_idx),
                "earned": COINS_PER_TASK + (COINS_ALL_DONE if all_done else 0)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)