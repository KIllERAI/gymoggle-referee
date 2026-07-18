# # # # import asyncio
# # # # import json
# # # # import websockets

# # # # DURATION = 20          # match length in seconds  (set to 10 for quick testing)

# # # # players = {}           # websocket -> {"id": "P1"/"P2", "reps": 0}
# # # # match_started = False


# # # # async def send(ws, payload):
# # # #     try:
# # # #         await ws.send(json.dumps(payload))
# # # #     except Exception:
# # # #         pass


# # # # async def broadcast(payload):
# # # #     await asyncio.gather(*[send(ws, payload) for ws in players])


# # # # def scores_dict():
# # # #     return {p["id"]: p["reps"] for p in players.values()}


# # # # async def run_match():
# # # #     print("Both players in — match starting!")
# # # #     await broadcast({"type": "start", "duration": DURATION})
# # # #     await asyncio.sleep(DURATION)

# # # #     s = scores_dict()
# # # #     if len(s) == 2:
# # # #         p1, p2 = s["P1"], s["P2"]
# # # #         winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
# # # #     else:
# # # #         winner = "TIE"
# # # #     print(f"Match over. Scores: {s}  Winner: {winner}")
# # # #     await broadcast({"type": "end", "winner": winner, "scores": s})


# # # # async def handler(websocket, *args):        # *args keeps it compatible across websockets versions
# # # #     global match_started
# # # #     if len(players) >= 2:
# # # #         await send(websocket, {"type": "full"})   # already 2 players, reject a third
# # # #         return

# # # #     pid = "P1" if len(players) == 0 else "P2"
# # # #     players[websocket] = {"id": pid, "reps": 0}
# # # #     print(f"{pid} connected ({len(players)}/2)")
# # # #     await send(websocket, {"type": "assigned", "you": pid})

# # # #     try:
# # # #         # start the match once both are in
# # # #         if len(players) == 2 and not match_started:
# # # #             match_started = True
# # # #             asyncio.create_task(run_match())

# # # #         async for raw in websocket:
# # # #             data = json.loads(raw)
# # # #             if data.get("type") == "reps":
# # # #                 players[websocket]["reps"] = int(data["reps"])
# # # #                 await broadcast({"type": "scores", "scores": scores_dict()})
# # # #     finally:
# # # #         pid = players.get(websocket, {}).get("id", "?")
# # # #         players.pop(websocket, None)
# # # #         print(f"{pid} disconnected")


# # # # async def main():
# # # #     async with websockets.serve(handler, "0.0.0.0", 8765):
# # # #         print("Referee running on port 8765. Waiting for 2 players…")
# # # #         await asyncio.Future()    # run forever


# # # # asyncio.run(main())
# # # # ----------------------Text 2----------------------
# # # # import asyncio
# # # # import json
# # # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # # # import uvicorn

# # # # DURATION = 60

# # # # app = FastAPI()

# # # # players = {}           # websocket -> {"id":..., "reps":...}
# # # # match_started = False


# # # # async def send(ws, payload):
# # # #     try:
# # # #         await ws.send_text(json.dumps(payload))
# # # #     except Exception:
# # # #         pass


# # # # async def broadcast(payload):
# # # #     await asyncio.gather(
# # # #         *[send(ws, payload) for ws in list(players.keys())],
# # # #         return_exceptions=True,
# # # #     )


# # # # def scores():
# # # #     return {p["id"]: p["reps"] for p in players.values()}


# # # # async def run_match():
# # # #     global match_started

# # # #     print("Both players connected. Starting match.")

# # # #     await broadcast({
# # # #         "type": "start",
# # # #         "duration": DURATION
# # # #     })

# # # #     await asyncio.sleep(DURATION)

# # # #     s = scores()

# # # #     if len(s) == 2:
# # # #         p1 = s.get("P1", 0)
# # # #         p2 = s.get("P2", 0)

# # # #         if p1 == p2:
# # # #             winner = "TIE"
# # # #         elif p1 > p2:
# # # #             winner = "P1"
# # # #         else:
# # # #             winner = "P2"
# # # #     else:
# # # #         winner = "TIE"

# # # #     print("Match finished:", s)

# # # #     await broadcast({
# # # #         "type": "end",
# # # #         "winner": winner,
# # # #         "scores": s
# # # #     })

# # # #     match_started = False


# # # # @app.websocket("/")
# # # # async def referee(ws: WebSocket):
# # # #     global match_started

# # # #     await ws.accept()

# # # #     if len(players) >= 2:
# # # #         await send(ws, {"type": "full"})
# # # #         await ws.close()
# # # #         return

# # # #     pid = "P1" if len(players) == 0 else "P2"

# # # #     players[ws] = {
# # # #         "id": pid,
# # # #         "reps": 0
# # # #     }

# # # #     print(f"{pid} connected ({len(players)}/2)")

# # # #     await send(ws, {
# # # #         "type": "assigned",
# # # #         "you": pid
# # # #     })

# # # #     if len(players) == 2 and not match_started:
# # # #         match_started = True
# # # #         asyncio.create_task(run_match())

# # # #     try:

# # # #         while True:
# # # #             raw = await ws.receive_text()
# # # #             data = json.loads(raw)

# # # #             if data.get("type") == "reps":
# # # #                 players[ws]["reps"] = int(data["reps"])

# # # #                 await broadcast({
# # # #                     "type": "scores",
# # # #                     "scores": scores()
# # # #                 })

# # # #     except WebSocketDisconnect:
# # # #         pass

# # # #     finally:

# # # #         if ws in players:
# # # #             print(players[ws]["id"], "disconnected")
# # # #             del players[ws]


# # # # @app.get("/")
# # # # async def root():
# # # #     return {"status": "GymOggle Referee Running"}


# # # # if __name__ == "__main__":
# # # #     uvicorn.run(
# # # #         "server:app",
# # # #         host="0.0.0.0",
# # # #         port=8000,
# # # # #     )
# # # # Test 3 ------------------------
# # # # import asyncio
# # # # import json
# # # # import random
# # # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # # # import uvicorn

# # # # DURATION = 60
# # # # # Code alphabet with no easily-confused characters (no O/0, I/1)
# # # # CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
# # # # CODE_LEN = 4

# # # # app = FastAPI()

# # # # # rooms: code -> {
# # # # #   "players": { websocket: {"id": "P1"/"P2", "reps": int, "ready": bool} },
# # # # #   "started": bool,
# # # # #   "task": asyncio.Task | None
# # # # # }
# # # # rooms = {}


# # # # def new_code():
# # # #     while True:
# # # #         c = "".join(random.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
# # # #         if c not in rooms:
# # # #             return c


# # # # async def send(ws, payload):
# # # #     try:
# # # #         await ws.send_text(json.dumps(payload))
# # # #     except Exception:
# # # #         pass


# # # # async def broadcast(room, payload):
# # # #     await asyncio.gather(
# # # #         *[send(ws, payload) for ws in list(room["players"].keys())],
# # # #         return_exceptions=True,
# # # #     )


# # # # def scores(room):
# # # #     return {p["id"]: p["reps"] for p in room["players"].values()}


# # # # async def run_match(code):
# # # #     room = rooms.get(code)
# # # #     if not room:
# # # #         return

# # # #     room["started"] = True
# # # #     for p in room["players"].values():
# # # #         p["reps"] = 0
# # # #         p["ready"] = False

# # # #     print(f"[{code}] match starting")
# # # #     await broadcast(room, {"type": "start", "duration": DURATION})

# # # #     await asyncio.sleep(DURATION)

# # # #     room = rooms.get(code)          # may have been torn down while we slept
# # # #     if not room:
# # # #         return

# # # #     s = scores(room)
# # # #     if len(s) == 2:
# # # #         p1, p2 = s.get("P1", 0), s.get("P2", 0)
# # # #         winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
# # # #     else:
# # # #         winner = "TIE"

# # # #     print(f"[{code}] match over {s} winner={winner}")
# # # #     await broadcast(room, {"type": "end", "winner": winner, "scores": s})
# # # #     room["started"] = False
# # # #     room["task"] = None


# # # # async def try_start(code):
# # # #     room = rooms.get(code)
# # # #     if room and len(room["players"]) == 2 and not room["started"]:
# # # #         room["task"] = asyncio.create_task(run_match(code))


# # # # @app.websocket("/")
# # # # async def referee(ws: WebSocket):
# # # #     await ws.accept()
# # # #     code = None                     # which room this socket belongs to

# # # #     try:
# # # #         while True:
# # # #             raw = await ws.receive_text()
# # # #             data = json.loads(raw)
# # # #             t = data.get("type")

# # # #             # ---- create a private room ----
# # # #             if t == "create":
# # # #                 if code:
# # # #                     continue        # already in a room
# # # #                 code = new_code()
# # # #                 rooms[code] = {
# # # #                     "players": {ws: {"id": "P1", "reps": 0, "ready": False}},
# # # #                     "started": False,
# # # #                     "task": None,
# # # #                 }
# # # #                 await send(ws, {"type": "created", "code": code, "you": "P1"})
# # # #                 print(f"[{code}] created")

# # # #             # ---- join a room by code ----
# # # #             elif t == "join":
# # # #                 want = (data.get("code") or "").strip().upper()
# # # #                 room = rooms.get(want)
# # # #                 if not room:
# # # #                     await send(ws, {"type": "error", "reason": "no_room"})
# # # #                 elif len(room["players"]) >= 2:
# # # #                     await send(ws, {"type": "error", "reason": "room_full"})
# # # #                 else:
# # # #                     code = want
# # # #                     room["players"][ws] = {"id": "P2", "reps": 0, "ready": False}
# # # #                     await send(ws, {"type": "joined", "you": "P2", "code": code})
# # # #                     await broadcast(room, {"type": "opponent_here"})
# # # #                     print(f"[{code}] P2 joined")
# # # #                     await try_start(code)

# # # #             # ---- live rep updates ----
# # # #             elif t == "reps":
# # # #                 if code and code in rooms and ws in rooms[code]["players"]:
# # # #                     rooms[code]["players"][ws]["reps"] = int(data.get("reps", 0))
# # # #                     await broadcast(rooms[code],
# # # #                                     {"type": "scores", "scores": scores(rooms[code])})

# # # #             # ---- rematch: both must ask before it restarts ----
# # # #             elif t == "rematch":
# # # #                 if code and code in rooms and ws in rooms[code]["players"]:
# # # #                     room = rooms[code]
# # # #                     room["players"][ws]["ready"] = True
# # # #                     both_ready = (len(room["players"]) == 2 and
# # # #                                   all(p["ready"] for p in room["players"].values()))
# # # #                     if both_ready:
# # # #                         await try_start(code)
# # # #                     else:
# # # #                         await broadcast(room, {"type": "rematch_wait"})

# # # #     except WebSocketDisconnect:
# # # #         pass
# # # #     except Exception as e:
# # # #         print("socket error:", e)

# # # #     finally:
# # # #         # clean up this player's room membership
# # # #         if code and code in rooms and ws in rooms[code]["players"]:
# # # #             pid = rooms[code]["players"][ws]["id"]
# # # #             del rooms[code]["players"][ws]
# # # #             print(f"[{code}] {pid} left")

# # # #             if rooms[code]["players"]:
# # # #                 # someone's still here — tell them, stop any running match
# # # #                 task = rooms[code].get("task")
# # # #                 if task:
# # # #                     task.cancel()
# # # #                 rooms[code]["started"] = False
# # # #                 for p in rooms[code]["players"].values():
# # # #                     p["ready"] = False
# # # #                 await broadcast(rooms[code], {"type": "opponent_left"})
# # # #             else:
# # # #                 # empty room — delete it
# # # #                 task = rooms[code].get("task")
# # # #                 if task:
# # # #                     task.cancel()
# # # #                 del rooms[code]
# # # #                 print(f"[{code}] closed")


# # # # @app.get("/")
# # # # async def root():
# # # #     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# # # # if __name__ == "__main__":
# # # #     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# # #     # TEST 4----------------------------

# # # # import asyncio
# # # # import json
# # # # import random
# # # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # # # import uvicorn

# # # # DURATION = 35
# # # # # Code alphabet with no easily-confused characters (no O/0, I/1)
# # # # CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
# # # # CODE_LEN = 4

# # # # app = FastAPI()

# # # # # rooms: code -> {
# # # # #   "players": { websocket: {"id": "P1"/"P2", "reps": int, "ready": bool} },
# # # # #   "started": bool,
# # # # #   "task": asyncio.Task | None
# # # # # }
# # # # rooms = {}


# # # # def new_code():
# # # #     while True:
# # # #         c = "".join(random.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
# # # #         if c not in rooms:
# # # #             return c


# # # # async def send(ws, payload):
# # # #     try:
# # # #         await ws.send_text(json.dumps(payload))
# # # #     except Exception:
# # # #         pass


# # # # async def broadcast(room, payload):
# # # #     await asyncio.gather(
# # # #         *[send(ws, payload) for ws in list(room["players"].keys())],
# # # #         return_exceptions=True,
# # # #     )


# # # # def scores(room):
# # # #     return {p["id"]: p["reps"] for p in room["players"].values()}


# # # # async def run_match(code):
# # # #     room = rooms.get(code)
# # # #     if not room:
# # # #         return

# # # #     room["started"] = True
# # # #     for p in room["players"].values():
# # # #         p["reps"] = 0
# # # #         p["ready"] = False

# # # #     print(f"[{code}] match starting")
# # # #     await broadcast(room, {"type": "start", "duration": DURATION})

# # # #     await asyncio.sleep(DURATION)

# # # #     room = rooms.get(code)          # may have been torn down while we slept
# # # #     if not room:
# # # #         return

# # # #     s = scores(room)
# # # #     if len(s) == 2:
# # # #         p1, p2 = s.get("P1", 0), s.get("P2", 0)
# # # #         winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
# # # #     else:
# # # #         winner = "TIE"

# # # #     print(f"[{code}] match over {s} winner={winner}")
# # # #     await broadcast(room, {"type": "end", "winner": winner, "scores": s})
# # # #     room["started"] = False
# # # #     room["task"] = None


# # # # async def try_start(code):
# # # #     room = rooms.get(code)
# # # #     if room and len(room["players"]) == 2 and not room["started"]:
# # # #         room["task"] = asyncio.create_task(run_match(code))


# # # # @app.websocket("/")
# # # # async def referee(ws: WebSocket):
# # # #     await ws.accept()
# # # #     code = None                     # which room this socket belongs to

# # # #     try:
# # # #         while True:
# # # #             raw = await ws.receive_text()
# # # #             data = json.loads(raw)
# # # #             t = data.get("type")

# # # #             # ---- create a private room ----
# # # #             if t == "create":
# # # #                 if code:
# # # #                     continue        # already in a room
# # # #                 code = new_code()
# # # #                 rooms[code] = {
# # # #                     "players": {ws: {"id": "P1", "reps": 0, "ready": False}},
# # # #                     "started": False,
# # # #                     "task": None,
# # # #                 }
# # # #                 await send(ws, {"type": "created", "code": code, "you": "P1"})
# # # #                 print(f"[{code}] created")

# # # #             # ---- join a room by code ----
# # # #             elif t == "join":
# # # #                 want = (data.get("code") or "").strip().upper()
# # # #                 room = rooms.get(want)
# # # #                 if not room:
# # # #                     await send(ws, {"type": "error", "reason": "no_room"})
# # # #                 elif len(room["players"]) >= 2:
# # # #                     await send(ws, {"type": "error", "reason": "room_full"})
# # # #                 else:
# # # #                     code = want
# # # #                     room["players"][ws] = {"id": "P2", "reps": 0, "ready": False}
# # # #                     await send(ws, {"type": "joined", "you": "P2", "code": code})
# # # #                     await broadcast(room, {"type": "opponent_here"})
# # # #                     print(f"[{code}] P2 joined")
# # # #                     await try_start(code)

# # # #             # ---- live rep updates ----
# # # #             elif t == "reps":
# # # #                 if code and code in rooms and ws in rooms[code]["players"]:
# # # #                     rooms[code]["players"][ws]["reps"] = int(data.get("reps", 0))
# # # #                     await broadcast(rooms[code],
# # # #                                     {"type": "scores", "scores": scores(rooms[code])})

# # # #             # ---- rematch: both must ask before it restarts ----
# # # #             elif t == "rematch":
# # # #                 if code and code in rooms and ws in rooms[code]["players"]:
# # # #                     room = rooms[code]
# # # #                     room["players"][ws]["ready"] = True
# # # #                     both_ready = (len(room["players"]) == 2 and
# # # #                                   all(p["ready"] for p in room["players"].values()))
# # # #                     if both_ready:
# # # #                         await try_start(code)
# # # #                     else:
# # # #                         # tell the requester they're waiting, and tell the
# # # #                         # opponent that a rematch has been offered
# # # #                         for w in room["players"]:
# # # #                             if w is ws:
# # # #                                 await send(w, {"type": "rematch_pending"})
# # # #                             else:
# # # #                                 await send(w, {"type": "rematch_offer"})

# # # #     except WebSocketDisconnect:
# # # #         pass
# # # #     except Exception as e:
# # # #         print("socket error:", e)

# # # #     finally:
# # # #         # clean up this player's room membership
# # # #         if code and code in rooms and ws in rooms[code]["players"]:
# # # #             pid = rooms[code]["players"][ws]["id"]
# # # #             del rooms[code]["players"][ws]
# # # #             print(f"[{code}] {pid} left")

# # # #             if rooms[code]["players"]:
# # # #                 # someone's still here — tell them, stop any running match
# # # #                 task = rooms[code].get("task")
# # # #                 if task:
# # # #                     task.cancel()
# # # #                 rooms[code]["started"] = False
# # # #                 for p in rooms[code]["players"].values():
# # # #                     p["ready"] = False
# # # #                 await broadcast(rooms[code], {"type": "opponent_left"})
# # # #             else:
# # # #                 # empty room — delete it
# # # #                 task = rooms[code].get("task")
# # # #                 if task:
# # # #                     task.cancel()
# # # #                 del rooms[code]
# # # #                 print(f"[{code}] closed")


# # # # @app.get("/")
# # # # async def root():
# # # #     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# # # # if __name__ == "__main__":
# # # #     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# # # # TEST 5----------------------------
# # # # import asyncio
# # # # import json
# # # # import random
# # # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # # # import uvicorn

# # # # DURATION = 35
# # # # # Code alphabet with no easily-confused characters (no O/0, I/1)
# # # # CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
# # # # CODE_LEN = 4

# # # # app = FastAPI()

# # # # # rooms: code -> {
# # # # #   "players": { websocket: {"id": "P1"/"P2", "reps": int, "ready": bool} },
# # # # #   "started": bool,
# # # # #   "task": asyncio.Task | None
# # # # # }
# # # # rooms = {}


# # # # def new_code():
# # # #     while True:
# # # #         c = "".join(random.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
# # # #         if c not in rooms:
# # # #             return c


# # # # async def send(ws, payload):
# # # #     try:
# # # #         await ws.send_text(json.dumps(payload))
# # # #     except Exception:
# # # #         pass


# # # # async def broadcast(room, payload):
# # # #     await asyncio.gather(
# # # #         *[send(ws, payload) for ws in list(room["players"].keys())],
# # # #         return_exceptions=True,
# # # #     )


# # # # def scores(room):
# # # #     return {p["id"]: p["reps"] for p in room["players"].values()}


# # # # async def run_match(code):
# # # #     room = rooms.get(code)
# # # #     if not room:
# # # #         return

# # # #     room["started"] = True
# # # #     for p in room["players"].values():
# # # #         p["reps"] = 0
# # # #         p["ready"] = False

# # # #     print(f"[{code}] match starting")
# # # #     await broadcast(room, {"type": "start", "duration": DURATION,
# # # #                            "exercise": room.get("exercise", "squats")})

# # # #     await asyncio.sleep(DURATION)

# # # #     room = rooms.get(code)          # may have been torn down while we slept
# # # #     if not room:
# # # #         return

# # # #     s = scores(room)
# # # #     if len(s) == 2:
# # # #         p1, p2 = s.get("P1", 0), s.get("P2", 0)
# # # #         winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
# # # #     else:
# # # #         winner = "TIE"

# # # #     print(f"[{code}] match over {s} winner={winner}")
# # # #     await broadcast(room, {"type": "end", "winner": winner, "scores": s})
# # # #     room["started"] = False
# # # #     room["task"] = None


# # # # async def try_start(code):
# # # #     room = rooms.get(code)
# # # #     if room and len(room["players"]) == 2 and not room["started"]:
# # # #         room["task"] = asyncio.create_task(run_match(code))


