import pygame
import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

pygame.init()
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Joystick connected:", joystick.get_name())

while True:
    pygame.event.pump()
    
    # Left joystick Y axis (axis 1), -1 to 1
    y = joystick.get_axis(1)
    
    # Map -1 to 1 → 0 to 180
    angle = (y + 1) / 2 * 180
    
    kit.servo[15].angle = angle
    print(f"Angle: {angle:.1f}")
    
    time.sleep(0.05)