# ---------------------Test 1-----------------------------------

# import cv2
# import numpy as np
# import mediapipe as mp

# mp_pose = mp.solutions.pose
# mp_draw = mp.solutions.drawing_utils

# def angle(a, b, c):                       # angle at point b (the knee)
#     a, b, c = map(np.array, (a, b, c))
#     rad = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
#     deg = np.abs(rad * 180.0 / np.pi)
#     return 360 - deg if deg > 180 else deg

# cap = cv2.VideoCapture(0)
# reps = 0
# stage = "up"
# flash_green = 0          # frames left to keep the box green after a rep

# with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#     while cap.isOpened():
#         ok, frame = cap.read()
#         if not ok:
#             break
#         frame = cv2.flip(frame, 1)        # mirror, feels natural
#         h, w = frame.shape[:2]
#         results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

#         down = False
#         legs_visible = False
#         if results.pose_landmarks:
#             lm, P = results.pose_landmarks.landmark, mp_pose.PoseLandmark
#             hip_lm, knee_lm, ankle_lm = lm[P.LEFT_HIP], lm[P.LEFT_KNEE], lm[P.LEFT_ANKLE]

#             # only count if legs are actually visible (not guessed off-screen)
#             if min(hip_lm.visibility, knee_lm.visibility, ankle_lm.visibility) > 0.6:
#                 legs_visible = True
#                 hip   = [hip_lm.x,   hip_lm.y]
#                 knee  = [knee_lm.x,  knee_lm.y]
#                 ankle = [ankle_lm.x, ankle_lm.y]
#                 ang = angle(hip, knee, ankle)

#                 if ang < 100:                 # deep enough → down
#                     stage = "down"
#                     down = True
#                 if ang > 160 and stage == "down":   # stood back up → count
#                     stage = "up"
#                     reps += 1
#                     flash_green = 10          # flash green for ~10 frames

#             mp_draw.draw_landmarks(frame, results.pose_landmarks,
#                                    mp_pose.POSE_CONNECTIONS)

#         # box: green on completion flash, red while down, otherwise plain
#         if flash_green > 0:
#             color = (0, 255, 0)           # green
#             flash_green -= 1
#         elif down:
#             color = (0, 0, 255)           # red
#         else:
#             color = (200, 200, 200)       # neutral
#         cv2.rectangle(frame, (10, 10), (w - 10, h - 10), color, 6)

#         cv2.putText(frame, f"REPS: {reps}", (30, 70),
#                     cv2.FONT_HERSHEY_SIMPLEX, 2, color, 4)

#         # tell you when your legs aren't in frame
#         if not legs_visible:
#             cv2.putText(frame, "STEP BACK - legs not visible", (30, h - 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

#         cv2.imshow("RepClock", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

# cap.release()
# cv2.destroyAllWindows()
# --------------------------------------------------------
# --------------------------------------------------------
# ---------------------Test 2-----------------------------------

# import cv2
# import numpy as np
# import mediapipe as mp
# import time

# mp_pose = mp.solutions.pose
# mp_draw = mp.solutions.drawing_utils

# def angle(a, b, c):                       # angle at point b (the knee)
#     a, b, c = map(np.array, (a, b, c))
#     rad = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
#     deg = np.abs(rad * 180.0 / np.pi)
#     return 360 - deg if deg > 180 else deg

# cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)   # higher-res capture
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# reps = 0
# stage = "up"
# flash_green = 0          # frames left to keep the box green after a rep

# # ---- Stage 2: challenge timer state ----
# active = False           # is a 60s challenge running?
# start_time = 0.0
# DURATION = 60            # seconds
# final_reps = None        # last challenge's final score

# cv2.namedWindow("RepClock", cv2.WINDOW_NORMAL)   # resizable window
# cv2.resizeWindow("RepClock", 1280, 720)

# with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#     while cap.isOpened():
#         ok, frame = cap.read()
#         if not ok:
#             break
#         frame = cv2.flip(frame, 1)        # mirror, feels natural
#         h, w = frame.shape[:2]
#         results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

#         # ---- challenge countdown ----
#         remaining = 0
#         if active:
#             remaining = DURATION - (time.time() - start_time)
#             if remaining <= 0:
#                 remaining = 0
#                 active = False
#                 final_reps = reps         # freeze the score