# # # # @app.websocket("/")
# # # # async def referee(ws: WebSocket):
# # # #     await ws.accept()
# # # #     code = None                     # which room this socket belongs to

# # # #     try:
# # # #         while True:
# # # #             raw = await ws.receive_text()
# # # #             data = json.loads(raw)
# # # #             t = data.get("type")

# # # #             # ---- create a private room ----
# # # #             if t == "create":
# # # #                 if code:
# # # #                     continue        # already in a room
# # # #                 code = new_code()
# # # #                 exercise = data.get("exercise", "squats")
# # # #                 rooms[code] = {
# # # #                     "players": {ws: {"id": "P1", "reps": 0, "ready": False}},
# # # #                     "started": False,
# # # #                     "task": None,
# # # #                     "exercise": exercise,
# # # #                 }
# # # #                 await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
# # # #                 print(f"[{code}] created ({exercise})")

# # # #             # ---- join a room by code ----
# # # #             elif t == "join":
# # # #                 want = (data.get("code") or "").strip().upper()
# # # #                 room = rooms.get(want)
# # # #                 if not room:
# # # #                     await send(ws, {"type": "error", "reason": "no_room"})
# # # #                 elif len(room["players"]) >= 2:
# # # #                     await send(ws, {"type": "error", "reason": "room_full"})
# # # #                 else:
# # # #                     code = want
# # # #                     room["players"][ws] = {"id": "P2", "reps": 0, "ready": False}
# # # #                     await send(ws, {"type": "joined", "you": "P2", "code": code,
# # # #                                     "exercise": room.get("exercise", "squats")})
# # # #                     await broadcast(room, {"type": "opponent_here"})
# # # #                     print(f"[{code}] P2 joined")
# # # #                     await try_start(code)

# # # #             # ---- live rep updates ----
# # # #             elif t == "reps":
# # # #                 if code and code in rooms and ws in rooms[code]["players"]:
# # # #                     rooms[code]["players"][ws]["reps"] = int(data.get("reps", 0))
# # # #                     await broadcast(rooms[code],
# # # #                                     {"type": "scores", "scores": scores(rooms[code])})

# # # #             # ---- rematch: both must ask before it restarts ----
# # # #             elif t == "rematch":
# # # #                 if code and code in rooms and ws in rooms[code]["players"]:
# # # #                     room = rooms[code]
# # # #                     room["players"][ws]["ready"] = True
# # # #                     both_ready = (len(room["players"]) == 2 and
# # # #                                   all(p["ready"] for p in room["players"].values()))
# # # #                     if both_ready:
# # # #                         await try_start(code)
# # # #                     else:
# # # #                         # tell the requester they're waiting, and tell the
# # # #                         # opponent that a rematch has been offered
# # # #                         for w in room["players"]:
# # # #                             if w is ws:
# # # #                                 await send(w, {"type": "rematch_pending"})
# # # #                             else:
# # # #                                 await send(w, {"type": "rematch_offer"})

# # # #     except WebSocketDisconnect:
# # # #         pass
# # # #     except Exception as e:
# # # #         print("socket error:", e)

# # # #     finally:
# # # #         # clean up this player's room membership
# # # #         if code and code in rooms and ws in rooms[code]["players"]:
# # # #             pid = rooms[code]["players"][ws]["id"]
# # # #             del rooms[code]["players"][ws]
# # # #             print(f"[{code}] {pid} left")

# # # #             if rooms[code]["players"]:
# # # #                 # someone's still here — tell them, stop any running match
# # # #                 task = rooms[code].get("task")
# # # #                 if task:
# # # #                     task.cancel()
# # # #                 rooms[code]["started"] = False
# # # #                 for p in rooms[code]["players"].values():
# # # #                     p["ready"] = False
# # # #                 await broadcast(rooms[code], {"type": "opponent_left"})
# # # #             else:
# # # #                 # empty room — delete it
# # # #                 task = rooms[code].get("task")
# # # #                 if task:
# # # #                     task.cancel()
# # # #                 del rooms[code]
# # # #                 print(f"[{code}] closed")


# # # # @app.get("/")
# # # # async def root():
# # # #     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# # # # if __name__ == "__main__":
# # # #     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# # # # Test 6----------------------------
# # # # import asyncio
# # # # import json
# # # # import random
# # # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # # # import uvicorn
# # # # import os
# # # # from supabase import create_client

# # # # DURATION = 35
# # # # # Code alphabet with no easily-confused characters (no O/0, I/1)
# # # # CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
# # # # CODE_LEN = 4

# # # # app = FastAPI()

# # # # # rooms: code -> {
# # # # #   "players": { websocket: {"id": "P1"/"P2", "reps": int, "ready": bool} },
# # # # #   "started": bool,
# # # # #   "task": asyncio.Task | None
# # # # # }
# # # # rooms = {}

# # # # # --- Supabase connection (reads the env vars you set on Render) ---
# # # # SUPABASE_URL = os.environ.get("project_url")
# # # # SUPABASE_KEY = os.environ.get("service_role_key")
# # # # supabase = None
# # # # if SUPABASE_URL and SUPABASE_KEY:
# # # #     try:
# # # #         supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
# # # #         print("Supabase connected")
# # # #     except Exception as e:
# # # #         print("Supabase connect failed:", e)
# # # # else:
# # # #     print("Supabase env vars missing")

# # # # def new_code():
# # # #     while True:
# # # #         c = "".join(random.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
# # # #         if c not in rooms:
# # # #             return c


# # # # async def send(ws, payload):
# # # #     try:
# # # #         await ws.send_text(json.dumps(payload))
# # # #     except Exception:
# # # #         pass


# # # # async def broadcast(room, payload):
# # # #     await asyncio.gather(
# # # #         *[send(ws, payload) for ws in list(room["players"].keys())],
# # # #         return_exceptions=True,
# # # #     )


# # # # def scores(room):
# # # #     return {p["id"]: p["reps"] for p in room["players"].values()}


# # # # async def run_match(code):
# # # #     room = rooms.get(code)
# # # #     if not room:
# # # #         return

# # # #     room["started"] = True
# # # #     for p in room["players"].values():
# # # #         p["reps"] = 0
# # # #         p["ready"] = False

# # # #     print(f"[{code}] match starting")
# # # #     await broadcast(room, {"type": "start", "duration": DURATION,
# # # #                            "exercise": room.get("exercise", "squats")})

# # # #     await asyncio.sleep(DURATION)

# # # #     room = rooms.get(code)          # may have been torn down while we slept
# # # #     if not room:
# # # #         return

# # # #     s = scores(room)
# # # #     if len(s) == 2:
# # # #         p1, p2 = s.get("P1", 0), s.get("P2", 0)
# # # #         winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
# # # #     else:
# # # #         winner = "TIE"

# # # #     print(f"[{code}] match over {s} winner={winner}")
# # # #     await broadcast(room, {"type": "end", "winner": winner, "scores": s})
# # # #     room["started"] = False
# # # #     room["task"] = None


# # # # async def try_start(code):
# # # #     room = rooms.get(code)
# # # #     if room and len(room["players"]) == 2 and not room["started"]:
# # # #         room["task"] = asyncio.create_task(run_match(code))


# # # # waiting = {}   # exercise -> list of websockets waiting for a random match


# # # # def room_of(ws):
# # # #     for c, room in rooms.items():
# # # #         if ws in room["players"]:
# # # #             return c, room
# # # #     return None, None


# # # # def enqueue(ws, exercise):
# # # #     waiting.setdefault(exercise, []).append(ws)


# # # # def dequeue(ws):
# # # #     for lst in waiting.values():
# # # #         if ws in lst:
# # # #             lst.remove(ws)


# # # # async def leave_room(ws):
# # # #     """Remove a player from the matchmaking queue and/or their room,
# # # #     and notify the opponent. Safe to call on explicit leave or disconnect."""
# # # #     dequeue(ws)
# # # #     c, room = room_of(ws)
# # # #     if not room:
# # # #         return
# # # #     pid = room["players"][ws]["id"]
# # # #     del room["players"][ws]
# # # #     print(f"[{c}] {pid} left")
# # # #     task = room.get("task")
# # # #     if task:
# # # #         task.cancel()
# # # #     if room["players"]:
# # # #         room["started"] = False
# # # #         for p in room["players"].values():
# # # #             p["ready"] = False
# # # #         await broadcast(room, {"type": "opponent_left"})
# # # #     else:
# # # #         del rooms[c]
# # # #         print(f"[{c}] closed")


# # # # @app.websocket("/")
# # # # async def referee(ws: WebSocket):
# # # #     await ws.accept()

# # # #     try:
# # # #         while True:
# # # #             raw = await ws.receive_text()
# # # #             data = json.loads(raw)
# # # #             t = data.get("type")

# # # #             # ---- create a private room ----
# # # #             if t == "create":
# # # #                 if room_of(ws)[1]:
# # # #                     continue
# # # #                 code = new_code()
# # # #                 exercise = data.get("exercise", "squats")
# # # #                 rooms[code] = {
# # # #                     "players": {ws: {"id": "P1", "reps": 0, "ready": False}},
# # # #                     "started": False,
# # # #                     "task": None,
# # # #                     "exercise": exercise,
# # # #                 }
# # # #                 await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
# # # #                 print(f"[{code}] created ({exercise})")

# # # #             # ---- join a private room by code ----
# # # #             elif t == "join":
# # # #                 want = (data.get("code") or "").strip().upper()
# # # #                 room = rooms.get(want)
# # # #                 if not room:
# # # #                     await send(ws, {"type": "error", "reason": "no_room"})
# # # #                 elif len(room["players"]) >= 2:
# # # #                     await send(ws, {"type": "error", "reason": "room_full"})
# # # #                 else:
# # # #                     room["players"][ws] = {"id": "P2", "reps": 0, "ready": False}
# # # #                     await send(ws, {"type": "joined", "you": "P2", "code": want,
# # # #                                     "exercise": room.get("exercise", "squats")})
# # # #                     await broadcast(room, {"type": "opponent_here"})
# # # #                     print(f"[{want}] P2 joined")
# # # #                     await try_start(want)

# # # #             # ---- quick match: pair with a waiting stranger (same exercise) ----
# # # #             elif t == "quick":
# # # #                 if room_of(ws)[1]:
# # # #                     continue
# # # #                 exercise = data.get("exercise", "squats")
# # # #                 dequeue(ws)                       # never queue the same socket twice
# # # #                 q = waiting.get(exercise, [])
# # # #                 opponent = None
# # # #                 while q:                          # find a still-waiting opponent
# # # #                     cand = q.pop(0)
# # # #                     if cand is not ws:
# # # #                         opponent = cand
# # # #                         break
# # # #                 if opponent is not None:
# # # #                     code = new_code()
# # # #                     rooms[code] = {
# # # #                         "players": {opponent: {"id": "P1", "reps": 0, "ready": False},
# # # #                                     ws:       {"id": "P2", "reps": 0, "ready": False}},
# # # #                         "started": False,
# # # #                         "task": None,
# # # #                         "exercise": exercise,
# # # #                     }
# # # #                     await send(opponent, {"type": "matched", "you": "P1", "exercise": exercise})
# # # #                     await send(ws,       {"type": "matched", "you": "P2", "exercise": exercise})
# # # #                     print(f"[{code}] quick match ({exercise})")
# # # #                     await try_start(code)
# # # #                 else:
# # # #                     enqueue(ws, exercise)
# # # #                     await send(ws, {"type": "searching", "exercise": exercise})
# # # #                     print(f"[queue] {exercise}: {len(waiting.get(exercise, []))} waiting")

# # # #             # ---- cancel searching ----
# # # #             elif t == "cancel":
# # # #                 dequeue(ws)
# # # #                 await send(ws, {"type": "cancelled"})

# # # #             # ---- live rep updates ----
# # # #             elif t == "reps":
# # # #                 c, room = room_of(ws)
# # # #                 if room:
# # # #                     room["players"][ws]["reps"] = int(data.get("reps", 0))
# # # #                     await broadcast(room, {"type": "scores", "scores": scores(room)})

# # # #             # ---- rematch: both must ask before it restarts ----
# # # #             elif t == "rematch":
# # # #                 c, room = room_of(ws)
# # # #                 if room:
# # # #                     room["players"][ws]["ready"] = True
# # # #                     both_ready = (len(room["players"]) == 2 and
# # # #                                   all(p["ready"] for p in room["players"].values()))
# # # #                     if both_ready:
# # # #                         await try_start(c)
# # # #                     else:
# # # #                         for w in room["players"]:
# # # #                             if w is ws:
# # # #                                 await send(w, {"type": "rematch_pending"})
# # # #                             else:
# # # #                                 await send(w, {"type": "rematch_offer"})

# # # #             # ---- explicit leave (reliable — doesn't wait for disconnect) ----
# # # #             elif t == "leave":
# # # #                 await leave_room(ws)

# # # #     except WebSocketDisconnect:
# # # #         pass
# # # #     except Exception as e:
# # # #         print("socket error:", e)

# # # #     finally:
# # # #         await leave_room(ws)


# # # # @app.get("/")
# # # # async def root():
# # # #     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# # # # if __name__ == "__main__":
# # # #     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# # # # # Test 7----------------------------
# # # # import asyncio
# # # # import json
# # # # import random
# # # # import os
# # # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # # # import uvicorn

# # # # # --- Supabase connection (reads the env vars set on Render) ---
# # # # try:
# # # #     from supabase import create_client
# # # #     SUPABASE_URL = os.environ.get("project_url")
# # # #     SUPABASE_KEY = os.environ.get("service_role_key")
# # # #     supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None
# # # #     print("Supabase connected" if supabase else "Supabase env vars missing")
# # # # except Exception as e:
# # # #     supabase = None
# # # #     print("Supabase setup failed:", e)

# # # # DURATION = 35
# # # # # Code alphabet with no easily-confused characters (no O/0, I/1)
# # # # CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
# # # # CODE_LEN = 4

# # # # app = FastAPI()

# # # # # rooms: code -> {
# # # # #   "players": { websocket: {"id": "P1"/"P2", "reps": int, "ready": bool} },
# # # # #   "started": bool,
# # # # #   "task": asyncio.Task | None
# # # # # }
# # # # rooms = {}


# # # # def new_code():
# # # #     while True:
# # # #         c = "".join(random.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
# # # #         if c not in rooms:
# # # #             return c


# # # # async def send(ws, payload):
# # # #     try:
# # # #         await ws.send_text(json.dumps(payload))
# # # #     except Exception:
# # # #         pass


# # # # async def broadcast(room, payload):
# # # #     await asyncio.gather(
# # # #         *[send(ws, payload) for ws in list(room["players"].keys())],
# # # #         return_exceptions=True,
# # # #     )


# # # # def scores(room):
# # # #     return {p["id"]: p["reps"] for p in room["players"].values()}


# # # # async def run_match(code):
# # # #     room = rooms.get(code)
# # # #     if not room:
# # # #         return

# # # #     room["started"] = True
# # # #     for p in room["players"].values():
# # # #         p["reps"] = 0
# # # #         p["ready"] = False

# # # #     print(f"[{code}] match starting")
# # # #     await broadcast(room, {"type": "start", "duration": DURATION,
# # # #                            "exercise": room.get("exercise", "squats")})

# # # #     await asyncio.sleep(DURATION)

# # # #     room = rooms.get(code)          # may have been torn down while we slept
# # # #     if not room:
# # # #         return

# # # #     s = scores(room)
# # # #     if len(s) == 2:
# # # #         p1, p2 = s.get("P1", 0), s.get("P2", 0)
# # # #         winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
# # # #     else:
# # # #         winner = "TIE"

# # # #     print(f"[{code}] match over {s} winner={winner}")
# # # #     await broadcast(room, {"type": "end", "winner": winner, "scores": s})
# # # #     room["started"] = False
# # # #     room["task"] = None


# # # # async def try_start(code):
# # # #     room = rooms.get(code)
# # # #     if room and len(room["players"]) == 2 and not room["started"]:
# # # #         room["task"] = asyncio.create_task(run_match(code))


# # # # waiting = {}   # exercise -> list of websockets waiting for a random match


# # # # def room_of(ws):
# # # #     for c, room in rooms.items():
# # # #         if ws in room["players"]:
# # # #             return c, room
# # # #     return None, None


# # # # def enqueue(ws, exercise):
# # # #     waiting.setdefault(exercise, []).append(ws)


# # # # def dequeue(ws):
# # # #     for lst in waiting.values():
# # # #         if ws in lst:
# # # #             lst.remove(ws)


# # # # async def leave_room(ws):
# # # #     """Remove a player from the matchmaking queue and/or their room,
# # # #     and notify the opponent. Safe to call on explicit leave or disconnect."""
# # # #     dequeue(ws)
# # # #     c, room = room_of(ws)
# # # #     if not room:
# # # #         return
# # # #     pid = room["players"][ws]["id"]
# # # #     del room["players"][ws]
# # # #     print(f"[{c}] {pid} left")
# # # #     task = room.get("task")
# # # #     if task:
# # # #         task.cancel()
# # # #     if room["players"]:
# # # #         room["started"] = False
# # # #         for p in room["players"].values():
# # # #             p["ready"] = False
# # # #         await broadcast(room, {"type": "opponent_left"})
# # # #     else:
# # # #         del rooms[c]
# # # #         print(f"[{c}] closed")


# # # # @app.websocket("/")
# # # # async def referee(ws: WebSocket):
# # # #     await ws.accept()

# # # #     try:
# # # #         while True:
# # # #             raw = await ws.receive_text()
# # # #             data = json.loads(raw)
# # # #             t = data.get("type")

# # # #             # ---- create a private room ----
# # # #             if t == "create":
# # # #                 if room_of(ws)[1]:
# # # #                     continue
# # # #                 code = new_code()
# # # #                 exercise = data.get("exercise", "squats")
# # # #                 rooms[code] = {
# # # #                     "players": {ws: {"id": "P1", "reps": 0, "ready": False}},
# # # #                     "started": False,
# # # #                     "task": None,
# # # #                     "exercise": exercise,
# # # #                 }
# # # #                 await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
# # # #                 print(f"[{code}] created ({exercise})")

# # # #             # ---- join a private room by code ----
# # # #             elif t == "join":
# # # #                 want = (data.get("code") or "").strip().upper()
# # # #                 room = rooms.get(want)
# # # #                 if not room:
# # # #                     await send(ws, {"type": "error", "reason": "no_room"})
# # # #                 elif len(room["players"]) >= 2:
# # # #                     await send(ws, {"type": "error", "reason": "room_full"})
# # # #                 else:
# # # #                     room["players"][ws] = {"id": "P2", "reps": 0, "ready": False}
# # # #                     await send(ws, {"type": "joined", "you": "P2", "code": want,
# # # #                                     "exercise": room.get("exercise", "squats")})
# # # #                     await broadcast(room, {"type": "opponent_here"})
# # # #                     print(f"[{want}] P2 joined")
# # # #                     await try_start(want)

# # # #             # ---- quick match: pair with a waiting stranger (same exercise) ----
# # # #             elif t == "quick":
# # # #                 if room_of(ws)[1]:
# # # #                     continue
# # # #                 exercise = data.get("exercise", "squats")
# # # #                 dequeue(ws)                       # never queue the same socket twice
# # # #                 q = waiting.get(exercise, [])
# # # #                 opponent = None
# # # #                 while q:                          # find a still-waiting opponent
# # # #                     cand = q.pop(0)
# # # #                     if cand is not ws:
# # # #                         opponent = cand
# # # #                         break
# # # #                 if opponent is not None:
# # # #                     code = new_code()
# # # #                     rooms[code] = {
# # # #                         "players": {opponent: {"id": "P1", "reps": 0, "ready": False},
# # # #                                     ws:       {"id": "P2", "reps": 0, "ready": False}},
# # # #                         "started": False,
# # # #                         "task": None,
# # # #                         "exercise": exercise,
# # # #                     }
# # # #                     await send(opponent, {"type": "matched", "you": "P1", "exercise": exercise})
# # # #                     await send(ws,       {"type": "matched", "you": "P2", "exercise": exercise})
# # # #                     print(f"[{code}] quick match ({exercise})")
# # # #                     await try_start(code)
# # # #                 else:
# # # #                     enqueue(ws, exercise)
# # # #                     await send(ws, {"type": "searching", "exercise": exercise})
# # # #                     print(f"[queue] {exercise}: {len(waiting.get(exercise, []))} waiting")

# # # #             # ---- cancel searching ----
# # # #             elif t == "cancel":
# # # #                 dequeue(ws)
# # # #                 await send(ws, {"type": "cancelled"})

