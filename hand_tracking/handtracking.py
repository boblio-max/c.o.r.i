import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import math
from math.ik_solver import IKSolver
import numpy as np
import pygame

pygame.init()
pygame.joystick.init()

vec = IKSolver()
MODEL = "hand_landmarker.task"
if not os.path.exists(MODEL):
    print("Downloading model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task",
        MODEL
    )
    print("Done.")

latest_result = None

def callback(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result

options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=MODEL),
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback=callback
)

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
                if pts[12] == pts[8] and pts[8] == pts[4]:
                    print("grab")
                    angles[4] = 180
                
                a,b = pts[12]
                x,y = pts[9]

                keys = pygame.key.get_pressed()

                if keys[pygame.K_R]:
                    if not is_rotating:
                        is_rotating = True
                        cv2.circle(frame, (x, y), 100, (255, 0, 0), 2)
                        distance = math.fabs((b-y))/(math.fabs(a - x))
                        angle = np.cosine((distance - 50) / 100 * math.pi) * 90
                        angles[3] = int(angle)
                    else:
                        is_rotating = not is_rotating
                    
                for a, b in CONNECTIONS:
                    cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)
                for pt in pts:
                    cv2.circle(frame, pt, 4, (0, 0, 255), -1)
                if pts:
                    x_coords = [p[0] for p in pts]
                    y_coords = [p[1] for p in pts]
                    x1, y1 = min(x_coords) - 20, min(y_coords) - 20
                    x2, y2 = max(x_coords) + 20, max(y_coords) + 20
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    
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
                    
                    cv2.line(frame, (640, 360), (x,z), (255, 255, 0), 2)
                    
                    disx = x - 640
                    disz = z - 360
                    
                    # print(f"distance from center: ({disx}, {disz})")
                    scaled_x = (disx / max_disx) * 3
                    scaled_y = (disy / max_disy) * 3
                    scaled_z = (disz / max_disz) * 3
                    
                    # print(f"3d vector: ({scaled_x}, {scaled_y}, {scaled_z})")
                    vector_pass = f"{scaled_x} {scaled_y} {scaled_z}"
                    angles = vec.update(vector_pass)
                    # print(f"Servo Angles: {angles}")

            
        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()