#         down = False
#         legs_visible = False
#         if results.pose_landmarks:
#             lm, P = results.pose_landmarks.landmark, mp_pose.PoseLandmark
#             l_hip, l_knee, l_ankle = lm[P.LEFT_HIP],  lm[P.LEFT_KNEE],  lm[P.LEFT_ANKLE]
#             r_hip, r_knee, r_ankle = lm[P.RIGHT_HIP], lm[P.RIGHT_KNEE], lm[P.RIGHT_ANKLE]

#             # both legs must be visible now
#             vis = min(l_hip.visibility, l_knee.visibility, l_ankle.visibility,
#                       r_hip.visibility, r_knee.visibility, r_ankle.visibility)

#             if vis > 0.6:
#                 legs_visible = True
#                 left_ang  = angle([l_hip.x, l_hip.y], [l_knee.x, l_knee.y], [l_ankle.x, l_ankle.y])
#                 right_ang = angle([r_hip.x, r_hip.y], [r_knee.x, r_knee.y], [r_ankle.x, r_ankle.y])

#                 # BOTH knees must bend deep -> bending one foot no longer counts
#                 if max(left_ang, right_ang) < 100:            # both knees deep
#                     stage = "down"
#                     down = True
#                 if min(left_ang, right_ang) > 160 and stage == "down":   # both legs straight
#                     stage = "up"
#                     flash_green = 10
#                     if active:                # only score during the challenge
#                         reps += 1

#             mp_draw.draw_landmarks(frame, results.pose_landmarks,
#                                    mp_pose.POSE_CONNECTIONS)

#         # box: green on completion flash, red while down, otherwise plain
#         if flash_green > 0:
#             color = (0, 255, 0)           # green
#             flash_green -= 1
#         elif down:
#             color = (0, 0, 255)           # red
#         else:
#             color = (200, 200, 200)       # neutral
#         cv2.rectangle(frame, (10, 10), (w - 10, h - 10), color, 6)

#         cv2.putText(frame, f"REPS: {reps}", (30, 70),
#                     cv2.FONT_HERSHEY_SIMPLEX, 2, color, 4)

#         # ---- timer / status readout ----
#         if active:
#             cv2.putText(frame, f"TIME: {int(remaining)}", (30, 140),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
#         elif final_reps is not None:
#             cv2.putText(frame, f"FINAL: {final_reps}", (30, 140),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 0), 4)
#             cv2.putText(frame, "Press S to go again", (30, 185),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
#         else:
#             cv2.putText(frame, "Press S to start 60s challenge", (30, 140),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

#         # tell you when your legs aren't in frame
#         if not legs_visible:
#             cv2.putText(frame, "STEP BACK - legs not visible", (30, h - 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

#         cv2.imshow("RepClock", frame)

#         key = cv2.waitKey(1) & 0xFF
#         if key == ord('q'):
#             break
#         if key == ord('s'):               # start / restart a 60s challenge
#             active = True
#             start_time = time.time()
#             reps = 0
#             stage = "up"
#             final_reps = None

# cap.release()
# cv2.destroyAllWindows()
# --------------------------------------------------------
# ---------------------Test 3-----------------------------------

import cv2
import numpy as np
import mediapipe as mp
import time
import json
import threading
import asyncio
import websockets

# ---- CHANGE THIS for two laptops: use the referee laptop's LAN IP, e.g. "ws://192.168.1.42:8765" ----
# SERVER = "ws://localhost:8765"
SERVER = "ws://192.168.56.1:8765"   # <-- change this to the referee's IP address

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

def angle(a, b, c):                       # angle at point b (the knee)
    a, b, c = map(np.array, (a, b, c))
    rad = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    deg = np.abs(rad * 180.0 / np.pi)
    return 360 - deg if deg > 180 else deg

# ---- shared state between camera loop (main thread) and network (bg thread) ----
state = {
    "me": None,             # "P1" or "P2", assigned by referee
    "my_reps": 0,
    "opp_reps": 0,
    "active": False,        # True while the match clock is running
    "duration": 60,
    "start_ts": 0.0,
    "phase": "connecting",  # connecting / waiting / playing / done / full / error
    "winner": None,
}

def other(pid):
    return "P2" if pid == "P1" else "P1"