# # # #             # ---- live rep updates ----
# # # #             elif t == "reps":
# # # #                 c, room = room_of(ws)
# # # #                 if room:
# # # #                     room["players"][ws]["reps"] = int(data.get("reps", 0))
# # # #                     await broadcast(room, {"type": "scores", "scores": scores(room)})

# # # #             # ---- rematch: both must ask before it restarts ----
# # # #             elif t == "rematch":
# # # #                 c, room = room_of(ws)
# # # #                 if room:
# # # #                     room["players"][ws]["ready"] = True
# # # #                     both_ready = (len(room["players"]) == 2 and
# # # #                                   all(p["ready"] for p in room["players"].values()))
# # # #                     if both_ready:
# # # #                         await try_start(c)
# # # #                     else:
# # # #                         for w in room["players"]:
# # # #                             if w is ws:
# # # #                                 await send(w, {"type": "rematch_pending"})
# # # #                             else:
# # # #                                 await send(w, {"type": "rematch_offer"})

# # # #             # ---- explicit leave (reliable — doesn't wait for disconnect) ----
# # # #             elif t == "leave":
# # # #                 await leave_room(ws)

# # # #     except WebSocketDisconnect:
# # # #         pass
# # # #     except Exception as e:
# # # #         print("socket error:", e)

# # # #     finally:
# # # #         await leave_room(ws)


# # # # @app.get("/")
# # # # async def root():
# # # #     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# # # # @app.get("/dbtest")
# # # # async def dbtest():
# # # #     if not supabase:
# # # #         return {"ok": False, "error": "no supabase client (check env vars)"}
# # # #     try:
# # # #         supabase.table("pings").insert({"note": "hello from render"}).execute()
# # # #         rows = supabase.table("pings").select("*").order("created_at", desc=True).limit(3).execute()
# # # #         return {"ok": True, "recent_pings": rows.data}
# # # #     except Exception as e:
# # # #         return {"ok": False, "error": str(e)}


# # # # if __name__ == "__main__":
# # # #     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# # # # Test 8----------------------------
# # # # import asyncio
# # # # import json
# # # # import random
# # # # import os
# # # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # # # import uvicorn

# # # # # --- Supabase connection (reads the env vars set on Render) ---
# # # # try:
# # # #     from supabase import create_client
# # # #     SUPABASE_URL = os.environ.get("project_url")
# # # #     SUPABASE_KEY = os.environ.get("service_role_key")
# # # #     supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None
# # # #     print("Supabase connected" if supabase else "Supabase env vars missing")
# # # # except Exception as e:
# # # #     supabase = None
# # # #     print("Supabase setup failed:", e)

# # # # DURATION = 35
# # # # # Code alphabet with no easily-confused characters (no O/0, I/1)
# # # # CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
# # # # CODE_LEN = 4

# # # # app = FastAPI()

# # # # # allow the browser (Netlify origin) to fetch the leaderboard over HTTP
# # # # from fastapi.middleware.cors import CORSMiddleware
# # # # app.add_middleware(
# # # #     CORSMiddleware,
# # # #     allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
# # # # )

# # # # # rooms: code -> {
# # # # #   "players": { websocket: {"id": "P1"/"P2", "reps": int, "ready": bool} },
# # # # #   "started": bool,
# # # # #   "task": asyncio.Task | None
# # # # # }
# # # # rooms = {}


# # # # def new_code():
# # # #     while True:
# # # #         c = "".join(random.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
# # # #         if c not in rooms:
# # # #             return c


# # # # async def send(ws, payload):
# # # #     try:
# # # #         await ws.send_text(json.dumps(payload))
# # # #     except Exception:
# # # #         pass


# # # # async def broadcast(room, payload):
# # # #     await asyncio.gather(
# # # #         *[send(ws, payload) for ws in list(room["players"].keys())],
# # # #         return_exceptions=True,
# # # #     )


# # # # def scores(room):
# # # #     return {p["id"]: p["reps"] for p in room["players"].values()}


# # # # # --- player identity (lightweight browser id + name, sent by the client) ---
# # # # ident = {}   # websocket -> {"pid": str, "name": str}

# # # # def remember(ws, data):
# # # #     ident[ws] = {"pid": (data.get("pid") or "anon"), "name": (data.get("name") or "Player")}

# # # # def pdict(ws, role):
# # # #     i = ident.get(ws, {})
# # # #     return {"id": role, "pid": i.get("pid", "anon"), "name": i.get("name", "Player"),
# # # #             "reps": 0, "ready": False}


# # # # # --- persistence: record a finished match + update player summaries ---
# # # # def record_match_sync(exercise, p1, p2, winner):
# # # #     if not supabase:
# # # #         return
# # # #     try:
# # # #         supabase.table("matches").insert({
# # # #             "exercise": exercise,
# # # #             "p1_id": p1["pid"], "p1_name": p1["name"], "p1_reps": p1["reps"],
# # # #             "p2_id": p2["pid"], "p2_name": p2["name"], "p2_reps": p2["reps"],
# # # #             "winner": "tie" if winner == "TIE" else ("p1" if winner == "P1" else "p2"),
# # # #         }).execute()
# # # #         _update_player(p1, exercise, won=(winner == "P1"), drew=(winner == "TIE"))
# # # #         _update_player(p2, exercise, won=(winner == "P2"), drew=(winner == "TIE"))
# # # #     except Exception as e:
# # # #         print("record_match failed:", e)

# # # # def _update_player(p, exercise, won, drew):
# # # #     pid = p.get("pid")
# # # #     if not pid or pid == "anon":
# # # #         return
# # # #     try:
# # # #         res = supabase.table("players").select("*").eq("id", pid).execute()
# # # #         row = res.data[0] if res.data else {}
# # # #         cur = (row.get("current_streak", 0) + 1) if won else 0
# # # #         payload = {
# # # #             "id": pid, "name": p.get("name", "Player"),
# # # #             "wins":   row.get("wins", 0)   + (1 if won else 0),
# # # #             "losses": row.get("losses", 0) + (0 if (won or drew) else 1),
# # # #             "draws":  row.get("draws", 0)  + (1 if drew else 0),
# # # #             "current_streak": cur,
# # # #             "best_streak": max(row.get("best_streak", 0), cur),
# # # #         }
# # # #         if exercise in ("squats", "pushups", "situps"):
# # # #             col = "best_" + exercise
# # # #             payload[col] = max(row.get(col, 0), p.get("reps", 0))
# # # #         supabase.table("players").upsert(payload).execute()
# # # #     except Exception as e:
# # # #         print("update_player failed:", e)


# # # # async def run_match(code):
# # # #     room = rooms.get(code)
# # # #     if not room:
# # # #         return

# # # #     room["started"] = True
# # # #     for p in room["players"].values():
# # # #         p["reps"] = 0
# # # #         p["ready"] = False

# # # #     print(f"[{code}] match starting")
# # # #     await broadcast(room, {"type": "start", "duration": DURATION,
# # # #                            "exercise": room.get("exercise", "squats")})

# # # #     await asyncio.sleep(DURATION)

# # # #     room = rooms.get(code)          # may have been torn down while we slept
# # # #     if not room:
# # # #         return

# # # #     s = scores(room)
# # # #     if len(s) == 2:
# # # #         p1, p2 = s.get("P1", 0), s.get("P2", 0)
# # # #         winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
# # # #     else:
# # # #         winner = "TIE"

# # # #     print(f"[{code}] match over {s} winner={winner}")
# # # #     await broadcast(room, {"type": "end", "winner": winner, "scores": s})

# # # #     # save the result to the database (in a thread so it never blocks the game)
# # # #     p1p = next((p for p in room["players"].values() if p["id"] == "P1"), None)
# # # #     p2p = next((p for p in room["players"].values() if p["id"] == "P2"), None)
# # # #     if p1p and p2p and len(s) == 2:
# # # #         asyncio.get_event_loop().run_in_executor(
# # # #             None, record_match_sync, room.get("exercise", "squats"),
# # # #             dict(p1p), dict(p2p), winner)

# # # #     room["started"] = False
# # # #     room["task"] = None


# # # # async def try_start(code):
# # # #     room = rooms.get(code)
# # # #     if room and len(room["players"]) == 2 and not room["started"]:
# # # #         room["task"] = asyncio.create_task(run_match(code))


# # # # waiting = {}   # exercise -> list of websockets waiting for a random match


# # # # def room_of(ws):
# # # #     for c, room in rooms.items():
# # # #         if ws in room["players"]:
# # # #             return c, room
# # # #     return None, None


# # # # def enqueue(ws, exercise):
# # # #     waiting.setdefault(exercise, []).append(ws)


# # # # def dequeue(ws):
# # # #     for lst in waiting.values():
# # # #         if ws in lst:
# # # #             lst.remove(ws)


# # # # async def leave_room(ws):
# # # #     """Remove a player from the matchmaking queue and/or their room,
# # # #     and notify the opponent. Safe to call on explicit leave or disconnect."""
# # # #     dequeue(ws)
# # # #     ident.pop(ws, None)
# # # #     c, room = room_of(ws)
# # # #     if not room:
# # # #         return
# # # #     pid = room["players"][ws]["id"]
# # # #     del room["players"][ws]
# # # #     print(f"[{c}] {pid} left")
# # # #     task = room.get("task")
# # # #     if task:
# # # #         task.cancel()
# # # #     if room["players"]:
# # # #         room["started"] = False
# # # #         for p in room["players"].values():
# # # #             p["ready"] = False
# # # #         await broadcast(room, {"type": "opponent_left"})
# # # #     else:
# # # #         del rooms[c]
# # # #         print(f"[{c}] closed")


# # # # @app.websocket("/")
# # # # async def referee(ws: WebSocket):
# # # #     await ws.accept()

# # # #     try:
# # # #         while True:
# # # #             raw = await ws.receive_text()
# # # #             data = json.loads(raw)
# # # #             t = data.get("type")

# # # #             # ---- create a private room ----
# # # #             if t == "create":
# # # #                 if room_of(ws)[1]:
# # # #                     continue
# # # #                 remember(ws, data)
# # # #                 code = new_code()
# # # #                 exercise = data.get("exercise", "squats")
# # # #                 rooms[code] = {
# # # #                     "players": {ws: pdict(ws, "P1")},
# # # #                     "started": False,
# # # #                     "task": None,
# # # #                     "exercise": exercise,
# # # #                 }
# # # #                 await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
# # # #                 print(f"[{code}] created ({exercise})")

# # # #             # ---- join a private room by code ----
# # # #             elif t == "join":
# # # #                 want = (data.get("code") or "").strip().upper()
# # # #                 room = rooms.get(want)
# # # #                 if not room:
# # # #                     await send(ws, {"type": "error", "reason": "no_room"})
# # # #                 elif len(room["players"]) >= 2:
# # # #                     await send(ws, {"type": "error", "reason": "room_full"})
# # # #                 else:
# # # #                     remember(ws, data)
# # # #                     room["players"][ws] = pdict(ws, "P2")
# # # #                     await send(ws, {"type": "joined", "you": "P2", "code": want,
# # # #                                     "exercise": room.get("exercise", "squats")})
# # # #                     await broadcast(room, {"type": "opponent_here"})
# # # #                     print(f"[{want}] P2 joined")
# # # #                     await try_start(want)

# # # #             # ---- quick match: pair with a waiting stranger (same exercise) ----
# # # #             elif t == "quick":
# # # #                 if room_of(ws)[1]:
# # # #                     continue
# # # #                 remember(ws, data)
# # # #                 exercise = data.get("exercise", "squats")
# # # #                 dequeue(ws)                       # never queue the same socket twice
# # # #                 q = waiting.get(exercise, [])
# # # #                 opponent = None
# # # #                 while q:                          # find a still-waiting opponent
# # # #                     cand = q.pop(0)
# # # #                     if cand is not ws:
# # # #                         opponent = cand
# # # #                         break
# # # #                 if opponent is not None:
# # # #                     code = new_code()
# # # #                     rooms[code] = {
# # # #                         "players": {opponent: pdict(opponent, "P1"),
# # # #                                     ws:       pdict(ws, "P2")},
# # # #                         "started": False,
# # # #                         "task": None,
# # # #                         "exercise": exercise,
# # # #                     }
# # # #                     await send(opponent, {"type": "matched", "you": "P1", "exercise": exercise})
# # # #                     await send(ws,       {"type": "matched", "you": "P2", "exercise": exercise})
# # # #                     print(f"[{code}] quick match ({exercise})")
# # # #                     await try_start(code)
# # # #                 else:
# # # #                     enqueue(ws, exercise)
# # # #                     await send(ws, {"type": "searching", "exercise": exercise})
# # # #                     print(f"[queue] {exercise}: {len(waiting.get(exercise, []))} waiting")

# # # #             # ---- cancel searching ----
# # # #             elif t == "cancel":
# # # #                 dequeue(ws)
# # # #                 await send(ws, {"type": "cancelled"})

# # # #             # ---- live rep updates ----
# # # #             elif t == "reps":
# # # #                 c, room = room_of(ws)
# # # #                 if room:
# # # #                     room["players"][ws]["reps"] = int(data.get("reps", 0))
# # # #                     await broadcast(room, {"type": "scores", "scores": scores(room)})

# # # #             # ---- rematch: both must ask before it restarts ----
# # # #             elif t == "rematch":
# # # #                 c, room = room_of(ws)
# # # #                 if room:
# # # #                     room["players"][ws]["ready"] = True
# # # #                     both_ready = (len(room["players"]) == 2 and
# # # #                                   all(p["ready"] for p in room["players"].values()))
# # # #                     if both_ready:
# # # #                         await try_start(c)
# # # #                     else:
# # # #                         for w in room["players"]:
# # # #                             if w is ws:
# # # #                                 await send(w, {"type": "rematch_pending"})
# # # #                             else:
# # # #                                 await send(w, {"type": "rematch_offer"})

# # # #             # ---- explicit leave (reliable — doesn't wait for disconnect) ----
# # # #             elif t == "leave":
# # # #                 await leave_room(ws)

# # # #     except WebSocketDisconnect:
# # # #         pass
# # # #     except Exception as e:
# # # #         print("socket error:", e)

# # # #     finally:
# # # #         await leave_room(ws)


# # # # @app.get("/")
# # # # async def root():
# # # #     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# # # # @app.get("/dbtest")
# # # # async def dbtest():
# # # #     if not supabase:
# # # #         return {"ok": False, "error": "no supabase client (check env vars)"}
# # # #     try:
# # # #         supabase.table("pings").insert({"note": "hello from render"}).execute()
# # # #         rows = supabase.table("pings").select("*").order("created_at", desc=True).limit(3).execute()
# # # #         return {"ok": True, "recent_pings": rows.data}
# # # #     except Exception as e:
# # # #         return {"ok": False, "error": str(e)}


# # # # # sync def -> FastAPI runs it in a threadpool, so DB reads don't block the game loop
# # # # @app.get("/leaderboard")
# # # # def leaderboard():
# # # #     if not supabase:
# # # #         return {"ok": False, "error": "no db"}
# # # #     out = {"ok": True, "scores": {}, "wins": []}
# # # #     try:
# # # #         for ex in ("squats", "pushups", "situps"):
# # # #             col = "best_" + ex
# # # #             r = (supabase.table("players").select("name," + col)
# # # #                  .gt(col, 0).order(col, desc=True).limit(10).execute())
# # # #             out["scores"][ex] = [{"name": row["name"], "value": row[col]} for row in r.data]
# # # #         w = (supabase.table("players").select("name,wins")
# # # #              .gt("wins", 0).order("wins", desc=True).limit(10).execute())
# # # #         out["wins"] = [{"name": row["name"], "value": row["wins"]} for row in w.data]
# # # #         return out
# # # #     except Exception as e:
# # # #         return {"ok": False, "error": str(e)}


# # # # if __name__ == "__main__":
# # # #     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# # # # Test 9----------------------------
# # # # import asyncio
# # # # import json
# # # # import random
# # # # import os
# # # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # # # import uvicorn

# # # # # --- Supabase connection (reads the env vars set on Render) ---
# # # # try:
# # # #     from supabase import create_client
# # # #     SUPABASE_URL = os.environ.get("project_url")
# # # #     SUPABASE_KEY = os.environ.get("service_role_key")
# # # #     supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None
# # # #     print("Supabase connected" if supabase else "Supabase env vars missing")
# # # # except Exception as e:
# # # #     supabase = None
# # # #     print("Supabase setup failed:", e)

# # # # DURATION = 35
# # # # # Code alphabet with no easily-confused characters (no O/0, I/1)
# # # # CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
# # # # CODE_LEN = 4

# # # # app = FastAPI()

# # # # # allow the browser (Netlify origin) to fetch the leaderboard over HTTP
# # # # from fastapi.middleware.cors import CORSMiddleware
# # # # app.add_middleware(
# # # #     CORSMiddleware,
# # # #     allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
# # # # )

# # # # # rooms: code -> {
# # # # #   "players": { websocket: {"id": "P1"/"P2", "reps": int, "ready": bool} },
# # # # #   "started": bool,
# # # # #   "task": asyncio.Task | None
# # # # # }
# # # # rooms = {}


# # # # def new_code():
# # # #     while True:
# # # #         c = "".join(random.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
# # # #         if c not in rooms:
# # # #             return c


# # # # async def send(ws, payload):
# # # #     try:
# # # #         await ws.send_text(json.dumps(payload))
# # # #     except Exception:
# # # #         pass


# # # # async def broadcast(room, payload):
# # # #     await asyncio.gather(
# # # #         *[send(ws, payload) for ws in list(room["players"].keys())],
# # # #         return_exceptions=True,
# # # #     )


# # # # def scores(room):
# # # #     return {p["id"]: p["reps"] for p in room["players"].values()}


# # # # # --- player identity (lightweight browser id + name, sent by the client) ---
# # # # ident = {}   # websocket -> {"pid": str, "name": str}

# # # # def remember(ws, data):
# # # #     ident[ws] = {"pid": (data.get("pid") or "anon"), "name": (data.get("name") or "Player")}

# # # # def pdict(ws, role):
# # # #     i = ident.get(ws, {})
# # # #     return {"id": role, "pid": i.get("pid", "anon"), "name": i.get("name", "Player"),
# # # #             "reps": 0, "ready": False}


# # # # # --- persistence: record a finished match + update player summaries ---
# # # # def record_match_sync(exercise, p1, p2, winner):
# # # #     if not supabase:
# # # #         return
# # # #     try:
# # # #         supabase.table("matches").insert({
# # # #             "exercise": exercise,
# # # #             "p1_id": p1["pid"], "p1_name": p1["name"], "p1_reps": p1["reps"],
# # # #             "p2_id": p2["pid"], "p2_name": p2["name"], "p2_reps": p2["reps"],
# # # #             "winner": "tie" if winner == "TIE" else ("p1" if winner == "P1" else "p2"),
# # # #         }).execute()
# # # #         _update_player(p1, exercise, won=(winner == "P1"), drew=(winner == "TIE"))
# # # #         _update_player(p2, exercise, won=(winner == "P2"), drew=(winner == "TIE"))
# # # #     except Exception as e:
# # # #         print("record_match failed:", e)

# # # # def _update_player(p, exercise, won, drew):
# # # #     pid = p.get("pid")
# # # #     if not pid or pid == "anon":
# # # #         return
# # # #     try:
# # # #         res = supabase.table("players").select("*").eq("id", pid).execute()
# # # #         row = res.data[0] if res.data else {}
# # # #         cur = (row.get("current_streak", 0) + 1) if won else 0
# # # #         payload = {
# # # #             "id": pid, "name": p.get("name", "Player"),
# # # #             "wins":   row.get("wins", 0)   + (1 if won else 0),
# # # #             "losses": row.get("losses", 0) + (0 if (won or drew) else 1),
# # # #             "draws":  row.get("draws", 0)  + (1 if drew else 0),
# # # #             "current_streak": cur,
# # # #             "best_streak": max(row.get("best_streak", 0), cur),
# # # #         }
# # # #         if exercise in ("squats", "pushups", "situps"):
# # # #             col = "best_" + exercise
# # # #             payload[col] = max(row.get(col, 0), p.get("reps", 0))
# # # #         supabase.table("players").upsert(payload).execute()
# # # #     except Exception as e:
# # # #         print("update_player failed:", e)


# # # # async def run_match(code):
# # # #     room = rooms.get(code)
# # # #     if not room:
# # # #         return

# # # #     room["started"] = True
# # # #     for p in room["players"].values():
# # # #         p["reps"] = 0
# # # #         p["ready"] = False

