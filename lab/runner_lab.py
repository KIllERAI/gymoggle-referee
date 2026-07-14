"""
GymOggle — RUNNER CONTROLLER  (FINAL: 4 MECHANICS)
==================================================
No jog detection. No speed. No stillness. No swipes. The runner always runs.
The OBSTACLES are the workout.

  JUMP        -> BOTH feet leave the ground   (jogging can never fake this)
  DUCK        -> upper body bends down
  RAISE LEFT  -> left hand above shoulder     -> move to the left lane
  RAISE RIGHT -> right hand above shoulder    -> move to the right lane

Why RAISE and not a swipe: jogging IS arms swinging across your body, so a
cross-body swipe fights the activity itself. Hands NEVER go above the shoulders
while jogging -> a raise is structurally impossible to false-fire. It's also a
real shoulder workout on its own.

CALIBRATION (3 steps, ~13s): learns your resting pose, your jump height, your
duck depth, and which hand is on which side of the mirrored frame.
Saved to calib.json, auto-loaded next run.

KEYS   q quit · c recalibrate · x delete profile · f fullscreen
"""

import cv2, time, math, json, os
import numpy as np
import mediapipe as mp

mp_pose=mp.solutions.pose; mp_draw=mp.solutions.drawing_utils
mp_styles=mp.solutions.drawing_styles

L_SH,R_SH=11,12; L_WR,R_WR=15,16
L_HIP,R_HIP=23,24; L_ANK,R_ANK=27,28

CALIB_FILE="calib.json"
TRIGGER_FRAC={"foot":.55,"duck":.55}     # fire at 55% of YOUR demonstrated peak
FLOOR={"foot":.05,"duck":.06}            # safety floors so noise can't hair-trigger

RAISE_ON, RAISE_OFF = 0.12, 0.02         # hand above shoulder (in torso-lengths)
GESTURE_COOL = 0.35                      # anti-double-fire
LOCK_AFTER   = 0.60                      # jump/duck lock out steering (arms fly up)
RUN_MPS      = 6.0                       # the runner's CONSTANT pace

CY,MG,GD,BN=(214,224,34),(126,46,255),(63,210,255),(240,240,250)
RD,DIM,BG=(80,80,255),(120,115,135),(24,18,30)

STEPS=[("STAND STILL","Arms relaxed. Learning your resting pose.",3.0),
       ("JUMP! JUMP!","Hop a few times — both feet off the ground.",5.0),
       ("DUCK! DUCK!","Bend your upper body down a few times.",5.0)]


def measure(lms):
    sh_y=(lms[L_SH].y+lms[R_SH].y)/2
    hip_y=(lms[L_HIP].y+lms[R_HIP].y)/2
    ank_y=(lms[L_ANK].y+lms[R_ANK].y)/2
    torso=abs(hip_y-sh_y) or 1e-3
    leg=abs(ank_y-hip_y) or 1e-3
    return dict(sh_y=sh_y, torso=torso, leg=leg,
                ankL=lms[L_ANK].y, ankR=lms[R_ANK].y,
                wrLx=lms[L_WR].x, wrRx=lms[R_WR].x)


class Calibrator:
    def __init__(self):
        self.step=0; self.t0=None; self.buf=[]; self.done=False
        self.rest=None; self.peak={"foot":0.,"duck":0.}
        self.left_id=None; self.right_id=None

    def info(self):
        n,s,d=STEPS[self.step]
        return n,s,(max(0.,d-(time.time()-self.t0)) if self.t0 else d)

    def feed(self,lms,now):
        q=measure(lms)
        if self.t0 is None: self.t0=now
        _,_,dur=STEPS[self.step]; el=now-self.t0

        if self.step==0:                                   # resting pose
            self.buf.append((q["torso"],q["leg"],q["ankL"],q["ankR"],q["wrLx"],q["wrRx"]))
            if el>=dur and len(self.buf)>10:
                a=np.array(self.buf)
                self.rest={"torso":float(np.median(a[:,0])),"leg":float(np.median(a[:,1])),
                           "ankL":float(np.median(a[:,2])),"ankR":float(np.median(a[:,3]))}
                # mirrored frame scrambles MediaPipe's left/right labels — so just look
                # at which wrist actually sits further LEFT on screen.
                self.left_id  = L_WR if float(np.median(a[:,4])) < float(np.median(a[:,5])) else R_WR
                self.right_id = R_WR if self.left_id==L_WR else L_WR
                self._next(now)
            return

        R=self.rest
        if self.step==1:                                   # jump -> foot lift peak
            fL=(R["ankL"]-q["ankL"])/R["leg"]; fR=(R["ankR"]-q["ankR"])/R["leg"]
            self.peak["foot"]=max(self.peak["foot"], min(fL,fR))   # BOTH feet -> the lower one
            if el>=dur: self._next(now)
            return
        if self.step==2:                                   # duck -> torso squash peak
            self.peak["duck"]=max(self.peak["duck"], (R["torso"]-q["torso"])/R["torso"])
            if el>=dur: self.done=True
            return

    def _next(self,now): self.step+=1; self.t0=now; self.buf=[]

    def profile(self):
        return {"rest":self.rest,
                "thr":{k:max(FLOOR[k], self.peak[k]*TRIGGER_FRAC[k]) for k in self.peak},
                "peak":self.peak, "left_id":self.left_id, "right_id":self.right_id}


