import pygame
# from adafruit_servokit import ServoKit
import time
import matplotlib.pyplot as plt
from vector import vector
pygame.init()
pygame.joystick.init()
# kit = ServoKit(channels=16)
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D





plt.show()


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
            
            vector1 = [0, 0, 0]

            if event.axis == 0:
                vector1[0] = event.value * 3
            elif event.axis == 1:
                vector1[1] = -event.value * 3
            elif event.axis == 3:
                vector1[2] = event.value * 3
            
            # print("3D Vector:", vector1)
            vector_pass = f"{float(vector1[0])} {float(vector1[1])} {float(vector1[2])}"
            print(vector_pass)
            angles = vector().update(vector_pass)

            # print("Servo Angles:", angles)
            # kit.servo[11].angle = angles['A1']  # base
            # kit.servo[12].angle = angles['A2']  # shoulder
            # kit.servo[13].angle = angles['A3']  # elbow
            # kit.servo[14].angle = angles['A4']  # wrist
            # print(angles)
            pygame.draw.line(w, (255,255,255), (250,250), (250 + vector1[0]*50, 250 - vector1[1]*50), 5)
            
        elif event.type == pygame.JOYHATMOTION:
            print(f"Hat {event.hat} moved to position {event.value}")

        pygame.display.flip()
        w.fill((0,0,0))

    