# # # #     print(f"[{code}] match starting")
# # # #     await broadcast(room, {"type": "start", "duration": DURATION,
# # # #                            "exercise": room.get("exercise", "squats")})

# # # #     await asyncio.sleep(DURATION)

# # # #     room = rooms.get(code)          # may have been torn down while we slept
# # # #     if not room:
# # # #         return

# # # #     s = scores(room)
# # # #     if len(s) == 2:
# # # #         p1, p2 = s.get("P1", 0), s.get("P2", 0)
# # # #         winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
# # # #     else:
# # # #         winner = "TIE"

# # # #     print(f"[{code}] match over {s} winner={winner}")
# # # #     await broadcast(room, {"type": "end", "winner": winner, "scores": s})

# # # #     # save the result to the database (in a thread so it never blocks the game)
# # # #     p1p = next((p for p in room["players"].values() if p["id"] == "P1"), None)
# # # #     p2p = next((p for p in room["players"].values() if p["id"] == "P2"), None)
# # # #     if p1p and p2p and len(s) == 2:
# # # #         asyncio.get_event_loop().run_in_executor(
# # # #             None, record_match_sync, room.get("exercise", "squats"),
# # # #             dict(p1p), dict(p2p), winner)

# # # #     room["started"] = False
# # # #     room["task"] = None


# # # # async def try_start(code):
# # # #     room = rooms.get(code)
# # # #     if room and len(room["players"]) == 2 and not room["started"]:
# # # #         room["task"] = asyncio.create_task(run_match(code))


# # # # LOBBY_SECS = 15   # pre-match ready-up + trash-talk window

# # # # async def start_lobby(code):
# # # #     room = rooms.get(code)
# # # #     if not room or room.get("started") or len(room["players"]) != 2:
# # # #         return
# # # #     room["in_lobby"] = True
# # # #     for p in room["players"].values():
# # # #         p["lobby_ready"] = False
# # # #     names = {p["id"]: p["name"] for p in room["players"].values()}
# # # #     await broadcast(room, {"type": "lobby", "duration": LOBBY_SECS, "names": names})
# # # #     room["lobby_task"] = asyncio.create_task(lobby_timer(code))

# # # # async def lobby_timer(code):
# # # #     try:
# # # #         await asyncio.sleep(LOBBY_SECS)
# # # #     except asyncio.CancelledError:
# # # #         return
# # # #     room = rooms.get(code)
# # # #     if room and room.get("in_lobby"):
# # # #         await begin_match(code)

# # # # async def begin_match(code):
# # # #     room = rooms.get(code)
# # # #     if not room or room.get("started"):
# # # #         return
# # # #     room["in_lobby"] = False
# # # #     t = room.get("lobby_task")
# # # #     if t:
# # # #         t.cancel()
# # # #     await try_start(code)


# # # # waiting = {}   # exercise -> list of websockets waiting for a random match


# # # # def room_of(ws):
# # # #     for c, room in rooms.items():
# # # #         if ws in room["players"]:
# # # #             return c, room
# # # #     return None, None


# # # # def enqueue(ws, exercise):
# # # #     waiting.setdefault(exercise, []).append(ws)


# # # # def dequeue(ws):
# # # #     for lst in waiting.values():
# # # #         if ws in lst:
# # # #             lst.remove(ws)


# # # # async def leave_room(ws):
# # # #     """Remove a player from the matchmaking queue and/or their room,
# # # #     and notify the opponent. Safe to call on explicit leave or disconnect."""
# # # #     dequeue(ws)
# # # #     ident.pop(ws, None)
# # # #     c, room = room_of(ws)
# # # #     if not room:
# # # #         return
# # # #     pid = room["players"][ws]["id"]
# # # #     del room["players"][ws]
# # # #     print(f"[{c}] {pid} left")
# # # #     task = room.get("task")
# # # #     if task:
# # # #         task.cancel()
# # # #     lt = room.get("lobby_task")
# # # #     if lt:
# # # #         lt.cancel()
# # # #     room["in_lobby"] = False
# # # #     if room["players"]:
# # # #         room["started"] = False
# # # #         for p in room["players"].values():
# # # #             p["ready"] = False
# # # #         await broadcast(room, {"type": "opponent_left"})
# # # #     else:
# # # #         del rooms[c]
# # # #         print(f"[{c}] closed")


# # # # @app.websocket("/")
# # # # async def referee(ws: WebSocket):
# # # #     await ws.accept()

# # # #     try:
# # # #         while True:
# # # #             raw = await ws.receive_text()
# # # #             data = json.loads(raw)
# # # #             t = data.get("type")

# # # #             # ---- create a private room ----
# # # #             if t == "create":
# # # #                 if room_of(ws)[1]:
# # # #                     continue
# # # #                 remember(ws, data)
# # # #                 code = new_code()
# # # #                 exercise = data.get("exercise", "squats")
# # # #                 rooms[code] = {
# # # #                     "players": {ws: pdict(ws, "P1")},
# # # #                     "started": False,
# # # #                     "task": None,
# # # #                     "exercise": exercise,
# # # #                 }
# # # #                 await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
# # # #                 print(f"[{code}] created ({exercise})")

# # # #             # ---- join a private room by code ----
# # # #             elif t == "join":
# # # #                 want = (data.get("code") or "").strip().upper()
# # # #                 room = rooms.get(want)
# # # #                 if not room:
# # # #                     await send(ws, {"type": "error", "reason": "no_room"})
# # # #                 elif len(room["players"]) >= 2:
# # # #                     await send(ws, {"type": "error", "reason": "room_full"})
# # # #                 else:
# # # #                     remember(ws, data)
# # # #                     room["players"][ws] = pdict(ws, "P2")
# # # #                     await send(ws, {"type": "joined", "you": "P2", "code": want,
# # # #                                     "exercise": room.get("exercise", "squats")})
# # # #                     await broadcast(room, {"type": "opponent_here"})
# # # #                     print(f"[{want}] P2 joined")
# # # #                     await start_lobby(want)

# # # #             # ---- quick match: pair with a waiting stranger (same exercise) ----
# # # #             elif t == "quick":
# # # #                 if room_of(ws)[1]:
# # # #                     continue
# # # #                 remember(ws, data)
# # # #                 exercise = data.get("exercise", "squats")
# # # #                 dequeue(ws)                       # never queue the same socket twice
# # # #                 q = waiting.get(exercise, [])
# # # #                 opponent = None
# # # #                 while q:                          # find a still-waiting opponent
# # # #                     cand = q.pop(0)
# # # #                     if cand is not ws:
# # # #                         opponent = cand
# # # #                         break
# # # #                 if opponent is not None:
# # # #                     code = new_code()
# # # #                     rooms[code] = {
# # # #                         "players": {opponent: pdict(opponent, "P1"),
# # # #                                     ws:       pdict(ws, "P2")},
# # # #                         "started": False,
# # # #                         "task": None,
# # # #                         "exercise": exercise,
# # # #                     }
# # # #                     await send(opponent, {"type": "matched", "you": "P1", "exercise": exercise})
# # # #                     await send(ws,       {"type": "matched", "you": "P2", "exercise": exercise})
# # # #                     print(f"[{code}] quick match ({exercise})")
# # # #                     await start_lobby(code)
# # # #                 else:
# # # #                     enqueue(ws, exercise)
# # # #                     await send(ws, {"type": "searching", "exercise": exercise})
# # # #                     print(f"[queue] {exercise}: {len(waiting.get(exercise, []))} waiting")

# # # #             # ---- cancel searching ----
# # # #             elif t == "cancel":
# # # #                 dequeue(ws)
# # # #                 await send(ws, {"type": "cancelled"})

# # # #             # ---- live rep updates ----
# # # #             elif t == "reps":
# # # #                 c, room = room_of(ws)
# # # #                 if room:
# # # #                     room["players"][ws]["reps"] = int(data.get("reps", 0))
# # # #                     await broadcast(room, {"type": "scores", "scores": scores(room)})

# # # #             # ---- rematch: both must ask before it restarts ----
# # # #             elif t == "rematch":
# # # #                 c, room = room_of(ws)
# # # #                 if room:
# # # #                     room["players"][ws]["ready"] = True
# # # #                     both_ready = (len(room["players"]) == 2 and
# # # #                                   all(p["ready"] for p in room["players"].values()))
# # # #                     if both_ready:
# # # #                         await try_start(c)
# # # #                     else:
# # # #                         for w in room["players"]:
# # # #                             if w is ws:
# # # #                                 await send(w, {"type": "rematch_pending"})
# # # #                             else:
# # # #                                 await send(w, {"type": "rematch_offer"})

# # # #             # ---- lobby: player hit READY (skip the timer if both are ready) ----
# # # #             elif t == "ready":
# # # #                 c, room = room_of(ws)
# # # #                 if room and room.get("in_lobby"):
# # # #                     room["players"][ws]["lobby_ready"] = True
# # # #                     await broadcast(room, {"type": "ready_state",
# # # #                                            "who": room["players"][ws]["id"]})
# # # #                     if (len(room["players"]) == 2 and
# # # #                             all(p.get("lobby_ready") for p in room["players"].values())):
# # # #                         await begin_match(c)

# # # #             # ---- lobby chat: relay a message to both players ----
# # # #             elif t == "chat":
# # # #                 c, room = room_of(ws)
# # # #                 if room:
# # # #                     txt = str(data.get("text", ""))[:200].strip()
# # # #                     if txt:
# # # #                         p = room["players"][ws]
# # # #                         await broadcast(room, {"type": "chat", "from": p["name"],
# # # #                                                "who": p["id"], "text": txt})

# # # #             # ---- explicit leave (reliable — doesn't wait for disconnect) ----
# # # #             elif t == "leave":
# # # #                 await leave_room(ws)

# # # #     except WebSocketDisconnect:
# # # #         pass
# # # #     except Exception as e:
# # # #         print("socket error:", e)

# # # #     finally:
# # # #         await leave_room(ws)


# # # # @app.get("/")
# # # # async def root():
# # # #     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# # # # @app.get("/dbtest")
# # # # async def dbtest():
# # # #     if not supabase:
# # # #         return {"ok": False, "error": "no supabase client (check env vars)"}
# # # #     try:
# # # #         supabase.table("pings").insert({"note": "hello from render"}).execute()
# # # #         rows = supabase.table("pings").select("*").order("created_at", desc=True).limit(3).execute()
# # # #         return {"ok": True, "recent_pings": rows.data}
# # # #     except Exception as e:
# # # #         return {"ok": False, "error": str(e)}


# # # # # sync def -> FastAPI runs it in a threadpool, so DB reads don't block the game loop
# # # # @app.get("/leaderboard")
# # # # def leaderboard():
# # # #     if not supabase:
# # # #         return {"ok": False, "error": "no db"}
# # # #     out = {"ok": True, "scores": {}, "wins": []}
# # # #     try:
# # # #         for ex in ("squats", "pushups", "situps"):
# # # #             col = "best_" + ex
# # # #             r = (supabase.table("players").select("name," + col)
# # # #                  .gt(col, 0).order(col, desc=True).limit(10).execute())
# # # #             out["scores"][ex] = [{"name": row["name"], "value": row[col]} for row in r.data]
# # # #         w = (supabase.table("players").select("name,wins")
# # # #              .gt("wins", 0).order("wins", desc=True).limit(10).execute())
# # # #         out["wins"] = [{"name": row["name"], "value": row["wins"]} for row in w.data]
# # # #         return out
# # # #     except Exception as e:
# # # #         return {"ok": False, "error": str(e)}


# # # # # ============================ DAILY TASKS ============================
# # # # # Three tasks a day, the SAME for everyone in the world, derived from the date.

# # # # import datetime, hashlib

# # # # DAILY_POOL = [
# # # #     ("squats",   [15, 20, 25, 30]),
# # # #     ("pushups",  [8, 10, 12, 15]),
# # # #     ("jacks",    [20, 25, 30, 40]),
# # # #     ("situps",   [10, 15, 20]),
# # # # ]
# # # # COINS_PER_TASK = 10
# # # # COINS_ALL_DONE = 25          # bonus for clearing all three


# # # # def todays_tasks(day: str):
# # # #     """Deterministic from the date -> everyone on earth gets the same 3 tasks."""
# # # #     seed = int(hashlib.sha256(day.encode()).hexdigest(), 16)
# # # #     picks, pool = [], list(DAILY_POOL)
# # # #     for i in range(3):
# # # #         ex, targets = pool.pop(seed % len(pool))
# # # #         seed //= max(1, len(pool) + 1)
# # # #         target = targets[seed % len(targets)]
# # # #         seed //= len(targets)
# # # #         picks.append({"idx": i, "exercise": ex, "target": target,
# # # #                       "coins": COINS_PER_TASK})
# # # #     return picks


# # # # @app.get("/daily")
# # # # def daily(pid: str = ""):
# # # #     day = datetime.date.today().isoformat()
# # # #     tasks = todays_tasks(day)
# # # #     out = {"ok": True, "day": day, "tasks": tasks, "done": [],
# # # #            "coins": 0, "streak": 0, "all_done": False}
# # # #     if not supabase or not pid:
# # # #         return out
# # # #     try:
# # # #         d = supabase.table("daily_done").select("task_idx") \
# # # #             .eq("pid", pid).eq("day", day).execute()
# # # #         out["done"] = sorted({r["task_idx"] for r in d.data})
# # # #         p = supabase.table("players").select("coins,daily_streak").eq("id", pid).execute()
# # # #         if p.data:
# # # #             out["coins"] = p.data[0].get("coins") or 0
# # # #             out["streak"] = p.data[0].get("daily_streak") or 0
# # # #         out["all_done"] = len(out["done"]) >= 3
# # # #         return out
# # # #     except Exception as e:
# # # #         out["error"] = str(e)
# # # #         return out


# # # # @app.post("/daily/complete")
# # # # def daily_complete(payload: dict):
# # # #     """Body: {pid, name, task_idx, exercise, reps}"""
# # # #     if not supabase:
# # # #         return {"ok": False, "error": "no db"}
# # # #     pid = (payload.get("pid") or "").strip()
# # # #     if not pid:
# # # #         return {"ok": False, "error": "no pid"}
# # # #     day = datetime.date.today().isoformat()
# # # #     tasks = todays_tasks(day)
# # # #     try:
# # # #         idx = int(payload.get("task_idx", -1))
# # # #         task = next((t for t in tasks if t["idx"] == idx), None)
# # # #         if not task:
# # # #             return {"ok": False, "error": "bad task"}
# # # #         reps = int(payload.get("reps", 0))
# # # #         # server-side sanity: must actually hit the target
# # # #         if reps < task["target"]:
# # # #             return {"ok": False, "error": "target not met"}

# # # #         # already done today? (unique constraint also protects us)
# # # #         prev = supabase.table("daily_done").select("task_idx") \
# # # #             .eq("pid", pid).eq("day", day).execute()
# # # #         done_idx = {r["task_idx"] for r in prev.data}
# # # #         if idx in done_idx:
# # # #             return {"ok": True, "already": True}

# # # #         supabase.table("daily_done").insert({
# # # #             "pid": pid, "day": day, "task_idx": idx,
# # # #             "exercise": task["exercise"], "reps": reps}).execute()
# # # #         done_idx.add(idx)

# # # #         # ---- coins + streak ----
# # # #         row = supabase.table("players").select("*").eq("id", pid).execute()
# # # #         p = row.data[0] if row.data else {}
# # # #         coins = (p.get("coins") or 0) + COINS_PER_TASK
# # # #         streak = p.get("daily_streak") or 0
# # # #         best = p.get("best_daily_streak") or 0
# # # #         last = p.get("last_daily")
# # # #         all_done = len(done_idx) >= 3

# # # #         if all_done:
# # # #             coins += COINS_ALL_DONE
# # # #             yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
# # # #             if last == day:
# # # #                 pass                      # streak already counted today
# # # #             elif last == yesterday:
# # # #                 streak += 1
# # # #             else:
# # # #                 streak = 1
# # # #             best = max(best, streak)

# # # #         upd = {"id": pid, "name": payload.get("name") or p.get("name") or "Player",
# # # #                "coins": coins, "daily_streak": streak, "best_daily_streak": best}
# # # #         if all_done:
# # # #             upd["last_daily"] = day
# # # #         supabase.table("players").upsert(upd).execute()

# # # #         return {"ok": True, "coins": coins, "streak": streak,
# # # #                 "all_done": all_done, "done": sorted(done_idx),
# # # #                 "earned": COINS_PER_TASK + (COINS_ALL_DONE if all_done else 0)}
# # # #     except Exception as e:
# # # #         return {"ok": False, "error": str(e)}


# # # # if __name__ == "__main__":
# # # #     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# # # # Test 10----------------------------
# # # import asyncio
# # # import json
# # # import random
# # # import os
# # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # # import uvicorn

# # # # --- Supabase connection (reads the env vars set on Render) ---
# # # try:
# # #     from supabase import create_client
# # #     SUPABASE_URL = os.environ.get("project_url")
# # #     SUPABASE_KEY = os.environ.get("service_role_key")
# # #     supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None
# # #     print("Supabase connected" if supabase else "Supabase env vars missing")
# # # except Exception as e:
# # #     supabase = None
# # #     print("Supabase setup failed:", e)

# # # DURATION = 35
# # # PLANK_MAX = 300     # safety cap for Plank Chicken (5 min) so a match can't run forever
# # # # Code alphabet with no easily-confused characters (no O/0, I/1)
# # # CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
# # # CODE_LEN = 4

# # # app = FastAPI()

# # # # allow the browser (Netlify origin) to fetch the leaderboard over HTTP
# # # from fastapi.middleware.cors import CORSMiddleware
# # # app.add_middleware(
# # #     CORSMiddleware,
# # #     allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
# # # )

# # # # rooms: code -> {
# # # #   "players": { websocket: {"id": "P1"/"P2", "reps": int, "ready": bool} },
# # # #   "started": bool,
# # # #   "task": asyncio.Task | None
# # # # }
# # # rooms = {}


# # # def new_code():
# # #     while True:
# # #         c = "".join(random.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
# # #         if c not in rooms:
# # #             return c


# # # async def send(ws, payload):
# # #     try:
# # #         await ws.send_text(json.dumps(payload))
# # #     except Exception:
# # #         pass


# # # async def broadcast(room, payload):
# # #     await asyncio.gather(
# # #         *[send(ws, payload) for ws in list(room["players"].keys())],
# # #         return_exceptions=True,
# # #     )


# # # def scores(room):
# # #     return {p["id"]: p["reps"] for p in room["players"].values()}


# # # # --- player identity (lightweight browser id + name, sent by the client) ---
# # # ident = {}   # websocket -> {"pid": str, "name": str}

# # # def remember(ws, data):
# # #     ident[ws] = {"pid": (data.get("pid") or "anon"), "name": (data.get("name") or "Player")}

# # # def pdict(ws, role):
# # #     i = ident.get(ws, {})
# # #     return {"id": role, "pid": i.get("pid", "anon"), "name": i.get("name", "Player"),
# # #             "reps": 0, "ready": False}


# # # # --- persistence: record a finished match + update player summaries ---
# # # def record_match_sync(exercise, p1, p2, winner):
# # #     if not supabase:
# # #         return
# # #     try:
# # #         supabase.table("matches").insert({
# # #             "exercise": exercise,
# # #             "p1_id": p1["pid"], "p1_name": p1["name"], "p1_reps": p1["reps"],
# # #             "p2_id": p2["pid"], "p2_name": p2["name"], "p2_reps": p2["reps"],
# # #             "winner": "tie" if winner == "TIE" else ("p1" if winner == "P1" else "p2"),
# # #         }).execute()
# # #         _update_player(p1, exercise, won=(winner == "P1"), drew=(winner == "TIE"))
# # #         _update_player(p2, exercise, won=(winner == "P2"), drew=(winner == "TIE"))
# # #     except Exception as e:
# # #         print("record_match failed:", e)

# # # def _update_player(p, exercise, won, drew):
# # #     pid = p.get("pid")
# # #     if not pid or pid == "anon":
# # #         return
# # #     try:
# # #         res = supabase.table("players").select("*").eq("id", pid).execute()
# # #         row = res.data[0] if res.data else {}
# # #         cur = (row.get("current_streak", 0) + 1) if won else 0
# # #         payload = {
# # #             "id": pid, "name": p.get("name", "Player"),
# # #             "wins":   row.get("wins", 0)   + (1 if won else 0),
# # #             "losses": row.get("losses", 0) + (0 if (won or drew) else 1),
# # #             "draws":  row.get("draws", 0)  + (1 if drew else 0),
# # #             "current_streak": cur,
# # #             "best_streak": max(row.get("best_streak", 0), cur),
# # #         }
# # #         if exercise in ("squats", "pushups", "situps", "jacks", "plank"):
# # #             col = "best_" + exercise
# # #             payload[col] = max(row.get(col, 0), p.get("reps", 0))
# # #         supabase.table("players").upsert(payload).execute()
# # #     except Exception as e:
# # #         print("update_player failed:", e)


