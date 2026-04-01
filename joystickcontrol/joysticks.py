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
        # process events for non-axis actions
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    if clawActive:
                        print("Claw deactivated")
                        clawActive = False
                    else:
                        print("Claw activated")
                        clawActive = True
                elif event.button == 1:
                    aiMode = not aiMode
                    print("AI Mode", "activated" if aiMode else "deactivated")
                elif event.button == 2:
                    print("Robot returned to original location")
                elif event.button == 3:
                    print("Preset position activated")

        # Poll joystick axes each frame to construct full vector (left stick X/Y + right Y / triggers for Z)
        vector1 = [0.0, 0.0, 0.0]
        if len(joysticks) > 0:
            j0 = joysticks[0]
            naxes = j0.get_numaxes()
            ax0 = j0.get_axis(0) if naxes > 0 else 0.0
            ax1 = j0.get_axis(1) if naxes > 1 else 0.0
            # choose axis for Z
            z = 0.0
            if naxes > 3:
                z = j0.get_axis(3)
            elif naxes > 2:
                z = j0.get_axis(2)
            vector1 = [ax0 * 3.0, -ax1 * 3.0, z * 3.0]

            vector_pass = f"{float(vector1[0])} {float(vector1[1])} {float(vector1[2])}"
            try:
                angles = vector().update(vector_pass)
                print("Servo Angles:", angles)
            except Exception as e:
                print("IK error:", e)

        # draw
        w.fill((0,0,0))
        pygame.draw.line(w, (255,255,255), (250,250), (250 + vector1[0]*50, 250 - vector1[1]*50), 5)
        pygame.display.flip()
            # kit.servo[13].angle = angles['A3']  # elbow

            # kit.servo[14].angle = angles['A4']  # wrist