class Controller:
    """Turns a body into 4 game inputs. That's all it does."""
    def __init__(self,p):
        self.R=p["rest"]; self.T=p["thr"]; self.peak=p["peak"]
        self.left_id=p["left_id"]; self.right_id=p["right_id"]
        self.fire={"JUMP":0.,"DUCK":0.,"LEFT":0.,"RIGHT":0.}
        self.count={"JUMP":0,"DUCK":0,"LEFT":0,"RIGHT":0}
        self.armed={"L":True,"R":True}
        self.lane=1
        self.jump_until=0.; self.duck_until=0.; self.lock_until=0.
        self.dist=0.

    def _f(self,n,now):
        if now-self.fire[n]<GESTURE_COOL: return False
        self.fire[n]=now; self.count[n]+=1; return True

    def update(self,lms,now,dt):
        q=measure(lms); R=self.R; T=self.T; m={}
        self.dist += RUN_MPS*dt                 # constant pace — the player can't change it

        # ---- JUMP: both feet off the ground ----
        fL=(R["ankL"]-q["ankL"])/R["leg"]; fR=(R["ankR"]-q["ankR"])/R["leg"]
        both = fL>T["foot"] and fR>T["foot"]
        if both and self._f("JUMP",now):
            self.jump_until=now+.45; self.lock_until=now+LOCK_AFTER
        jumping = now<self.jump_until

        # ---- DUCK: torso squashes ----
        squash=(R["torso"]-q["torso"])/R["torso"]
        ducking_now = squash>T["duck"]
        if ducking_now and self._f("DUCK",now):
            self.duck_until=now+.5; self.lock_until=now+LOCK_AFTER
        ducking = now<self.duck_until

        # ---- STEER: raise a hand above the shoulder ----
        # jump/duck OWN the frame (arms fly up on a jump), so steering is locked out
        blocked = jumping or ducking or both or ducking_now or now<self.lock_until
        raiseL=(q["sh_y"]-lms[self.left_id].y)/R["torso"]
        raiseR=(q["sh_y"]-lms[self.right_id].y)/R["torso"]

        if blocked:
            self.armed["L"]=self.armed["R"]=False       # can't fire on the way down either
        else:
            onL, onR = raiseL>RAISE_ON, raiseR>RAISE_ON
            if onL and not onR and self.armed["L"] and self._f("LEFT",now):
                self.lane=max(0,self.lane-1); self.armed["L"]=False
            if onR and not onL and self.armed["R"] and self._f("RIGHT",now):
                self.lane=min(2,self.lane+1); self.armed["R"]=False
            if raiseL<RAISE_OFF: self.armed["L"]=True   # hand back down -> can fire again
            if raiseR<RAISE_OFF: self.armed["R"]=True

        m.update(footL=fL,footR=fR,both=both,squash=squash,
                 raiseL=raiseL,raiseR=raiseR,blocked=blocked,
                 jumping=jumping,ducking=ducking,dist=self.dist)
        return m


# ------------------------------- HUD -------------------------------------
def panel(img,lines,x,y,s=.6,col=BN):
    fh=int(30*s)+6
    w=max((cv2.getTextSize(t,cv2.FONT_HERSHEY_SIMPLEX,s,1)[0][0] for t in lines),default=0)
    ov=img.copy(); cv2.rectangle(ov,(x-9,y-9),(x+w+9,y+fh*len(lines)+9),BG,-1)
    cv2.addWeighted(ov,.6,img,.4,0,img)
    for i,t in enumerate(lines):
        cv2.putText(img,t,(x,y+fh*i+int(21*s)),cv2.FONT_HERSHEY_SIMPLEX,s,col,1,cv2.LINE_AA)

def lamp(img,x,y,on,label,col):
    cv2.circle(img,(x,y),14,col if on else (55,50,62),-1); cv2.circle(img,(x,y),14,DIM,1)
    cv2.putText(img,label,(x+22,y+6),cv2.FONT_HERSHEY_SIMPLEX,.6,col if on else DIM,1,cv2.LINE_AA)

def track(img,ox,oy,w,h,c,m):
    cv2.rectangle(img,(ox,oy),(ox+w,oy+h),(34,26,42),-1)
    cv2.rectangle(img,(ox,oy),(ox+w,oy+h),DIM,1)
    lw=w//3
    for i in (1,2):
        x=ox+i*lw
        for yy in range(oy+40,oy+h-8,22): cv2.line(img,(x,yy),(x,yy+11),(70,64,82),1)
    cx=ox+c.lane*lw+lw//2; base=oy+h-30
    y=base-(38 if m.get("jumping") else 0); bh=16 if m.get("ducking") else 30
    col=GD if m.get("jumping") else (MG if m.get("ducking") else CY)
    cv2.circle(img,(cx,y-bh-8),8,col,-1)
    cv2.rectangle(img,(cx-7,y-bh),(cx+7,y),col,-1)
    if not m.get("ducking"):
        sw=int(6*math.sin(time.time()*13))
        cv2.line(img,(cx-3,y),(cx-6+sw,y+16),col,3)
        cv2.line(img,(cx+3,y),(cx+6-sw,y+16),col,3)
    cv2.line(img,(ox,base+18),(ox+w,base+18),(80,74,92),2)
    cv2.putText(img,f"RUNNING   {m.get('dist',0):.0f} m",(ox+14,oy+28),
                cv2.FONT_HERSHEY_SIMPLEX,.55,CY,1,cv2.LINE_AA)