# # # async def run_match(code):
# # #     room = rooms.get(code)
# # #     if not room:
# # #         return

# # #     room["started"] = True
# # #     for p in room["players"].values():
# # #         p["reps"] = 0
# # #         p["ready"] = False

# # #     ex = room.get("exercise", "squats")
# # #     is_plank = (ex == "plank")
# # #     for p in room["players"].values():
# # #         p["broke"] = False

# # #     print(f"[{code}] match starting ({ex})")
# # #     await broadcast(room, {"type": "start",
# # #                            "duration": (PLANK_MAX if is_plank else DURATION),
# # #                            "mode": ("hold" if is_plank else "reps"),
# # #                            "exercise": ex})

# # #     if is_plank:
# # #         # PLANK CHICKEN: no countdown. Hold until someone's form breaks.
# # #         # The first to break loses. A safety cap stops an eternal match.
# # #         waited = 0.0
# # #         while waited < PLANK_MAX:
# # #             await asyncio.sleep(0.2)
# # #             waited += 0.2
# # #             room = rooms.get(code)
# # #             if not room or len(room["players"]) < 2:
# # #                 return
# # #             broken = [p for p in room["players"].values() if p.get("broke")]
# # #             if broken:
# # #                 break
# # #     else:
# # #         await asyncio.sleep(DURATION)

# # #     room = rooms.get(code)          # may have been torn down while we slept
# # #     if not room:
# # #         return

# # #     s = scores(room)
# # #     if is_plank:
# # #         broken = [p for p in room["players"].values() if p.get("broke")]
# # #         if len(broken) == 1:
# # #             loser = broken[0]["id"]
# # #             winner = "P2" if loser == "P1" else "P1"
# # #         elif len(broken) >= 2:
# # #             winner = "TIE"                       # both cracked in the same instant
# # #         else:
# # #             # hit the safety cap with both still holding -> longest hold wins
# # #             p1, p2 = s.get("P1", 0), s.get("P2", 0)
# # #             winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
# # #     elif len(s) == 2:
# # #         p1, p2 = s.get("P1", 0), s.get("P2", 0)
# # #         winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
# # #     else:
# # #         winner = "TIE"

# # #     print(f"[{code}] match over {s} winner={winner}")
# # #     await broadcast(room, {"type": "end", "winner": winner, "scores": s})

# # #     # save the result to the database (in a thread so it never blocks the game)
# # #     p1p = next((p for p in room["players"].values() if p["id"] == "P1"), None)
# # #     p2p = next((p for p in room["players"].values() if p["id"] == "P2"), None)
# # #     if p1p and p2p and len(s) == 2:
# # #         asyncio.get_event_loop().run_in_executor(
# # #             None, record_match_sync, room.get("exercise", "squats"),
# # #             dict(p1p), dict(p2p), winner)

# # #     room["started"] = False
# # #     room["task"] = None


# # # async def try_start(code):
# # #     room = rooms.get(code)
# # #     if room and len(room["players"]) == 2 and not room["started"]:
# # #         room["task"] = asyncio.create_task(run_match(code))


# # # LOBBY_SECS = 15   # pre-match ready-up + trash-talk window

# # # async def start_lobby(code):
# # #     room = rooms.get(code)
# # #     if not room or room.get("started") or len(room["players"]) != 2:
# # #         return
# # #     room["in_lobby"] = True
# # #     for p in room["players"].values():
# # #         p["lobby_ready"] = False
# # #     names = {p["id"]: p["name"] for p in room["players"].values()}
# # #     await broadcast(room, {"type": "lobby", "duration": LOBBY_SECS, "names": names})
# # #     room["lobby_task"] = asyncio.create_task(lobby_timer(code))

# # # async def lobby_timer(code):
# # #     try:
# # #         await asyncio.sleep(LOBBY_SECS)
# # #     except asyncio.CancelledError:
# # #         return
# # #     room = rooms.get(code)
# # #     if room and room.get("in_lobby"):
# # #         await begin_match(code)

# # # async def begin_match(code):
# # #     room = rooms.get(code)
# # #     if not room or room.get("started"):
# # #         return
# # #     room["in_lobby"] = False
# # #     t = room.get("lobby_task")
# # #     if t:
# # #         t.cancel()
# # #     await try_start(code)


# # # waiting = {}   # exercise -> list of websockets waiting for a random match


# # # def room_of(ws):
# # #     for c, room in rooms.items():
# # #         if ws in room["players"]:
# # #             return c, room
# # #     return None, None


# # # def enqueue(ws, exercise):
# # #     waiting.setdefault(exercise, []).append(ws)


# # # def dequeue(ws):
# # #     for lst in waiting.values():
# # #         if ws in lst:
# # #             lst.remove(ws)


# # # async def leave_room(ws):
# # #     """Remove a player from the matchmaking queue and/or their room,
# # #     and notify the opponent. Safe to call on explicit leave or disconnect."""
# # #     dequeue(ws)
# # #     ident.pop(ws, None)
# # #     c, room = room_of(ws)
# # #     if not room:
# # #         return
# # #     pid = room["players"][ws]["id"]
# # #     del room["players"][ws]
# # #     print(f"[{c}] {pid} left")
# # #     task = room.get("task")
# # #     if task:
# # #         task.cancel()
# # #     lt = room.get("lobby_task")
# # #     if lt:
# # #         lt.cancel()
# # #     room["in_lobby"] = False
# # #     if room["players"]:
# # #         room["started"] = False
# # #         for p in room["players"].values():
# # #             p["ready"] = False
# # #         await broadcast(room, {"type": "opponent_left"})
# # #     else:
# # #         del rooms[c]
# # #         print(f"[{c}] closed")


# # # @app.websocket("/")
# # # async def referee(ws: WebSocket):
# # #     await ws.accept()

# # #     try:
# # #         while True:
# # #             raw = await ws.receive_text()
# # #             data = json.loads(raw)
# # #             t = data.get("type")

# # #             # ---- create a private room ----
# # #             if t == "create":
# # #                 if room_of(ws)[1]:
# # #                     continue
# # #                 remember(ws, data)
# # #                 code = new_code()
# # #                 exercise = data.get("exercise", "squats")
# # #                 rooms[code] = {
# # #                     "players": {ws: pdict(ws, "P1")},
# # #                     "started": False,
# # #                     "task": None,
# # #                     "exercise": exercise,
# # #                 }
# # #                 await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
# # #                 print(f"[{code}] created ({exercise})")

# # #             # ---- join a private room by code ----
# # #             elif t == "join":
# # #                 want = (data.get("code") or "").strip().upper()
# # #                 room = rooms.get(want)
# # #                 if not room:
# # #                     await send(ws, {"type": "error", "reason": "no_room"})
# # #                 elif len(room["players"]) >= 2:
# # #                     await send(ws, {"type": "error", "reason": "room_full"})
# # #                 else:
# # #                     remember(ws, data)
# # #                     room["players"][ws] = pdict(ws, "P2")
# # #                     await send(ws, {"type": "joined", "you": "P2", "code": want,
# # #                                     "exercise": room.get("exercise", "squats")})
# # #                     await broadcast(room, {"type": "opponent_here"})
# # #                     print(f"[{want}] P2 joined")
# # #                     await start_lobby(want)

# # #             # ---- quick match: pair with a waiting stranger (same exercise) ----
# # #             elif t == "quick":
# # #                 if room_of(ws)[1]:
# # #                     continue
# # #                 remember(ws, data)
# # #                 exercise = data.get("exercise", "squats")
# # #                 dequeue(ws)                       # never queue the same socket twice
# # #                 q = waiting.get(exercise, [])
# # #                 opponent = None
# # #                 while q:                          # find a still-waiting opponent
# # #                     cand = q.pop(0)
# # #                     if cand is not ws:
# # #                         opponent = cand
# # #                         break
# # #                 if opponent is not None:
# # #                     code = new_code()
# # #                     rooms[code] = {
# # #                         "players": {opponent: pdict(opponent, "P1"),
# # #                                     ws:       pdict(ws, "P2")},
# # #                         "started": False,
# # #                         "task": None,
# # #                         "exercise": exercise,
# # #                     }
# # #                     await send(opponent, {"type": "matched", "you": "P1", "exercise": exercise})
# # #                     await send(ws,       {"type": "matched", "you": "P2", "exercise": exercise})
# # #                     print(f"[{code}] quick match ({exercise})")
# # #                     await start_lobby(code)
# # #                 else:
# # #                     enqueue(ws, exercise)
# # #                     await send(ws, {"type": "searching", "exercise": exercise})
# # #                     print(f"[queue] {exercise}: {len(waiting.get(exercise, []))} waiting")

# # #             # ---- cancel searching ----
# # #             elif t == "cancel":
# # #                 dequeue(ws)
# # #                 await send(ws, {"type": "cancelled"})

# # #             # ---- live rep updates ----
# # #             elif t == "reps":
# # #                 c, room = room_of(ws)
# # #                 if room:
# # #                     room["players"][ws]["reps"] = int(data.get("reps", 0))
# # #                     await broadcast(room, {"type": "scores", "scores": scores(room)})

# # #             # ---- rematch: both must ask before it restarts ----
# # #             elif t == "rematch":
# # #                 c, room = room_of(ws)
# # #                 if room:
# # #                     room["players"][ws]["ready"] = True
# # #                     both_ready = (len(room["players"]) == 2 and
# # #                                   all(p["ready"] for p in room["players"].values()))
# # #                     if both_ready:
# # #                         await try_start(c)
# # #                     else:
# # #                         for w in room["players"]:
# # #                             if w is ws:
# # #                                 await send(w, {"type": "rematch_pending"})
# # #                             else:
# # #                                 await send(w, {"type": "rematch_offer"})

# # #             # ---- plank chicken: this player's form broke ----
# # #             elif t == "broke":
# # #                 c, room = room_of(ws)
# # #                 if room and room.get("started"):
# # #                     room["players"][ws]["broke"] = True
# # #                     print(f"[{c}] {room['players'][ws]['id']} broke form")

# # #             # ---- lobby: player hit READY (skip the timer if both are ready) ----
# # #             elif t == "ready":
# # #                 c, room = room_of(ws)
# # #                 if room and room.get("in_lobby"):
# # #                     room["players"][ws]["lobby_ready"] = True
# # #                     await broadcast(room, {"type": "ready_state",
# # #                                            "who": room["players"][ws]["id"]})
# # #                     if (len(room["players"]) == 2 and
# # #                             all(p.get("lobby_ready") for p in room["players"].values())):
# # #                         await begin_match(c)

# # #             # ---- lobby chat: relay a message to both players ----
# # #             elif t == "chat":
# # #                 c, room = room_of(ws)
# # #                 if room:
# # #                     txt = str(data.get("text", ""))[:200].strip()
# # #                     if txt:
# # #                         p = room["players"][ws]
# # #                         await broadcast(room, {"type": "chat", "from": p["name"],
# # #                                                "who": p["id"], "text": txt})

# # #             # ---- explicit leave (reliable — doesn't wait for disconnect) ----
# # #             elif t == "leave":
# # #                 await leave_room(ws)

# # #     except WebSocketDisconnect:
# # #         pass
# # #     except Exception as e:
# # #         print("socket error:", e)

# # #     finally:
# # #         await leave_room(ws)


# # # @app.get("/")
# # # async def root():
# # #     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# # # @app.get("/dbtest")
# # # async def dbtest():
# # #     if not supabase:
# # #         return {"ok": False, "error": "no supabase client (check env vars)"}
# # #     try:
# # #         supabase.table("pings").insert({"note": "hello from render"}).execute()
# # #         rows = supabase.table("pings").select("*").order("created_at", desc=True).limit(3).execute()
# # #         return {"ok": True, "recent_pings": rows.data}
# # #     except Exception as e:
# # #         return {"ok": False, "error": str(e)}


# # # # sync def -> FastAPI runs it in a threadpool, so DB reads don't block the game loop
# # # @app.get("/leaderboard")
# # # def leaderboard():
# # #     if not supabase:
# # #         return {"ok": False, "error": "no db"}
# # #     out = {"ok": True, "scores": {}, "wins": []}
# # #     try:
# # #         for ex in ("squats", "pushups", "situps"):
# # #             col = "best_" + ex
# # #             r = (supabase.table("players").select("name," + col)
# # #                  .gt(col, 0).order(col, desc=True).limit(10).execute())
# # #             out["scores"][ex] = [{"name": row["name"], "value": row[col]} for row in r.data]
# # #         w = (supabase.table("players").select("name,wins")
# # #              .gt("wins", 0).order("wins", desc=True).limit(10).execute())
# # #         out["wins"] = [{"name": row["name"], "value": row["wins"]} for row in w.data]
# # #         return out
# # #     except Exception as e:
# # #         return {"ok": False, "error": str(e)}


# # # # ============================ DAILY TASKS ============================
# # # # Three tasks a day, the SAME for everyone in the world, derived from the date.

# # # import datetime, hashlib

# # # DAILY_POOL = [
# # #     ("squats",   [15, 20, 25, 30]),
# # #     ("pushups",  [8, 10, 12, 15]),
# # #     ("jacks",    [20, 25, 30, 40]),
# # #     ("situps",   [10, 15, 20]),
# # #     ("plank",    [30, 45, 60]),        # seconds held, not reps
# # # ]
# # # COINS_PER_TASK = 10
# # # COINS_ALL_DONE = 25          # bonus for clearing all three


# # # def todays_tasks(day: str):
# # #     """Deterministic from the date -> everyone on earth gets the same 3 tasks."""
# # #     seed = int(hashlib.sha256(day.encode()).hexdigest(), 16)
# # #     picks, pool = [], list(DAILY_POOL)
# # #     for i in range(3):
# # #         ex, targets = pool.pop(seed % len(pool))
# # #         seed //= max(1, len(pool) + 1)
# # #         target = targets[seed % len(targets)]
# # #         seed //= len(targets)
# # #         picks.append({"idx": i, "exercise": ex, "target": target,
# # #                       "coins": COINS_PER_TASK})
# # #     return picks


# # # @app.get("/daily")
# # # def daily(pid: str = ""):
# # #     day = datetime.date.today().isoformat()
# # #     tasks = todays_tasks(day)
# # #     out = {"ok": True, "day": day, "tasks": tasks, "done": [],
# # #            "coins": 0, "streak": 0, "all_done": False}
# # #     if not supabase or not pid:
# # #         return out
# # #     try:
# # #         d = supabase.table("daily_done").select("task_idx") \
# # #             .eq("pid", pid).eq("day", day).execute()
# # #         out["done"] = sorted({r["task_idx"] for r in d.data})
# # #         p = supabase.table("players").select("coins,daily_streak").eq("id", pid).execute()
# # #         if p.data:
# # #             out["coins"] = p.data[0].get("coins") or 0
# # #             out["streak"] = p.data[0].get("daily_streak") or 0
# # #         out["all_done"] = len(out["done"]) >= 3
# # #         return out
# # #     except Exception as e:
# # #         out["error"] = str(e)
# # #         return out


# # # @app.post("/daily/complete")
# # # def daily_complete(payload: dict):
# # #     """Body: {pid, name, task_idx, exercise, reps}"""
# # #     if not supabase:
# # #         return {"ok": False, "error": "no db"}
# # #     pid = (payload.get("pid") or "").strip()
# # #     if not pid:
# # #         return {"ok": False, "error": "no pid"}
# # #     day = datetime.date.today().isoformat()
# # #     tasks = todays_tasks(day)
# # #     try:
# # #         idx = int(payload.get("task_idx", -1))
# # #         task = next((t for t in tasks if t["idx"] == idx), None)
# # #         if not task:
# # #             return {"ok": False, "error": "bad task"}
# # #         reps = int(payload.get("reps", 0))
# # #         # server-side sanity: must actually hit the target
# # #         if reps < task["target"]:
# # #             return {"ok": False, "error": "target not met"}

# # #         # already done today? (unique constraint also protects us)
# # #         prev = supabase.table("daily_done").select("task_idx") \
# # #             .eq("pid", pid).eq("day", day).execute()
# # #         done_idx = {r["task_idx"] for r in prev.data}
# # #         if idx in done_idx:
# # #             return {"ok": True, "already": True}

# # #         supabase.table("daily_done").insert({
# # #             "pid": pid, "day": day, "task_idx": idx,
# # #             "exercise": task["exercise"], "reps": reps}).execute()
# # #         done_idx.add(idx)

# # #         # ---- coins + streak ----
# # #         row = supabase.table("players").select("*").eq("id", pid).execute()
# # #         p = row.data[0] if row.data else {}
# # #         coins = (p.get("coins") or 0) + COINS_PER_TASK
# # #         streak = p.get("daily_streak") or 0
# # #         best = p.get("best_daily_streak") or 0
# # #         last = p.get("last_daily")
# # #         all_done = len(done_idx) >= 3

# # #         if all_done:
# # #             coins += COINS_ALL_DONE
# # #             yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
# # #             if last == day:
# # #                 pass                      # streak already counted today
# # #             elif last == yesterday:
# # #                 streak += 1
# # #             else:
# # #                 streak = 1
# # #             best = max(best, streak)

# # #         upd = {"id": pid, "name": payload.get("name") or p.get("name") or "Player",
# # #                "coins": coins, "daily_streak": streak, "best_daily_streak": best}
# # #         if all_done:
# # #             upd["last_daily"] = day
# # #         supabase.table("players").upsert(upd).execute()

# # #         return {"ok": True, "coins": coins, "streak": streak,
# # #                 "all_done": all_done, "done": sorted(done_idx),
# # #                 "earned": COINS_PER_TASK + (COINS_ALL_DONE if all_done else 0)}
# # #     except Exception as e:
# # #         return {"ok": False, "error": str(e)}


# # # if __name__ == "__main__":
# # #     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# # # test 11--------------------------------
# # import asyncio
# # import json
# # import random
# # import os
# # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # import uvicorn

# # # --- Supabase connection (reads the env vars set on Render) ---
# # try:
# #     from supabase import create_client
# #     SUPABASE_URL = os.environ.get("project_url")
# #     SUPABASE_KEY = os.environ.get("service_role_key")
# #     supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None
# #     print("Supabase connected" if supabase else "Supabase env vars missing")
# # except Exception as e:
# #     supabase = None
# #     print("Supabase setup failed:", e)

# # DURATION = 35
# # PLANK_MAX = 300     # safety cap for Plank Chicken (5 min) so a match can't run forever
# # # Code alphabet with no easily-confused characters (no O/0, I/1)
# # CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
# # CODE_LEN = 4

# # app = FastAPI()

# # # allow the browser (Netlify origin) to fetch the leaderboard over HTTP
# # from fastapi.middleware.cors import CORSMiddleware
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
# # )

# # # rooms: code -> {
# # #   "players": { websocket: {"id": "P1"/"P2", "reps": int, "ready": bool} },
# # #   "started": bool,
# # #   "task": asyncio.Task | None
# # # }
# # rooms = {}


# # def new_code():
# #     while True:
# #         c = "".join(random.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
# #         if c not in rooms:
# #             return c


# # async def send(ws, payload):
# #     try:
# #         await ws.send_text(json.dumps(payload))
# #     except Exception:
# #         pass


# # async def broadcast(room, payload):
# #     await asyncio.gather(
# #         *[send(ws, payload) for ws in list(room["players"].keys())],
# #         return_exceptions=True,
# #     )


# # def scores(room):
# #     return {p["id"]: p["reps"] for p in room["players"].values()}


# # # --- player identity (lightweight browser id + name, sent by the client) ---
# # ident = {}   # websocket -> {"pid": str, "name": str}

# # def remember(ws, data):
# #     ident[ws] = {"pid": (data.get("pid") or "anon"), "name": (data.get("name") or "Player")}

# # def pdict(ws, role):
# #     i = ident.get(ws, {})
# #     return {"id": role, "pid": i.get("pid", "anon"), "name": i.get("name", "Player"),
# #             "reps": 0, "ready": False}


