# C.O.R.I Hand Tracking - Computer Vision Interface
# This is the coolest part of the project! It uses your webcam to track your hand 
# landmarks and converts your hand movements into robot joint commands.
# It's basically like controlling the robot with "The Force".

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import sys
import math

# Add parent directory for ik_solver access.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ik_solver import IKSolver
import numpy as np
import pygame
<<<<<<< Updated upstream
import websockets
import asyncio
import json
pygame.init()
pygame.joystick.init()

HOST = "192.168.1.20"  # Replace with your Pi's IP or "localhost"
PORT = 8765

# Initialize IK solver for calculating joint angles from hand position
ik_solver = IKSolver()
=======

# Initialize Pygame and our IK Solver.
pygame.init()
pygame.joystick.init()

vec = IKSolver()

# We need a specific model file for MediaPipe to work. 
# If it's not here, we'll just download it automatically.
>>>>>>> Stashed changes
MODEL = "hand_landmarker.task"
if not os.path.exists(MODEL):
    print("Downloading model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task",
        MODEL
    )
    print("Done.")

latest_result = None

<<<<<<< Updated upstream

def in_range(value, target, deviance):
    if value <= target + deviance and value >= target - deviance:
        return True
    else:
        return False
async def main(host, port, values):
    uri = f"ws://{host}:{port}/ws"
    try:
        async with websockets.connect(uri) as ws:
            payload = [int(v) for v in values]
            await ws.send(json.dumps(payload, separators=(",", ":")))
            # print(f"Successfully sent {payload} to {uri}")
    except Exception as e:
        print(f"Failed to connect or send: {e}")

=======
# This callback is called every time the AI finishes processing a frame.
# It updates our latest_result so the main loop can use it.
>>>>>>> Stashed changes
def callback(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result

options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=MODEL),
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback=callback
)

# These connections define how to draw the hand "skeleton" on the screen.
# It's just a list of which landmarks should have lines between them.
CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17)
]

cap = cv2.VideoCapture(0)
ts = 0
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
angles = [0,0,0,0, 0]
is_rotating = False
w = pygame.display.set_mode((800, 600))
with vision.HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        landmarker.detect_async(mp_image, ts)
        ts += 1
        cv2.line(frame, (630, 360), (650, 360), (255, 0, 0), 2)
        cv2.line(frame, (640, 350), (640, 370), (255, 0, 0), 2)
        if latest_result:
            for hand_landmarks in latest_result.hand_landmarks:
                pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
                
                
                a,b = pts[12]
                x,y = pts[9]

                keys = pygame.key.get_pressed()

                
                    
                for a, b in CONNECTIONS:
                    cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)
                for pt in pts:
                    cv2.circle(frame, pt, 4, (0, 0, 255), -1)
                if pts:
                    x_coords = [p[0] for p in pts]
                    y_coords = [p[1] for p in pts]
                    x1, y1 = min(x_coords) - 20, min(y_coords) - 20
                    x2, y2 = max(x_coords) + 20, max(y_coords) + 20
                    
                    if not is_rotating:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    
                    if is_rotating:
                        n0, n1 = pts[9]
                        cv2.circle(frame, (x, y), 100, (255, 0, 0), 2)
                        distance = math.fabs((b-y))/(math.fabs(a - x))
                        angle = np.cos((distance - 50) / 100 * math.pi) * 90
                        cv2.line(frame, (x,y), (n0, n1),(0, 255, 0), 2)
                        angles[3] = int(angle)
                    
                    # INDEX To THUMB Touching
                    if in_range(pts[4][0], pts[8][0], 15) and in_range(pts[4][1], pts[8][1], 15):
                        print("grab")
                        angles[4] = 180
                    
                    # Point gesture (index, middle, and ring fingers all touching)
                    if in_range(pts[11][0], pts[9][0], 15) and in_range(pts[11][1], pts[9][1], 15) and in_range(pts[13][0], pts[15][0], 15) and in_range(pts[13][1], pts[15][1], 15) or in_range(pts[19][0], pts[17][0], 15) and in_range(pts[19][1], pts[17][1], 15) and in_range(pts[11][1], pts[9][1], 15) and in_range(pts[13][0], pts[15][0], 15) and in_range(pts[13][1], pts[15][1], 15) or in_range(pts[3][0], pts[7][0], 15) and in_range(pts[3][1], pts[7][1], 15) and in_range(pts[2][0], pts[6][0], 15) and in_range(pts[2][1], pts[6][1], 15):
                        print("point")

                    width = x2 - x1
                    height = y2 - y1

                    max_disx = 640   
                    max_disy = 1475100 - 88377
                    max_disz = 360 

                    area = width * height   
                    # print(f"Hand area: {area}")

                    set_y = 88377
                    
                    disy = area - set_y
                    x,z = pts[9]
                    
                    # cv2.line(frame, (640, 360), (x,z), (255, 255, 0), 2)
                    
                    disx = x - 640
                    disz = z - 360
                    
                    # print(f"distance from center: ({disx}, {disz})")
                    # We scale the distances to get a 3D vector our solver can understand.
                    scaled_x = (disx / max_disx) * 3
                    scaled_y = (disy / max_disy) * 3
                    scaled_z = (disz / max_disz) * 3
                    
                    # Finally, we pass the vector to the IK solver to get the joint angles.
                    vector_pass = f"{scaled_x} {scaled_y} {scaled_z}"
                    angles_dict = ik_solver.update(vector_pass)
                    # Update angles with IK solution (keep angles[4] for grabber/claw)
                    angles[0] = int(angles_dict['A1'])
                    angles[1] = int(angles_dict['A2'])
                    angles[2] = int(angles_dict['A3'])
                    angles[3] = int(angles_dict['A4'])
                    joint_angles = angles
                    try:
                        asyncio.run(main(HOST, PORT, joint_angles))
                    except Exception as e:
                        #REPLACE WITH LOGGING
                        pass
                        # logs.append(f"Failed to send data: {e}")
                    if keys[pygame.K_r]:
                        is_rotating = True
                    if keys[pygame.K_s]:
                        is_rotating = False
                        
        cv2.imshow("Hand Tracking", frame)
        pygame.display.flip()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()