def main():
    cap=cv2.VideoCapture(0)
    if not cap.isOpened(): print("no webcam"); return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280); cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    WIN="GymOggle Runner"; cv2.namedWindow(WIN,cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(WIN,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN); full=True
    pose=mp_pose.Pose(min_detection_confidence=.5,min_tracking_confidence=.5,model_complexity=1)

    prof=None; ctl=None; cal=None
    if os.path.exists(CALIB_FILE):
        try:
            p=json.load(open(CALIB_FILE))
            if all(k in p for k in ("rest","thr","left_id")):
                prof=p; ctl=Controller(p); print("loaded calibration ('c' to redo)")
        except Exception: pass
    if ctl is None: cal=Calibrator(); print("calibrating — stand still...")

    prev=time.time()
    while True:
        ok,frame=cap.read()
        if not ok: break
        frame=cv2.flip(frame,1); H,W=frame.shape[:2]
        res=pose.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        now=time.time(); dt=max(1e-3,min(.1,now-prev)); prev=now; m={}

        if res.pose_landmarks:
            mp_draw.draw_landmarks(frame,res.pose_landmarks,mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_styles.get_default_pose_landmarks_style())
            lms=res.pose_landmarks.landmark
            if cal and not cal.done:
                cal.feed(lms,now)
                n,s,left=cal.info()
                panel(frame,[f"[{cal.step+1}/3]  {n}", s, f"{left:.1f}s"],W//2-300,70,.9,GD)
                panel(frame,[f"jump peak {cal.peak['foot']:.2f}   duck peak {cal.peak['duck']:.2f}"],
                      30,H-200,.6,(200,235,255))
                if cal.done:
                    prof=cal.profile(); ctl=Controller(prof)
                    json.dump(prof,open(CALIB_FILE,"w"),indent=1)
                    print("CALIBRATED:",json.dumps(prof["thr"],indent=1))
            elif ctl:
                m=ctl.update(lms,now,dt)
        else:
            panel(frame,["NO PERSON — step back, WHOLE BODY in frame"],W//2-250,H//2,.8,RD)

        if ctl and not (cal and not cal.done):
            lx,ly=30,46
            lamp(frame,lx,ly,     m.get("jumping"),"JUMP",GD)
            lamp(frame,lx,ly+42,  m.get("ducking"),"DUCK",MG)
            lamp(frame,lx,ly+84,  now-ctl.fire["LEFT"]<.4, "RAISE LEFT",BN)
            lamp(frame,lx,ly+126, now-ctl.fire["RIGHT"]<.4,"RAISE RIGHT",BN)
            T=ctl.T
            panel(frame,[
                f"feet  L{m.get('footL',0):+.2f} R{m.get('footR',0):+.2f}   fire > {T['foot']:.2f}"
                + ("   BOTH UP" if m.get("both") else ""),
                f"duck  {m.get('squash',0):+.2f}                fire > {T['duck']:.2f}",
                f"raise L{m.get('raiseL',0):+.2f} R{m.get('raiseR',0):+.2f}   fire > {RAISE_ON:.2f}"
                + ("   [LOCKED]" if m.get("blocked") else ""),
                f"lane {ctl.lane}",
            ],30,220,.6,(200,235,255))
            c=ctl.count
            panel(frame,[f"jump {c['JUMP']}   duck {c['DUCK']}   left {c['LEFT']}   right {c['RIGHT']}"],
                  30,H-190,.6,GD)
            track(frame,W-380,46,340,300,ctl,m)

        panel(frame,["c recalibrate   x delete profile   f fullscreen   q quit"],30,H-130,.5,DIM)
        cv2.imshow(WIN,frame)
        k=cv2.waitKey(1)&0xFF
        if k in (ord('q'),27): break
        elif k==ord('c'): cal=Calibrator(); ctl=None; print("recalibrating...")
        elif k==ord('x') and os.path.exists(CALIB_FILE): os.remove(CALIB_FILE); print("deleted")
        elif k==ord('f'):
            full=not full
            cv2.setWindowProperty(WIN,cv2.WND_PROP_FULLSCREEN,
                cv2.WINDOW_FULLSCREEN if full else cv2.WINDOW_NORMAL)

    cap.release(); cv2.destroyAllWindows()
    if prof: print("\n=== CONTROLLER PROFILE ===\n"+json.dumps(prof["thr"],indent=1))

if __name__=="__main__": main()