# # # --- persistence: record a finished match + update player summaries ---
# # def record_match_sync(exercise, p1, p2, winner):
# #     if not supabase:
# #         return
# #     try:
# #         supabase.table("matches").insert({
# #             "exercise": exercise,
# #             "p1_id": p1["pid"], "p1_name": p1["name"], "p1_reps": p1["reps"],
# #             "p2_id": p2["pid"], "p2_name": p2["name"], "p2_reps": p2["reps"],
# #             "winner": "tie" if winner == "TIE" else ("p1" if winner == "P1" else "p2"),
# #         }).execute()
# #         _update_player(p1, exercise, won=(winner == "P1"), drew=(winner == "TIE"))
# #         _update_player(p2, exercise, won=(winner == "P2"), drew=(winner == "TIE"))
# #     except Exception as e:
# #         print("record_match failed:", e)

# # def _update_player(p, exercise, won, drew):
# #     pid = p.get("pid")
# #     if not pid or pid == "anon":
# #         return
# #     try:
# #         res = supabase.table("players").select("*").eq("id", pid).execute()
# #         row = res.data[0] if res.data else {}
# #         cur = (row.get("current_streak", 0) + 1) if won else 0
# #         payload = {
# #             "id": pid, "name": p.get("name", "Player"),
# #             "wins":   row.get("wins", 0)   + (1 if won else 0),
# #             "losses": row.get("losses", 0) + (0 if (won or drew) else 1),
# #             "draws":  row.get("draws", 0)  + (1 if drew else 0),
# #             "current_streak": cur,
# #             "best_streak": max(row.get("best_streak", 0), cur),
# #         }
# #         if exercise in ("squats", "pushups", "situps", "jacks", "plank"):
# #             col = "best_" + exercise
# #             payload[col] = max(row.get(col, 0), p.get("reps", 0))
# #         supabase.table("players").upsert(payload).execute()
# #     except Exception as e:
# #         print("update_player failed:", e)


# # async def run_match(code):
# #     room = rooms.get(code)
# #     if not room:
# #         return

# #     room["started"] = True
# #     for p in room["players"].values():
# #         p["reps"] = 0
# #         p["ready"] = False

# #     ex = room.get("exercise", "squats")
# #     is_plank = (ex == "plank")
# #     for p in room["players"].values():
# #         p["broke"] = False

# #     print(f"[{code}] match starting ({ex})")
# #     await broadcast(room, {"type": "start",
# #                            "duration": (PLANK_MAX if is_plank else DURATION),
# #                            "mode": ("hold" if is_plank else "reps"),
# #                            "exercise": ex})

# #     if is_plank:
# #         # PLANK CHICKEN
# #         # Phase 1: wait for BOTH players to get into a plank ("ready").
# #         # Phase 2: a synced 5s countdown — both must stay in position.
# #         # Phase 3: LIVE — first to drop loses.
# #         for p in room["players"].values():
# #             p["ready"] = False
# #             p["broke"] = False

# #         waited = 0.0
# #         while waited < 60:                      # up to 60s to both get into position
# #             await asyncio.sleep(0.15); waited += 0.15
# #             room = rooms.get(code)
# #             if not room or len(room["players"]) < 2: return
# #             if all(p.get("ready") for p in room["players"].values()):
# #                 break

# #         # synced countdown
# #         await broadcast(room, {"type": "plank_go", "count": 5})
# #         for n in range(5, 0, -1):
# #             await asyncio.sleep(1.0)
# #             room = rooms.get(code)
# #             if not room or len(room["players"]) < 2: return

# #         await broadcast(room, {"type": "plank_live"})   # NOW it counts
# #         for p in room["players"].values():
# #             p["broke"] = False                          # ignore any drops before this

# #         waited = 0.0
# #         while waited < PLANK_MAX:
# #             await asyncio.sleep(0.15); waited += 0.15
# #             room = rooms.get(code)
# #             if not room or len(room["players"]) < 2: return
# #             if any(p.get("broke") for p in room["players"].values()):
# #                 break
# #     else:
# #         await asyncio.sleep(DURATION)

# #     room = rooms.get(code)          # may have been torn down while we slept
# #     if not room:
# #         return

# #     s = scores(room)
# #     if is_plank:
# #         broken = [p for p in room["players"].values() if p.get("broke")]
# #         if len(broken) == 1:
# #             loser = broken[0]["id"]
# #             winner = "P2" if loser == "P1" else "P1"
# #         elif len(broken) >= 2:
# #             winner = "TIE"                       # both cracked in the same instant
# #         else:
# #             # hit the safety cap with both still holding -> longest hold wins
# #             p1, p2 = s.get("P1", 0), s.get("P2", 0)
# #             winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
# #     elif len(s) == 2:
# #         p1, p2 = s.get("P1", 0), s.get("P2", 0)
# #         winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
# #     else:
# #         winner = "TIE"

# #     print(f"[{code}] match over {s} winner={winner}")
# #     await broadcast(room, {"type": "end", "winner": winner, "scores": s})

# #     # save the result to the database (in a thread so it never blocks the game)
# #     p1p = next((p for p in room["players"].values() if p["id"] == "P1"), None)
# #     p2p = next((p for p in room["players"].values() if p["id"] == "P2"), None)
# #     if p1p and p2p and len(s) == 2:
# #         asyncio.get_event_loop().run_in_executor(
# #             None, record_match_sync, room.get("exercise", "squats"),
# #             dict(p1p), dict(p2p), winner)

# #     room["started"] = False
# #     room["task"] = None


# # async def try_start(code):
# #     room = rooms.get(code)
# #     if room and len(room["players"]) == 2 and not room["started"]:
# #         room["task"] = asyncio.create_task(run_match(code))


# # LOBBY_SECS = 15   # pre-match ready-up + trash-talk window

# # async def start_lobby(code):
# #     room = rooms.get(code)
# #     if not room or room.get("started") or len(room["players"]) != 2:
# #         return
# #     room["in_lobby"] = True
# #     for p in room["players"].values():
# #         p["lobby_ready"] = False
# #     names = {p["id"]: p["name"] for p in room["players"].values()}
# #     await broadcast(room, {"type": "lobby", "duration": LOBBY_SECS, "names": names})
# #     room["lobby_task"] = asyncio.create_task(lobby_timer(code))

# # async def lobby_timer(code):
# #     try:
# #         await asyncio.sleep(LOBBY_SECS)
# #     except asyncio.CancelledError:
# #         return
# #     room = rooms.get(code)
# #     if room and room.get("in_lobby"):
# #         await begin_match(code)

# # async def begin_match(code):
# #     room = rooms.get(code)
# #     if not room or room.get("started"):
# #         return
# #     room["in_lobby"] = False
# #     t = room.get("lobby_task")
# #     if t:
# #         t.cancel()
# #     await try_start(code)


# # waiting = {}   # exercise -> list of websockets waiting for a random match


# # def room_of(ws):
# #     for c, room in rooms.items():
# #         if ws in room["players"]:
# #             return c, room
# #     return None, None


# # def enqueue(ws, exercise):
# #     waiting.setdefault(exercise, []).append(ws)


# # def dequeue(ws):
# #     for lst in waiting.values():
# #         if ws in lst:
# #             lst.remove(ws)


# # async def leave_room(ws):
# #     """Remove a player from the matchmaking queue and/or their room,
# #     and notify the opponent. Safe to call on explicit leave or disconnect."""
# #     dequeue(ws)
# #     ident.pop(ws, None)
# #     c, room = room_of(ws)
# #     if not room:
# #         return
# #     pid = room["players"][ws]["id"]
# #     del room["players"][ws]
# #     print(f"[{c}] {pid} left")
# #     task = room.get("task")
# #     if task:
# #         task.cancel()
# #     lt = room.get("lobby_task")
# #     if lt:
# #         lt.cancel()
# #     room["in_lobby"] = False
# #     if room["players"]:
# #         room["started"] = False
# #         for p in room["players"].values():
# #             p["ready"] = False
# #         await broadcast(room, {"type": "opponent_left"})
# #     else:
# #         del rooms[c]
# #         print(f"[{c}] closed")




# # # =====================================================================
# # #  N-PLAYER FREE-FOR-ALL (2-8)  — a SEPARATE system from 1v1 `rooms`.
# # #  Nothing here touches the validated 2-player match code above.
# # # =====================================================================
# # mrooms = {}   # code -> {host, size, exercise, started, players:{ws:{...}}, task}
# # COLORS = ["#22e0d6","#ff2e7e","#ffd23f","#7cf16a","#a78bfa","#ff9f43","#4dd0e1","#f06292"]

# # def mroom_of(ws):
# #     for code, r in mrooms.items():
# #         if ws in r["players"]:
# #             return code, r
# #     return None, None

# # def mroster(r):
# #     return [{"pid":p["pid"],"name":p["name"],"color":p["color"],
# #              "reps":p["reps"],"out":p["out"],"ready":p["ready"]}
# #             for p in r["players"].values()]

# # async def mbroadcast(r, payload):
# #     await asyncio.gather(*[send(ws,payload) for ws in list(r["players"].keys())],
# #                          return_exceptions=True)

# # async def msend_roster(r):
# #     await mbroadcast(r, {"type":"m_roster","players":mroster(r),
# #                          "size":r["size"],"host":r["host_pid"],"exercise":r["exercise"]})

# # async def mstart(code):
# #     r = mrooms.get(code)
# #     if not r or r["started"]: return
# #     r["started"] = True
# #     is_plank = (r["exercise"] == "plank")
# #     for p in r["players"].values():
# #         p["reps"]=0; p["out"]=False; p["ready"]=False
# #     await mbroadcast(r, {"type":"m_start","exercise":r["exercise"],
# #                          "mode":("hold" if is_plank else "reps"),
# #                          "duration":(PLANK_MAX if is_plank else DURATION)})
# #     r["task"] = asyncio.create_task(mrun(code, is_plank))

# # async def mrun(code, is_plank):
# #     r = mrooms.get(code)
# #     if not r: return
# #     if is_plank:
# #         # last one still holding wins
# #         await mbroadcast(r, {"type":"m_go"})
# #         waited=0.0
# #         while waited < PLANK_MAX:
# #             await asyncio.sleep(0.2); waited+=0.2
# #             r = mrooms.get(code)
# #             if not r: return
# #             alive=[p for p in r["players"].values() if not p["out"]]
# #             if len(alive) <= 1: break
# #     else:
# #         await mbroadcast(r, {"type":"m_go"})
# #         await asyncio.sleep(DURATION)
# #     r = mrooms.get(code)
# #     if not r: return
# #     # decide winner
# #     if is_plank:
# #         alive=[p for p in r["players"].values() if not p["out"]]
# #         winner = alive[0]["pid"] if len(alive)==1 else (alive[0]["pid"] if alive else None)
# #     else:
# #         best=max(r["players"].values(), key=lambda p:p["reps"], default=None)
# #         winner = best["pid"] if best else None
# #     r["started"]=False
# #     standings=sorted(mroster(r), key=lambda p:(p["out"], -p["reps"]))
# #     await mbroadcast(r, {"type":"m_over","winner":winner,"standings":standings})

# # async def mleave(ws):
# #     code, r = mroom_of(ws)
# #     if not r: return
# #     pid = r["players"][ws]["pid"]
# #     del r["players"][ws]
# #     if not r["players"]:
# #         t=r.get("task");  t.cancel() if t else None
# #         mrooms.pop(code, None)
# #         return
# #     # host migrates if needed
# #     if r["host_pid"]==pid:
# #         r["host_pid"]=next(iter(r["players"].values()))["pid"]
# #     if r["started"]:
# #         # if a live match empties to 1, end it
# #         alive=[p for p in r["players"].values() if not p["out"]]
# #         if r["exercise"]=="plank" and len(alive)<=1:
# #             pass  # mrun loop will finish it
# #     await msend_roster(r)


# # @app.websocket("/")
# # async def referee(ws: WebSocket):
# #     await ws.accept()

# #     try:
# #         while True:
# #             raw = await ws.receive_text()
# #             data = json.loads(raw)
# #             t = data.get("type")

# #             # ---- create a private room ----
# #             if t == "create":
# #                 if room_of(ws)[1]:
# #                     continue
# #                 remember(ws, data)
# #                 code = new_code()
# #                 exercise = data.get("exercise", "squats")
# #                 rooms[code] = {
# #                     "players": {ws: pdict(ws, "P1")},
# #                     "started": False,
# #                     "task": None,
# #                     "exercise": exercise,
# #                 }
# #                 await send(ws, {"type": "created", "code": code, "you": "P1", "exercise": exercise})
# #                 print(f"[{code}] created ({exercise})")

# #             # ---- join a private room by code ----
# #             elif t == "join":
# #                 want = (data.get("code") or "").strip().upper()
# #                 room = rooms.get(want)
# #                 if not room:
# #                     await send(ws, {"type": "error", "reason": "no_room"})
# #                 elif len(room["players"]) >= 2:
# #                     await send(ws, {"type": "error", "reason": "room_full"})
# #                 else:
# #                     remember(ws, data)
# #                     room["players"][ws] = pdict(ws, "P2")
# #                     await send(ws, {"type": "joined", "you": "P2", "code": want,
# #                                     "exercise": room.get("exercise", "squats")})
# #                     await broadcast(room, {"type": "opponent_here"})
# #                     print(f"[{want}] P2 joined")
# #                     await start_lobby(want)

# #             # ---- quick match: pair with a waiting stranger (same exercise) ----
# #             elif t == "quick":
# #                 if room_of(ws)[1]:
# #                     continue
# #                 remember(ws, data)
# #                 exercise = data.get("exercise", "squats")
# #                 dequeue(ws)                       # never queue the same socket twice
# #                 q = waiting.get(exercise, [])
# #                 opponent = None
# #                 while q:                          # find a still-waiting opponent
# #                     cand = q.pop(0)
# #                     if cand is not ws:
# #                         opponent = cand
# #                         break
# #                 if opponent is not None:
# #                     code = new_code()
# #                     rooms[code] = {
# #                         "players": {opponent: pdict(opponent, "P1"),
# #                                     ws:       pdict(ws, "P2")},
# #                         "started": False,
# #                         "task": None,
# #                         "exercise": exercise,
# #                     }
# #                     await send(opponent, {"type": "matched", "you": "P1", "exercise": exercise})
# #                     await send(ws,       {"type": "matched", "you": "P2", "exercise": exercise})
# #                     print(f"[{code}] quick match ({exercise})")
# #                     await start_lobby(code)
# #                 else:
# #                     enqueue(ws, exercise)
# #                     await send(ws, {"type": "searching", "exercise": exercise})
# #                     print(f"[queue] {exercise}: {len(waiting.get(exercise, []))} waiting")

# #             # ---- cancel searching ----
# #             elif t == "cancel":
# #                 dequeue(ws)
# #                 await send(ws, {"type": "cancelled"})

# #             # ---- live rep updates ----
# #             elif t == "reps":
# #                 c, room = room_of(ws)
# #                 if room:
# #                     room["players"][ws]["reps"] = int(data.get("reps", 0))
# #                     await broadcast(room, {"type": "scores", "scores": scores(room)})

# #             # ---- rematch: both must ask before it restarts ----
# #             elif t == "rematch":
# #                 c, room = room_of(ws)
# #                 if room:
# #                     room["players"][ws]["ready"] = True
# #                     both_ready = (len(room["players"]) == 2 and
# #                                   all(p["ready"] for p in room["players"].values()))
# #                     if both_ready:
# #                         await try_start(c)
# #                     else:
# #                         for w in room["players"]:
# #                             if w is ws:
# #                                 await send(w, {"type": "rematch_pending"})
# #                             else:
# #                                 await send(w, {"type": "rematch_offer"})

# #             # ---- plank chicken: player is now in a plank (phase 1) ----
# #             elif t == "plank_ready":
# #                 c, room = room_of(ws)
# #                 if room and room.get("started"):
# #                     room["players"][ws]["ready"] = True

# #             # ---- plank chicken: this player's form broke ----
# #             elif t == "broke":
# #                 c, room = room_of(ws)
# #                 if room and room.get("started"):
# #                     room["players"][ws]["broke"] = True
# #                     print(f"[{c}] {room['players'][ws]['id']} broke form")

# #             # ---- lobby: player hit READY (skip the timer if both are ready) ----
# #             elif t == "ready":
# #                 c, room = room_of(ws)
# #                 if room and room.get("in_lobby"):
# #                     room["players"][ws]["lobby_ready"] = True
# #                     await broadcast(room, {"type": "ready_state",
# #                                            "who": room["players"][ws]["id"]})
# #                     if (len(room["players"]) == 2 and
# #                             all(p.get("lobby_ready") for p in room["players"].values())):
# #                         await begin_match(c)

# #             # ---- lobby chat: relay a message to both players ----
# #             elif t == "chat":
# #                 c, room = room_of(ws)
# #                 if room:
# #                     txt = str(data.get("text", ""))[:200].strip()
# #                     if txt:
# #                         p = room["players"][ws]
# #                         await broadcast(room, {"type": "chat", "from": p["name"],
# #                                                "who": p["id"], "text": txt})

# #             # ---- explicit leave (reliable — doesn't wait for disconnect) ----
# #             elif t == "leave":
# #                 await leave_room(ws)

# #             # ======== N-PLAYER FREE-FOR-ALL (all "m_" types) ========
# #             elif t == "m_create":
# #                 if mroom_of(ws)[1] or room_of(ws)[1]:
# #                     continue
# #                 remember(ws, data)
# #                 i = ident.get(ws, {})
# #                 size = max(2, min(8, int(data.get("size", 4))))
# #                 code = new_code()
# #                 mrooms[code] = {
# #                     "host_pid": i.get("pid", "anon"), "size": size,
# #                     "exercise": data.get("exercise", "squats"),
# #                     "started": False, "task": None,
# #                     "players": {ws: {"pid": i.get("pid","anon"), "name": i.get("name","Player"),
# #                                      "color": COLORS[0], "reps": 0, "out": False, "ready": False}},
# #                 }
# #                 await send(ws, {"type": "m_created", "code": code, "size": size})
# #                 await msend_roster(mrooms[code])

# #             elif t == "m_join":
# #                 code = (data.get("code") or "").upper().strip()
# #                 r = mrooms.get(code)
# #                 if not r:
# #                     await send(ws, {"type": "m_error", "msg": "Room not found"}); continue
# #                 if r["started"]:
# #                     await send(ws, {"type": "m_error", "msg": "Match already started"}); continue
# #                 if len(r["players"]) >= r["size"]:
# #                     await send(ws, {"type": "m_error", "msg": "Room is full"}); continue
# #                 remember(ws, data)
# #                 i = ident.get(ws, {})
# #                 used = {p["color"] for p in r["players"].values()}
# #                 color = next((c for c in COLORS if c not in used), COLORS[len(r["players"]) % len(COLORS)])
# #                 r["players"][ws] = {"pid": i.get("pid","anon"), "name": i.get("name","Player"),
# #                                     "color": color, "reps": 0, "out": False, "ready": False}
# #                 await send(ws, {"type": "m_joined", "code": code})
# #                 await msend_roster(r)

# #             elif t == "m_begin":                 # host starts the match
# #                 code, r = mroom_of(ws)
# #                 if r and r["host_pid"] == ident.get(ws, {}).get("pid") and len(r["players"]) >= 2:
# #                     await mstart(code)

# #             elif t == "m_rep":                   # a rep happened (reps modes)
# #                 code, r = mroom_of(ws)
# #                 if r and r["started"]:
# #                     r["players"][ws]["reps"] = int(data.get("reps", 0))
# #                     await mbroadcast(r, {"type": "m_score",
# #                                          "pid": r["players"][ws]["pid"],
# #                                          "reps": r["players"][ws]["reps"]})

# #             elif t == "m_out":                   # this player dropped (plank)
# #                 code, r = mroom_of(ws)
# #                 if r and r["started"] and not r["players"][ws]["out"]:
# #                     r["players"][ws]["out"] = True
# #                     await mbroadcast(r, {"type": "m_dropped", "pid": r["players"][ws]["pid"]})

# #             elif t == "m_ready":                 # in-position for plank
# #                 code, r = mroom_of(ws)
# #                 if r:
# #                     r["players"][ws]["ready"] = True
# #                     await mbroadcast(r, {"type": "m_ready", "pid": r["players"][ws]["pid"]})

# #             elif t == "m_chat":
# #                 code, r = mroom_of(ws)
# #                 if r:
# #                     txt = str(data.get("text",""))[:200].strip()
# #                     if txt:
# #                         p = r["players"][ws]
# #                         await mbroadcast(r, {"type":"m_chat","from":p["name"],
# #                                              "pid":p["pid"],"color":p["color"],"text":txt})

# #             elif t == "m_leave":
# #                 await mleave(ws)

# #     except WebSocketDisconnect:
# #         pass
# #     except Exception as e:
# #         print("socket error:", e)

# #     finally:
# #         await leave_room(ws)
# #         await mleave(ws)