# ---- networking runs in the background so it never freezes the camera ----
async def net():
    try:
        async with websockets.connect(SERVER) as ws:
            state["phase"] = "waiting"

            async def sender():                 # push my rep count up whenever it changes
                last = -1
                while True:
                    if state["active"] and state["my_reps"] != last:
                        last = state["my_reps"]
                        try:
                            await ws.send(json.dumps({"type": "reps", "reps": last}))
                        except Exception:
                            return
                    await asyncio.sleep(0.05)

            asyncio.create_task(sender())

            async for raw in ws:                # receive referee messages
                data = json.loads(raw)
                t = data.get("type")
                if t == "assigned":
                    state["me"] = data["you"]
                elif t == "start":
                    state["duration"] = data["duration"]
                    state["start_ts"] = time.time()
                    state["my_reps"] = 0
                    state["opp_reps"] = 0
                    state["active"] = True
                    state["phase"] = "playing"
                elif t == "scores":
                    me = state["me"]
                    sc = data["scores"]
                    if me and other(me) in sc:
                        state["opp_reps"] = sc[other(me)]
                elif t == "end":
                    state["active"] = False
                    state["winner"] = data["winner"]
                    me = state["me"]
                    sc = data["scores"]
                    if me and other(me) in sc:
                        state["opp_reps"] = sc[other(me)]
                    state["phase"] = "done"
                elif t == "full":
                    state["phase"] = "full"
                    return
    except Exception as e:
        print("Network error:", e)
        state["phase"] = "error"

threading.Thread(target=lambda: asyncio.run(net()), daemon=True).start()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

stage = "up"
flash_green = 0

cv2.namedWindow("RepClock", cv2.WINDOW_NORMAL)
cv2.resizeWindow("RepClock", 1280, 720)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # local countdown; stop counting the instant time runs out
        remaining = 0
        if state["active"]:
            remaining = state["duration"] - (time.time() - state["start_ts"])
            if remaining <= 0:
                remaining = 0
                state["active"] = False

        down = False
        legs_visible = False
        if results.pose_landmarks:
            lm, P = results.pose_landmarks.landmark, mp_pose.PoseLandmark
            l_hip, l_knee, l_ankle = lm[P.LEFT_HIP],  lm[P.LEFT_KNEE],  lm[P.LEFT_ANKLE]
            r_hip, r_knee, r_ankle = lm[P.RIGHT_HIP], lm[P.RIGHT_KNEE], lm[P.RIGHT_ANKLE]

            vis = min(l_hip.visibility, l_knee.visibility, l_ankle.visibility,
                      r_hip.visibility, r_knee.visibility, r_ankle.visibility)

            if vis > 0.6:
                legs_visible = True
                left_ang  = angle([l_hip.x, l_hip.y], [l_knee.x, l_knee.y], [l_ankle.x, l_ankle.y])
                right_ang = angle([r_hip.x, r_hip.y], [r_knee.x, r_knee.y], [r_ankle.x, r_ankle.y])

                if max(left_ang, right_ang) < 100:            # both knees deep
                    stage = "down"
                    down = True
                if min(left_ang, right_ang) > 160 and stage == "down":   # both legs straight
                    stage = "up"
                    flash_green = 10
                    if state["active"]:                       # only score during the match
                        state["my_reps"] += 1

            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        if flash_green > 0:
            color = (0, 255, 0); flash_green -= 1
        elif down:
            color = (0, 0, 255)
        else:
            color = (200, 200, 200)
        cv2.rectangle(frame, (10, 10), (w - 10, h - 10), color, 6)

        # scoreboard: you vs opponent
        cv2.putText(frame, f"YOU: {state['my_reps']}", (30, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.6, color, 4)
        cv2.putText(frame, f"OPP: {state['opp_reps']}", (30, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 200, 0), 4)

        # status line driven by referee phase
        phase = state["phase"]
        if phase == "connecting":
            msg, mc = "Connecting to referee...", (255, 255, 255)
        elif phase == "waiting":
            msg, mc = "Waiting for opponent...", (255, 255, 255)
        elif phase == "playing":
            msg, mc = f"MATCH ON  -  TIME: {int(remaining)}", (0, 255, 255)
        elif phase == "done":
            me, win = state["me"], state["winner"]
            res = "TIE" if win == "TIE" else ("YOU WIN!" if win == me else "YOU LOSE")
            msg, mc = f"{res}   (you {state['my_reps']} - {state['opp_reps']} opp)", (0, 255, 0)
        elif phase == "full":
            msg, mc = "Match full - two players already connected", (0, 0, 255)
        else:
            msg, mc = "Cannot reach referee - check SERVER address", (0, 0, 255)
        cv2.putText(frame, msg, (30, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.9, mc, 2)

        if not legs_visible:
            cv2.putText(frame, "STEP BACK - legs not visible", (30, h - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow("RepClock", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()