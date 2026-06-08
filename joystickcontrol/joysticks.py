# Read joystick input, compute IK, and optionally actuate servos.
import pygame
# from adafruit_servokit import ServoKit
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from math.ik_solver import IKSolver

pygame.init()
pygame.joystick.init()
# kit = ServoKit(channels=16)

joysticks = []
for i in range(pygame.joystick.get_count()):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    joysticks.append(joy)
    print(f"Initialized Joystick {i}: {joy.get_name()}")

w = pygame.display.set_mode([500,500])
running = True
clawActive = False
aiMode = False
originPl = True
DEADZONE = 0.1
vector1 = [0.0, 0.0, 0.0]
ik_solver = IKSolver()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle joystick events
        elif event.type == pygame.JOYBUTTONDOWN:
            # You can map specific buttons to in-game actions
            if event.button == 0:
                if clawActive:
                    print("Claw deactivated")
                    clawActive = False
                    # kit.servo[10].angle = 0
                else:
                    print("Claw activated")
                    clawActive = True
                    # kit.servo[10].angle = 180
            
            elif event.button == 1:
                if aiMode:
                     print("AI Mode deactivated")
                     aiMode = False
                else:
                    print("AI Mode activated")
                    aiMode = True
                    
            elif event.button == 2:
                # kit.servo[10].angle = 180
                # kit.servo[11].angle = 0
                # kit.servo[12].angle = 0
                # kit.servo[13].angle = 0
                # kit.servo[14].angle = 0
                # kit.servo[15].angle = 0
                print("Robot returned to original location")
            
            elif event.button == 3:
                # kit.servo[10].angle = 40
                # kit.servo[11].angle = 110
                # kit.servo[12].angle = 150
                # kit.servo[13].angle = 80
                # kit.servo[14].angle = 0
                # kit.servo[15].angle = 180
                time.sleep(0.5)
                # kit.servo[15].angle = 0
                # kit.servo[10].angle = 180
                # kit.servo[11].angle = 135
                # kit.servo[12].angle = 135
                # kit.servo[13].angle = 135
                # kit.servo[14].angle = 180
                print("Preset position activated")

        elif event.type == pygame.JOYAXISMOTION:

            if event.axis == 0:
                if abs(event.value) > DEADZONE:
                    vector1[0] = event.value * 3
                else:
                    vector1[0] = 0.0
            elif event.axis == 1:
                if abs(event.value) > DEADZONE:
                    vector1[1] = -event.value * 3
                else:
                    vector1[1] = 0.0
            elif event.axis == 3:
                if abs(event.value) > DEADZONE:
                    vector1[2] = -1 * (event.value * 3)
                else:
                    vector1[2] = 0.0
            
            # print("3D Vector:", vector1)
            vector_pass = f"{vector1[0]} {vector1[1]} {vector1[2]}"
            # Format vector as 'x y z' for the IK solver
            angles = ik_solver.update(vector_pass)
            print(vector_pass)
            # print("Servo Angles:", angles)
            # kit.servo[11].angle = angles['A1']  # base
            # kit.servo[12].angle = angles['A2']  # shoulder
            # kit.servo[13].angle = angles['A3']  # elbow
            # kit.servo[14].angle = angles['A4']  # wrist
            print(angles["A1"])
            print(angles["A2"])
            print(angles["A3"])
            print(angles["A4"])

        elif event.type == pygame.JOYHATMOTION:
            print(f"Hat {event.hat} moved to position {event.value}")

    pygame.display.flip()
    w.fill((0,0,0))

    