# # @app.get("/")
# # async def root():
# #     return {"status": "GymOggle Referee Running", "rooms": len(rooms)}


# # @app.get("/dbtest")
# # async def dbtest():
# #     if not supabase:
# #         return {"ok": False, "error": "no supabase client (check env vars)"}
# #     try:
# #         supabase.table("pings").insert({"note": "hello from render"}).execute()
# #         rows = supabase.table("pings").select("*").order("created_at", desc=True).limit(3).execute()
# #         return {"ok": True, "recent_pings": rows.data}
# #     except Exception as e:
# #         return {"ok": False, "error": str(e)}


# # # sync def -> FastAPI runs it in a threadpool, so DB reads don't block the game loop
# # @app.get("/leaderboard")
# # def leaderboard():
# #     if not supabase:
# #         return {"ok": False, "error": "no db"}
# #     out = {"ok": True, "scores": {}, "wins": []}
# #     try:
# #         for ex in ("squats", "pushups", "situps"):
# #             col = "best_" + ex
# #             r = (supabase.table("players").select("name," + col)
# #                  .gt(col, 0).order(col, desc=True).limit(10).execute())
# #             out["scores"][ex] = [{"name": row["name"], "value": row[col]} for row in r.data]
# #         w = (supabase.table("players").select("name,wins")
# #              .gt("wins", 0).order("wins", desc=True).limit(10).execute())
# #         out["wins"] = [{"name": row["name"], "value": row["wins"]} for row in w.data]
# #         return out
# #     except Exception as e:
# #         return {"ok": False, "error": str(e)}


# # # ============================ DAILY TASKS ============================
# # # Three tasks a day, the SAME for everyone in the world, derived from the date.

# # import datetime, hashlib

# # DAILY_POOL = [
# #     ("squats",   [15, 20, 25, 30]),
# #     ("pushups",  [8, 10, 12, 15]),
# #     ("jacks",    [20, 25, 30, 40]),
# #     ("situps",   [10, 15, 20]),
# #     ("plank",    [30, 45, 60]),        # seconds held, not reps
# # ]
# # COINS_PER_TASK = 10
# # COINS_ALL_DONE = 25          # bonus for clearing all three


# # def todays_tasks(day: str):
# #     """Deterministic from the date -> everyone on earth gets the same 3 tasks."""
# #     seed = int(hashlib.sha256(day.encode()).hexdigest(), 16)
# #     picks, pool = [], list(DAILY_POOL)
# #     for i in range(3):
# #         ex, targets = pool.pop(seed % len(pool))
# #         seed //= max(1, len(pool) + 1)
# #         target = targets[seed % len(targets)]
# #         seed //= len(targets)
# #         picks.append({"idx": i, "exercise": ex, "target": target,
# #                       "coins": COINS_PER_TASK})
# #     return picks


# # @app.get("/daily")
# # def daily(pid: str = ""):
# #     day = datetime.date.today().isoformat()
# #     tasks = todays_tasks(day)
# #     out = {"ok": True, "day": day, "tasks": tasks, "done": [],
# #            "coins": 0, "streak": 0, "all_done": False}
# #     if not supabase or not pid:
# #         return out
# #     try:
# #         d = supabase.table("daily_done").select("task_idx") \
# #             .eq("pid", pid).eq("day", day).execute()
# #         out["done"] = sorted({r["task_idx"] for r in d.data})
# #         p = supabase.table("players").select("coins,daily_streak").eq("id", pid).execute()
# #         if p.data:
# #             out["coins"] = p.data[0].get("coins") or 0
# #             out["streak"] = p.data[0].get("daily_streak") or 0
# #         out["all_done"] = len(out["done"]) >= 3
# #         return out
# #     except Exception as e:
# #         out["error"] = str(e)
# #         return out


# # @app.post("/daily/complete")
# # def daily_complete(payload: dict):
# #     """Body: {pid, name, task_idx, exercise, reps}"""
# #     if not supabase:
# #         return {"ok": False, "error": "no db"}
# #     pid = (payload.get("pid") or "").strip()
# #     if not pid:
# #         return {"ok": False, "error": "no pid"}
# #     day = datetime.date.today().isoformat()
# #     tasks = todays_tasks(day)
# #     try:
# #         idx = int(payload.get("task_idx", -1))
# #         task = next((t for t in tasks if t["idx"] == idx), None)
# #         if not task:
# #             return {"ok": False, "error": "bad task"}
# #         reps = int(payload.get("reps", 0))
# #         # server-side sanity: must actually hit the target
# #         if reps < task["target"]:
# #             return {"ok": False, "error": "target not met"}

# #         # already done today? (unique constraint also protects us)
# #         prev = supabase.table("daily_done").select("task_idx") \
# #             .eq("pid", pid).eq("day", day).execute()
# #         done_idx = {r["task_idx"] for r in prev.data}
# #         if idx in done_idx:
# #             return {"ok": True, "already": True}

# #         supabase.table("daily_done").insert({
# #             "pid": pid, "day": day, "task_idx": idx,
# #             "exercise": task["exercise"], "reps": reps}).execute()
# #         done_idx.add(idx)

# #         # ---- coins + streak ----
# #         row = supabase.table("players").select("*").eq("id", pid).execute()
# #         p = row.data[0] if row.data else {}
# #         coins = (p.get("coins") or 0) + COINS_PER_TASK
# #         streak = p.get("daily_streak") or 0
# #         best = p.get("best_daily_streak") or 0
# #         last = p.get("last_daily")
# #         all_done = len(done_idx) >= 3

# #         if all_done:
# #             coins += COINS_ALL_DONE
# #             yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
# #             if last == day:
# #                 pass                      # streak already counted today
# #             elif last == yesterday:
# #                 streak += 1
# #             else:
# #                 streak = 1
# #             best = max(best, streak)

# #         upd = {"id": pid, "name": payload.get("name") or p.get("name") or "Player",
# #                "coins": coins, "daily_streak": streak, "best_daily_streak": best}
# #         if all_done:
# #             upd["last_daily"] = day
# #         supabase.table("players").upsert(upd).execute()

# #         return {"ok": True, "coins": coins, "streak": streak,
# #                 "all_done": all_done, "done": sorted(done_idx),
# #                 "earned": COINS_PER_TASK + (COINS_ALL_DONE if all_done else 0)}
# #     except Exception as e:
# #         return {"ok": False, "error": str(e)}


# # if __name__ == "__main__":
# #     uvicorn.run("server:app", host="0.0.0.0", port=8000)
# # Test 11 ------
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
# PLANK_MAX = 300     # safety cap for Plank Chicken (5 min) so a match can't run forever
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
#         if exercise in ("squats", "pushups", "situps", "jacks", "plank"):
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

#     ex = room.get("exercise", "squats")
#     is_plank = (ex == "plank")
#     for p in room["players"].values():
#         p["broke"] = False

#     print(f"[{code}] match starting ({ex})")
#     await broadcast(room, {"type": "start",
#                            "duration": (PLANK_MAX if is_plank else DURATION),
#                            "mode": ("hold" if is_plank else "reps"),
#                            "exercise": ex})

#     if is_plank:
#         # PLANK CHICKEN
#         # Phase 1: wait for BOTH players to get into a plank ("ready").
#         # Phase 2: a synced 5s countdown — both must stay in position.
#         # Phase 3: LIVE — first to drop loses.
#         for p in room["players"].values():
#             p["ready"] = False
#             p["broke"] = False

#         waited = 0.0
#         while waited < 60:                      # up to 60s to both get into position
#             await asyncio.sleep(0.15); waited += 0.15
#             room = rooms.get(code)
#             if not room or len(room["players"]) < 2: return
#             if all(p.get("ready") for p in room["players"].values()):
#                 break

#         # synced countdown
#         await broadcast(room, {"type": "plank_go", "count": 5})
#         for n in range(5, 0, -1):
#             await asyncio.sleep(1.0)
#             room = rooms.get(code)
#             if not room or len(room["players"]) < 2: return

#         await broadcast(room, {"type": "plank_live"})   # NOW it counts
#         for p in room["players"].values():
#             p["broke"] = False                          # ignore any drops before this

#         waited = 0.0
#         while waited < PLANK_MAX:
#             await asyncio.sleep(0.15); waited += 0.15
#             room = rooms.get(code)
#             if not room or len(room["players"]) < 2: return
#             if any(p.get("broke") for p in room["players"].values()):
#                 break
#     else:
#         await asyncio.sleep(DURATION)

#     room = rooms.get(code)          # may have been torn down while we slept
#     if not room:
#         return

#     s = scores(room)
#     if is_plank:
#         broken = [p for p in room["players"].values() if p.get("broke")]
#         if len(broken) == 1:
#             loser = broken[0]["id"]
#             winner = "P2" if loser == "P1" else "P1"
#         elif len(broken) >= 2:
#             winner = "TIE"                       # both cracked in the same instant
#         else:
#             # hit the safety cap with both still holding -> longest hold wins
#             p1, p2 = s.get("P1", 0), s.get("P2", 0)
#             winner = "TIE" if p1 == p2 else ("P1" if p1 > p2 else "P2")
#     elif len(s) == 2:
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




# # =====================================================================
# #  N-PLAYER FREE-FOR-ALL (2-8)  — a SEPARATE system from 1v1 `rooms`.
# #  Nothing here touches the validated 2-player match code above.
# # =====================================================================
# mrooms = {}   # code -> {host, size, exercise, started, players:{ws:{...}}, task}
# COLORS = ["#22e0d6","#ff2e7e","#ffd23f","#7cf16a","#a78bfa","#ff9f43","#4dd0e1","#f06292"]

# def mroom_of(ws):
#     for code, r in mrooms.items():
#         if ws in r["players"]:
#             return code, r
#     return None, None

# def mroster(r):
#     return [{"pid":p["pid"],"name":p["name"],"color":p["color"],
#              "reps":p["reps"],"out":p["out"],"ready":p["ready"]}
#             for p in r["players"].values()]

# async def mbroadcast(r, payload):
#     await asyncio.gather(*[send(ws,payload) for ws in list(r["players"].keys())],
#                          return_exceptions=True)

# async def msend_roster(r):
#     await mbroadcast(r, {"type":"m_roster","players":mroster(r),
#                          "size":r["size"],"host":r["host_pid"],"exercise":r["exercise"]})

# async def mstart(code):
#     r = mrooms.get(code)
#     if not r or r["started"]: return
#     r["started"] = True
#     is_plank = (r["exercise"] == "plank")
#     for p in r["players"].values():
#         p["reps"]=0; p["out"]=False; p["ready"]=False
#     await mbroadcast(r, {"type":"m_start","exercise":r["exercise"],
#                          "mode":("hold" if is_plank else "reps"),
#                          "duration":(PLANK_MAX if is_plank else DURATION)})
#     r["task"] = asyncio.create_task(mrun(code, is_plank))

# async def mrun(code, is_plank):
#     r = mrooms.get(code)
#     if not r: return
#     if is_plank:
#         # last one still holding wins
#         await mbroadcast(r, {"type":"m_go"})
#         waited=0.0
#         while waited < PLANK_MAX:
#             await asyncio.sleep(0.2); waited+=0.2
#             r = mrooms.get(code)
#             if not r: return
#             alive=[p for p in r["players"].values() if not p["out"]]
#             if len(alive) <= 1: break
#     else:
#         await mbroadcast(r, {"type":"m_go"})
#         await asyncio.sleep(DURATION)
#     r = mrooms.get(code)
#     if not r: return
#     # decide winner
#     if is_plank:
#         alive=[p for p in r["players"].values() if not p["out"]]
#         winner = alive[0]["pid"] if len(alive)==1 else (alive[0]["pid"] if alive else None)
#     else:
#         best=max(r["players"].values(), key=lambda p:p["reps"], default=None)
#         winner = best["pid"] if best else None
#     r["started"]=False
#     standings=sorted(mroster(r), key=lambda p:(p["out"], -p["reps"]))
#     await mbroadcast(r, {"type":"m_over","winner":winner,"standings":standings})

# async def mleave(ws):
#     code, r = mroom_of(ws)
#     if not r: return
#     pid = r["players"][ws]["pid"]
#     del r["players"][ws]
#     if not r["players"]:
#         t=r.get("task");  t.cancel() if t else None
#         mrooms.pop(code, None)
#         return
#     # host migrates if needed
#     if r["host_pid"]==pid:
#         r["host_pid"]=next(iter(r["players"].values()))["pid"]
#     if r["started"]:
#         # if a live match empties to 1, end it
#         alive=[p for p in r["players"].values() if not p["out"]]
#         if r["exercise"]=="plank" and len(alive)<=1:
#             pass  # mrun loop will finish it
#     await msend_roster(r)


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

#             # ---- plank chicken: player is now in a plank (phase 1) ----
#             elif t == "plank_ready":
#                 c, room = room_of(ws)
#                 if room and room.get("started"):
#                     room["players"][ws]["ready"] = True

#             # ---- plank chicken: this player's form broke ----
#             elif t == "broke":
#                 c, room = room_of(ws)
#                 if room and room.get("started"):
#                     room["players"][ws]["broke"] = True
#                     print(f"[{c}] {room['players'][ws]['id']} broke form")

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

#             # ======== N-PLAYER FREE-FOR-ALL (all "m_" types) ========
#             elif t == "m_create":
#                 if mroom_of(ws)[1] or room_of(ws)[1]:
#                     continue
#                 remember(ws, data)
#                 i = ident.get(ws, {})
#                 size = max(2, min(8, int(data.get("size", 4))))
#                 code = new_code()
#                 mrooms[code] = {
#                     "host_pid": i.get("pid", "anon"), "size": size,
#                     "exercise": data.get("exercise", "squats"),
#                     "started": False, "task": None,
#                     "players": {ws: {"pid": i.get("pid","anon"), "name": i.get("name","Player"),
#                                      "color": COLORS[0], "reps": 0, "out": False, "ready": False}},
#                 }
#                 await send(ws, {"type": "m_created", "code": code, "size": size})
#                 await msend_roster(mrooms[code])

#             elif t == "m_join":
#                 code = (data.get("code") or "").upper().strip()
#                 r = mrooms.get(code)
#                 if not r:
#                     await send(ws, {"type": "m_error", "msg": "Room not found"}); continue
#                 if r["started"]:
#                     await send(ws, {"type": "m_error", "msg": "Match already started"}); continue
#                 if len(r["players"]) >= r["size"]:
#                     await send(ws, {"type": "m_error", "msg": "Room is full"}); continue
#                 remember(ws, data)
#                 i = ident.get(ws, {})
#                 used = {p["color"] for p in r["players"].values()}
#                 color = next((c for c in COLORS if c not in used), COLORS[len(r["players"]) % len(COLORS)])
#                 r["players"][ws] = {"pid": i.get("pid","anon"), "name": i.get("name","Player"),
#                                     "color": color, "reps": 0, "out": False, "ready": False}
#                 await send(ws, {"type": "m_joined", "code": code})
#                 await msend_roster(r)

#             elif t == "m_begin":                 # host starts the match
#                 code, r = mroom_of(ws)
#                 if r and r["host_pid"] == ident.get(ws, {}).get("pid") and len(r["players"]) >= 2:
#                     await mstart(code)

#             elif t == "m_rep":                   # a rep happened (reps modes)
#                 code, r = mroom_of(ws)
#                 if r and r["started"]:
#                     r["players"][ws]["reps"] = int(data.get("reps", 0))
#                     await mbroadcast(r, {"type": "m_score",
#                                          "pid": r["players"][ws]["pid"],
#                                          "reps": r["players"][ws]["reps"]})

#             elif t == "m_out":                   # this player dropped (plank)
#                 code, r = mroom_of(ws)
#                 if r and r["started"] and not r["players"][ws]["out"]:
#                     r["players"][ws]["out"] = True
#                     await mbroadcast(r, {"type": "m_dropped", "pid": r["players"][ws]["pid"]})

#             elif t == "m_ready":                 # in-position for plank
#                 code, r = mroom_of(ws)
#                 if r:
#                     r["players"][ws]["ready"] = True
#                     await mbroadcast(r, {"type": "m_ready", "pid": r["players"][ws]["pid"]})

#             elif t == "m_chat":
#                 code, r = mroom_of(ws)
#                 if r:
#                     txt = str(data.get("text",""))[:200].strip()
#                     if txt:
#                         p = r["players"][ws]
#                         await mbroadcast(r, {"type":"m_chat","from":p["name"],
#                                              "pid":p["pid"],"color":p["color"],"text":txt})

#             elif t == "m_leave":
#                 await mleave(ws)

#     except WebSocketDisconnect:
#         pass
#     except Exception as e:
#         print("socket error:", e)

#     finally:
#         await leave_room(ws)
#         await mleave(ws)


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
#     ("plank",    [30, 45, 60]),        # seconds held, not reps
# ]
# COINS_PER_TASK = 10
# JOURNEY_COINS = 20        # coins for completing one journey day
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


# @app.post("/journey/complete")
# def journey_complete(payload: dict):
#     """Body: {pid, name, day}. Awards coins for finishing a journey day (once per day-number)."""
#     if not supabase:
#         return {"ok": False, "error": "no db"}
#     pid = (payload.get("pid") or "").strip()
#     if not pid:
#         return {"ok": False, "error": "no pid"}
#     try:
#         day = int(payload.get("day", 0))
#         if day < 1 or day > 30:
#             return {"ok": False, "error": "bad day"}
#         # has this player already claimed this journey day?
#         prev = supabase.table("journey_done").select("day").eq("pid", pid).eq("day", day).execute()
#         if prev.data:
#             return {"ok": True, "already": True}
#         supabase.table("journey_done").insert({"pid": pid, "day": day}).execute()
#         row = supabase.table("players").select("coins").eq("id", pid).execute()
#         coins = ((row.data[0].get("coins") if row.data else 0) or 0) + JOURNEY_COINS
#         name = (payload.get("name") or "Player")[:24]
#         supabase.table("players").upsert({"id": pid, "name": name, "coins": coins}).execute()
#         return {"ok": True, "earned": JOURNEY_COINS, "coins": coins}
#     except Exception as e:
#         print("journey error:", e)
#         return {"ok": False, "error": "server"}


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
# TEst 12 --------
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
    # If the client sent a login token, VERIFY it and use the real user id.
    # This stops anyone from claiming another player's identity / padding their stats.
    tok = data.get("token")
    if tok:
        u = verify_token(tok)
        if u:
            ident[ws] = {"pid": u["id"], "name": (data.get("name") or "Player")}
            return
    ident[ws] = {"pid": (data.get("pid") or "anon"), "name": (data.get("name") or "Player")}

def pdict(ws, role):
    i = ident.get(ws, {})
    return {"id": role, "pid": i.get("pid", "anon"), "name": i.get("name", "Player"),
            "reps": 0, "ready": False}


# --- persistence: record a finished match + update player summaries ---
def record_match_sync(exercise, p1, p2, winner):
    if not supabase:
        return
    # a bot has a pid starting with "bot_" — never write bots to the DB or
    # the leaderboard, and don't log matches that involve a bot.
    p1_bot = str(p1.get("pid", "")).startswith("bot_")
    p2_bot = str(p2.get("pid", "")).startswith("bot_")
    if p1_bot or p2_bot:
        # update only the HUMAN's personal bests (real effort); no match row,
        # no win/loss change, nothing about the bot.
        try:
            if not p1_bot:
                _update_player(p1, exercise, won=False, drew=False, record_result=False)
            if not p2_bot:
                _update_player(p2, exercise, won=False, drew=False, record_result=False)
        except Exception as e:
            print("bot-match stat update failed:", e)
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

def _update_player(p, exercise, won, drew, record_result=True):
    pid = p.get("pid")
    if not pid or pid == "anon":
        return
    try:
        res = supabase.table("players").select("*").eq("id", pid).execute()
        row = res.data[0] if res.data else {}
        payload = {"id": pid, "name": p.get("name", "Player")}
        if record_result:
            # only real (human-vs-human) matches affect the competitive record
            cur = (row.get("current_streak", 0) + 1) if won else 0
            payload.update({
                "wins":   row.get("wins", 0)   + (1 if won else 0),
                "losses": row.get("losses", 0) + (0 if (won or drew) else 1),
                "draws":  row.get("draws", 0)  + (1 if drew else 0),
                "current_streak": cur,
                "best_streak": max(row.get("best_streak", 0), cur),
            })
        # personal bests reflect REAL effort, so they update even vs a bot
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

    # if this room has a bot, start its behaviour engine
    bot_ws = next((w for w in room["players"] if is_bot(w)), None)
    if bot_ws is not None:
        if is_plank:
            asyncio.create_task(run_bot_plank(code, bot_ws))
        else:
            asyncio.create_task(run_bot_reps(code, bot_ws, ex))

    if is_plank:
        # PLANK CHICKEN
        # Phase 1: wait for BOTH players to get into a plank ("ready").
        # Phase 2: a synced 5s countdown — both must stay in position.
        # Phase 3: LIVE — first to drop loses.
        for p in room["players"].values():
            p["ready"] = False
            p["broke"] = False

        waited = 0.0
        while waited < 60:                      # up to 60s to both get into position
            await asyncio.sleep(0.15); waited += 0.15
            room = rooms.get(code)
            if not room or len(room["players"]) < 2: return
            if all(p.get("ready") for p in room["players"].values()):
                break

        # synced countdown
        await broadcast(room, {"type": "plank_go", "count": 5})
        for n in range(5, 0, -1):
            await asyncio.sleep(1.0)
            room = rooms.get(code)
            if not room or len(room["players"]) < 2: return

        await broadcast(room, {"type": "plank_live"})   # NOW it counts
        room["plank_live_at"] = _time.monotonic()       # bot times its hold from here
        for p in room["players"].values():
            p["broke"] = False                          # ignore any drops before this

        waited = 0.0
        while waited < PLANK_MAX:
            await asyncio.sleep(0.15); waited += 0.15
            room = rooms.get(code)
            if not room or len(room["players"]) < 2: return
            if any(p.get("broke") for p in room["players"].values()):
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
BOT_WAIT_SECS = 18   # wait this long for a human before spawning a bot

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
    # if a bot is in the room, have it drop one trash-talk line after a beat
    bot_ws = next((w for w in room["players"] if is_bot(w)), None)
    if bot_ws is not None:
        asyncio.create_task(_bot_taunt(code, bot_ws))

async def _bot_taunt(code, bot_ws):
    await asyncio.sleep(random.uniform(2.5, 5.0))
    room = rooms.get(code)
    if not room or not room.get("in_lobby") or bot_ws not in room["players"]:
        return
    line = random.choice(BOT_TAUNTS)
    bname = ident.get(bot_ws, {}).get("name", "Opponent")
    # send to the human(s) as a normal chat message from the bot's "P2"/"P1" seat
    seat = room["players"][bot_ws]["id"]
    for ws in list(room["players"].keys()):
        if not is_bot(ws):
            await send(ws, {"type": "chat", "text": line, "who": seat, "from": bname})

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



# =====================================================================
#  BOTS — fill empty quick-match rooms so players always land in a game.
#  A bot is a fake "player" backed by BotWS (a no-op stand-in for a real
#  websocket). It slots into the room dict exactly like a human, so every
#  existing function (broadcast, scores, run_match) works unchanged.
#  The bot's reps are generated on a REALISTIC curve — variable pace,
#  a slow start, a mid plateau, and a final surge — so it feels human.
# =====================================================================
import time as _time

BOT_NAMES = [
    "riya_22","arjunnn","sam_k","kabir.x","mia_fit","leo7","zara_z","neilll","adi_04","tara.m",
    "jay_x7","nina__","ravi.99","kimmy_k","alexxx","dev_op","sana_z","omar.k","ivy_23","max_out",
    "priya_p","rohan_11","ella.x","vik_08","noor__","ash_ley","kai.99","reyansh","aria_a","ben_10",
    "isha.k","yuki_x","diego7","lena__","tom_k","fatima.z","chris99","anya.a","raj_00","cleo_x",
    "maya_m","finn.7","sara__","ib_x","nomi99","zed_z","lux.k","rex_00","bo__","quinn7",
    "big_mike","fit_freak","noscope","xX_dan","gym_rat9","reps4days","chad.99","lil_squat","the_beast","sweatybetty",
]
BOT_TAUNTS = [
    "let's go 💪","easy win incoming","try to keep up 😏","warmed up already",
    "may the best win","you ready?","no mercy today","first one's on me 😂",
    "let's gooo","bring it",
]
BOT_COLORS = ["#22e0d6","#ff2e7e","#ffd23f","#7cf16a","#a78bfa","#ff9f43","#4dd0e1","#f06292"]

class BotWS:
    """Stand-in for a websocket. Sends go nowhere; identity lives in ident[]."""
    def __init__(self):
        self.is_bot = True
    async def send_text(self, _):
        pass
    async def close(self):
        pass

def is_bot(ws):
    return getattr(ws, "is_bot", False)

def make_bot(exercise):
    ws = BotWS()
    name = random.choice(BOT_NAMES)
    ident[ws] = {"pid": "bot_" + str(random.randint(10000, 99999)), "name": name}
    return ws

COUNTDOWN_PAD = 3.0    # ~length of the 3-2-1-GO countdown before reps count
BOT_START_AT  = 28     # bot stays at 0 until the match clock counts down to this
BOT_CAP = {"squats": 24, "pushups": 13, "jacks": 27, "situps": 18}  # HARD ceilings — never exceed

def bot_target(exercise):
    """A believable BEGINNER performance — kept in the lower/mid range, never elite."""
    if exercise == "plank":
        return random.uniform(30, 45)        # seconds held before dropping (30-45s window)
    base = {"squats": 17, "pushups": 9, "jacks": 20, "situps": 13}.get(exercise, 15)
    val = random.gauss(base, base * 0.24)
    cap = BOT_CAP.get(exercise, 24)
    return max(6, min(cap, val))             # clamp: floor 6, hard ceiling per exercise

def bot_rep_schedule(total, duration):
    """Return a list of timestamps (seconds from the "start" broadcast) at which
    the bot does each rep. The bot stays at ZERO until the match clock counts
    down to BOT_START_AT (so it never has a head-start during the 3-2-1-GO
    countdown), then reps across the remaining time with a human-like curve."""
    total = int(round(total))
    if total <= 0:
        return []
    times = []
    for i in range(total):
        frac = (i + 0.5) / total
        if frac < 0.15:      pace = 0.70 + frac
        elif frac < 0.65:    pace = 1.0
        elif frac < 0.85:    pace = 0.82
        else:                pace = 1.25            # final surge
        times.append(pace)
    # the bot only starts once the clock has ticked down to BOT_START_AT.
    # elapsed_at_start = duration - BOT_START_AT  (e.g. 35 - 28 = 7s in)
    begin = COUNTDOWN_PAD + (duration - BOT_START_AT)
    span = (BOT_START_AT * random.uniform(0.80, 0.95))   # fit reps into what's left
    cum = []
    acc = 0.0
    for p in times:
        acc += 1.0 / p
        cum.append(acc)
    scale = span / cum[-1]
    out = []
    for c in cum:
        jitter = random.uniform(-0.18, 0.18)
        out.append(begin + max(0.0, c * scale + jitter))
    out.sort()
    return out

async def run_bot_reps(code, bot_ws, exercise):
    """Drive the bot's reps over the match on its schedule."""
    room = rooms.get(code)
    if not room or bot_ws not in room["players"]:
        return
    total = bot_target(exercise)
    schedule = bot_rep_schedule(total, DURATION)
    start = _time.monotonic()
    for t in schedule:
        delay = t - (_time.monotonic() - start)
        if delay > 0:
            await asyncio.sleep(delay)
        room = rooms.get(code)
        if not room or bot_ws not in room["players"] or not room.get("started"):
            return
        room["players"][bot_ws]["reps"] += 1
        # broadcast the FULL score dict, exactly like a human's rep does —
        # so the client literally cannot tell this came from a bot.
        await broadcast(room, {"type": "scores", "scores": scores(room)})

async def run_bot_plank(code, bot_ws):
    """Bot gets into a plank, then drops after a believable hold."""
    room = rooms.get(code)
    if not room or bot_ws not in room["players"]:
        return
    # get into position quickly (0.5-2.5s)
    await asyncio.sleep(random.uniform(0.5, 2.5))
    room = rooms.get(code)
    if room and bot_ws in room["players"]:
        room["players"][bot_ws]["ready"] = True
    # wait until the match goes live, then hold for target seconds, then drop
    hold = max(6, bot_target("plank"))
    waited = 0.0
    while waited < hold + 15:
        await asyncio.sleep(0.3); waited += 0.3
        room = rooms.get(code)
        if not room or bot_ws not in room["players"]:
            return
        if room.get("plank_live_at"):
            elapsed = _time.monotonic() - room["plank_live_at"]
            if elapsed >= hold:
                room["players"][bot_ws]["broke"] = True
                return

async def spawn_bot_match(human_ws, exercise):
    """Create a room pairing the human with a fresh bot, and start it."""
    dequeue(human_ws)
    bot_ws = make_bot(exercise)
    code = new_code()
    rooms[code] = {
        "players": {human_ws: pdict(human_ws, "P1"),
                    bot_ws:   pdict(bot_ws, "P2")},
        "started": False, "task": None, "exercise": exercise,
        "has_bot": True,
    }
    await send(human_ws, {"type": "matched", "you": "P1", "exercise": exercise})
    print(f"[{code}] BOT match ({exercise}) vs {ident[bot_ws]['name']}")
    await start_lobby(code)


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




# =====================================================================
#  N-PLAYER FREE-FOR-ALL (2-8)  — a SEPARATE system from 1v1 `rooms`.
#  Nothing here touches the validated 2-player match code above.
# =====================================================================
mrooms = {}   # code -> {host, size, exercise, started, players:{ws:{...}}, task}
COLORS = ["#22e0d6","#ff2e7e","#ffd23f","#7cf16a","#a78bfa","#ff9f43","#4dd0e1","#f06292"]

def mroom_of(ws):
    for code, r in mrooms.items():
        if ws in r["players"]:
            return code, r
    return None, None

def mroster(r):
    return [{"pid":p["pid"],"name":p["name"],"color":p["color"],
             "reps":p["reps"],"out":p["out"],"ready":p["ready"]}
            for p in r["players"].values()]

async def mbroadcast(r, payload):
    await asyncio.gather(*[send(ws,payload) for ws in list(r["players"].keys())],
                         return_exceptions=True)

async def msend_roster(r):
    await mbroadcast(r, {"type":"m_roster","players":mroster(r),
                         "size":r["size"],"host":r["host_pid"],"exercise":r["exercise"]})

async def mstart(code):
    r = mrooms.get(code)
    if not r or r["started"]: return
    r["started"] = True
    is_plank = (r["exercise"] == "plank")
    dur = int(r.get("duration") or DURATION)
    dur = max(15, min(300, dur))                      # clamp 15s..5min
    for p in r["players"].values():
        p["reps"]=0; p["out"]=False; p["ready"]=False
    await mbroadcast(r, {"type":"m_start","exercise":r["exercise"],
                         "mode":("hold" if is_plank else "reps"),
                         "duration":(PLANK_MAX if is_plank else dur)})
    r["task"] = asyncio.create_task(mrun(code, is_plank, dur))

async def mrun(code, is_plank, dur):
    r = mrooms.get(code)
    if not r: return
    # a synced 3-2-1-GO countdown so the match doesn't start abruptly
    await mbroadcast(r, {"type":"m_countdown", "count":3})
    await asyncio.sleep(3.2)
    r = mrooms.get(code)
    if not r: return
    if is_plank:
        # last one still holding wins (no countdown-to-win; just a running timer)
        await mbroadcast(r, {"type":"m_go"})
        waited=0.0
        while waited < PLANK_MAX:
            await asyncio.sleep(0.2); waited+=0.2
            r = mrooms.get(code)
            if not r: return
            alive=[p for p in r["players"].values() if not p["out"]]
            if len(alive) <= 1: break
    else:
        await mbroadcast(r, {"type":"m_go"})
        await asyncio.sleep(dur)
    r = mrooms.get(code)
    if not r: return
    # decide winner
    if is_plank:
        alive=[p for p in r["players"].values() if not p["out"]]
        winner = alive[0]["pid"] if len(alive)==1 else (alive[0]["pid"] if alive else None)
    else:
        best=max(r["players"].values(), key=lambda p:p["reps"], default=None)
        winner = best["pid"] if best else None
    r["started"]=False
    standings=sorted(mroster(r), key=lambda p:(p["out"], -p["reps"]))
    await mbroadcast(r, {"type":"m_over","winner":winner,"standings":standings})

async def mleave(ws):
    code, r = mroom_of(ws)
    if not r: return
    pid = r["players"][ws]["pid"]
    del r["players"][ws]
    if not r["players"]:
        t=r.get("task");  t.cancel() if t else None
        mrooms.pop(code, None)
        return
    # host migrates if needed
    if r["host_pid"]==pid:
        r["host_pid"]=next(iter(r["players"].values()))["pid"]
    if r["started"]:
        # if a live match empties to 1, end it
        alive=[p for p in r["players"].values() if not p["out"]]
        if r["exercise"]=="plank" and len(alive)<=1:
            pass  # mrun loop will finish it
    await msend_roster(r)


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
                    # if nobody real shows up in time, fill the room with a bot so the
                    # player always lands in a game (the cold-start fix).
                    async def _bot_fallback(w=ws, ex=exercise):
                        await asyncio.sleep(BOT_WAIT_SECS)
                        # still waiting (not matched, not cancelled, not gone)?
                        if w in waiting.get(ex, []) and not room_of(w)[1]:
                            await spawn_bot_match(w, ex)
                    asyncio.create_task(_bot_fallback())

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

            # ---- plank chicken: player is now in a plank (phase 1) ----
            elif t == "plank_ready":
                c, room = room_of(ws)
                if room and room.get("started"):
                    room["players"][ws]["ready"] = True

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

            # ======== N-PLAYER FREE-FOR-ALL (all "m_" types) ========
            elif t == "m_create":
                if mroom_of(ws)[1] or room_of(ws)[1]:
                    continue
                remember(ws, data)
                i = ident.get(ws, {})
                size = max(2, min(8, int(data.get("size", 4))))
                code = new_code()
                mrooms[code] = {
                    "host_pid": i.get("pid", "anon"), "size": size,
                    "exercise": data.get("exercise", "squats"),
                    "duration": max(15, min(300, int(data.get("duration", DURATION)))),
                    "started": False, "task": None,
                    "players": {ws: {"pid": i.get("pid","anon"), "name": i.get("name","Player"),
                                     "color": COLORS[0], "reps": 0, "out": False, "ready": False}},
                }
                await send(ws, {"type": "m_created", "code": code, "size": size})
                await msend_roster(mrooms[code])

            elif t == "m_join":
                code = (data.get("code") or "").upper().strip()
                r = mrooms.get(code)
                if not r:
                    await send(ws, {"type": "m_error", "msg": "Room not found"}); continue
                if r["started"]:
                    await send(ws, {"type": "m_error", "msg": "Match already started"}); continue
                if len(r["players"]) >= r["size"]:
                    await send(ws, {"type": "m_error", "msg": "Room is full"}); continue
                remember(ws, data)
                i = ident.get(ws, {})
                used = {p["color"] for p in r["players"].values()}
                color = next((c for c in COLORS if c not in used), COLORS[len(r["players"]) % len(COLORS)])
                r["players"][ws] = {"pid": i.get("pid","anon"), "name": i.get("name","Player"),
                                    "color": color, "reps": 0, "out": False, "ready": False}
                await send(ws, {"type": "m_joined", "code": code})
                await msend_roster(r)

            elif t == "m_begin":                 # host starts the match
                code, r = mroom_of(ws)
                if r and r["host_pid"] == ident.get(ws, {}).get("pid") and len(r["players"]) >= 2:
                    await mstart(code)

            elif t == "m_rep":                   # a rep happened (reps modes)
                code, r = mroom_of(ws)
                if r and r["started"]:
                    r["players"][ws]["reps"] = int(data.get("reps", 0))
                    await mbroadcast(r, {"type": "m_score",
                                         "pid": r["players"][ws]["pid"],
                                         "reps": r["players"][ws]["reps"]})

            elif t == "m_out":                   # this player dropped (plank)
                code, r = mroom_of(ws)
                if r and r["started"] and not r["players"][ws]["out"]:
                    r["players"][ws]["out"] = True
                    await mbroadcast(r, {"type": "m_dropped", "pid": r["players"][ws]["pid"]})

            elif t == "m_ready":                 # in-position for plank
                code, r = mroom_of(ws)
                if r:
                    r["players"][ws]["ready"] = True
                    await mbroadcast(r, {"type": "m_ready", "pid": r["players"][ws]["pid"]})

            elif t == "m_chat":
                code, r = mroom_of(ws)
                if r:
                    txt = str(data.get("text",""))[:200].strip()
                    if txt:
                        p = r["players"][ws]
                        await mbroadcast(r, {"type":"m_chat","from":p["name"],
                                             "pid":p["pid"],"color":p["color"],"text":txt})

            elif t == "m_leave":
                await mleave(ws)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print("socket error:", e)

    finally:
        await leave_room(ws)
        await mleave(ws)


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
JOURNEY_COINS = 20        # coins for completing one journey day
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



# =====================================================================
#  AUTH — verify the Supabase JWT so we KNOW who a user is (not just
#  trust whatever id the client sends). This is the security backbone.
# =====================================================================
def verify_token(token: str):
    """Return the Supabase user {id, email} for a valid JWT, else None.
    We ask Supabase to validate the token — no local secret needed."""
    if not token or not supabase:
        return None
    try:
        res = supabase.auth.get_user(token)      # validates signature + expiry
        u = getattr(res, "user", None) or (res.get("user") if isinstance(res, dict) else None)
        if not u:
            return None
        uid = getattr(u, "id", None) or (u.get("id") if isinstance(u, dict) else None)
        email = getattr(u, "email", None) or (u.get("email") if isinstance(u, dict) else None)
        return {"id": uid, "email": email} if uid else None
    except Exception as e:
        print("token verify failed:", e)
        return None


@app.post("/me")
def me(payload: dict):
    """Return this user's GymOggle profile (or ok:true with no profile if new)."""
    user = verify_token((payload or {}).get("token", ""))
    if not user:
        return {"ok": False, "error": "unauthorized"}
    try:
        r = supabase.table("players").select("id,name,color,wins,losses,coins").eq("id", user["id"]).execute()
        if r.data:
            return {"ok": True, "profile": r.data[0]}
        return {"ok": True, "profile": None}      # new user -> needs setup
    except Exception as e:
        print("me error:", e)
        return {"ok": False, "error": "server"}


@app.post("/me/create")
def me_create(payload: dict):
    """First-time setup: claim a username + colour, keyed to the verified user id."""
    user = verify_token((payload or {}).get("token", ""))
    if not user:
        return {"ok": False, "error": "unauthorized"}
    name = str((payload or {}).get("name", "")).strip()[:16]
    color = str((payload or {}).get("color", "#22e0d6"))[:9]
    if len(name) < 2:
        return {"ok": False, "error": "bad_name"}
    try:
        # username must be unique (case-insensitive) and not already taken by someone else
        taken = supabase.table("players").select("id").ilike("name", name).execute()
        if taken.data and any(row["id"] != user["id"] for row in taken.data):
            return {"ok": False, "error": "name_taken"}
        row = {"id": user["id"], "name": name, "color": color, "email": user.get("email")}
        supabase.table("players").upsert(row).execute()
        got = supabase.table("players").select("id,name,color,wins,losses,coins").eq("id", user["id"]).execute()
        return {"ok": True, "profile": got.data[0] if got.data else row}
    except Exception as e:
        print("me_create error:", e)
        return {"ok": False, "error": "server"}


@app.post("/journey/complete")
def journey_complete(payload: dict):
    """Body: {pid, name, day}. Awards coins for finishing a journey day (once per day-number)."""
    if not supabase:
        return {"ok": False, "error": "no db"}
    pid = (payload.get("pid") or "").strip()
    if not pid:
        return {"ok": False, "error": "no pid"}
    try:
        day = int(payload.get("day", 0))
        if day < 1 or day > 30:
            return {"ok": False, "error": "bad day"}
        # has this player already claimed this journey day?
        prev = supabase.table("journey_done").select("day").eq("pid", pid).eq("day", day).execute()
        if prev.data:
            return {"ok": True, "already": True}
        supabase.table("journey_done").insert({"pid": pid, "day": day}).execute()
        row = supabase.table("players").select("coins").eq("id", pid).execute()
        coins = ((row.data[0].get("coins") if row.data else 0) or 0) + JOURNEY_COINS
        name = (payload.get("name") or "Player")[:24]
        supabase.table("players").upsert({"id": pid, "name": name, "coins": coins}).execute()
        return {"ok": True, "earned": JOURNEY_COINS, "coins": coins}
    except Exception as e:
        print("journey error:", e)
        return {"ok": False, "error": "server"}


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