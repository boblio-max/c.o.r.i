# AI MODE TOGGLE
# LOGS DISPLAY
# ERRORS OBJECT FOR EASY ACCESS - TODAY
import pygame
import sys
from errors import *
import math
import os


pygame.init()
pygame.joystick.init()

width, height = 700,700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("C.O.R.I DASHBOARD")

WHITE = (255, 255, 255)
BLUE = (0,0,255)
font = pygame.font.SysFont('Arial', 20)
static_rect = pygame.Rect(10, height//2, (width//2)-10, (height//2)-10)
logs = ["Hello", "how are you"]

font       = pygame.font.SysFont('Consolas', 18)
small_font = pygame.font.SysFont('Consolas', 13)

joint_angles = [90, 180, 90, 90]

CIRCLE_R = 65
col_xs = [width // 6, width // 2.5]
row_ys  = [height // 12 + 30, height // 2 - 110]
circle_positions = []
for r in range(2):
    for c in range(2):
        circle_positions.append((col_xs[c]-5, row_ys[r]))
        
joint_labels = []
for i in range(4):
    joint_labels.append(f"J{i+1}")


joysticks = []
for i in range(pygame.joystick.get_count()):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    joysticks.append(joy)
    print(f"Initialized Joystick {i}: {joy.get_name()}")


red_button = (255,255,255)
blue_button = (255,255,255)
green_button = (255,255,255)
yellow_button = (255,255,255)

# Game loop
is_clicked = False
is_clicked1 = False
is_clicked2 = False
is_clicked3 = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            try:
                if event.button == 0:
                    is_clicked= not is_clicked
                    if is_clicked:
                        logs.append("Claw Activated")
                        green_button = (0,255,0)
                    else:
                        logs.append("Claw Deactivated")
                        green_button = (255,255,255)
                elif event.button == 1:
                    is_clicked1 = not is_clicked1
                    if is_clicked1:
                        logs.append("AI Mode Activated")
                        red_button = (255,0,0)
                    else:
                        logs.append("AI Mode Deactivated")
                        red_button = (255,255,255)
                        
                elif event.button == 2:
                    is_clicked2 = not is_clicked2
                    logs.append("Robot returned to original location")
                    if is_clicked2:
                        blue_button = (0,0,255)
                    else:
                        blue_button = (255,255,255)
                
                elif event.button == 3:
                    is_clicked3 = not is_clicked3
                    logs.append("Predefined pose activated")
                    if is_clicked3:
                        yellow_button = (255, 250, 0)
                    else:
                        yellow_button = (255,255,255)

            except Exception as e:
                x,y = pygame.mouse.get_pos()
                if x <= (width//2) + ((width//2) - 100)+ 100 and x >=  (width//2) + ((width//2) - 100) or event.button == 1:
                    if y <= 60 and y >= 10 or  event.button == 1:
                        if is_clicked:
                            pass
                        else:
                            pass
                        is_clicked = not is_clicked
                

        i = 10
        for line in logs:
            text_surface = font.render(f"> {line}", True, WHITE)
            screen.blit(text_surface, (15, (height//2)+i))
            i += 20
        
        color = None
        if is_clicked:
            color = BLUE
        else:
            color = WHITE
        for i, (cx, cy) in enumerate(circle_positions):
            angle_rad = math.radians(joint_angles[i])
            if joint_angles[i] >= 180 or joint_angles[i] <= 0:
                logs.append(Error(17).get())
                joint_angles[i] = max(1, min(joint_angles[i], 179))
                
            pygame.draw.circle(screen, WHITE, (cx, cy), CIRCLE_R, 2)
            
            nx = cx + CIRCLE_R * math.cos(-angle_rad)
            ny = cy + CIRCLE_R * math.sin(-angle_rad)
            pygame.draw.line(screen, WHITE, (cx, cy), (int(nx), int(ny)), 2)

            pygame.draw.circle(screen, WHITE, (cx, cy), 4)
            
            lbl = small_font.render(f"{joint_labels[i]}  {joint_angles[i]}°", True, BLUE)
            screen.blit(lbl, (cx - lbl.get_width() // 2, cy + CIRCLE_R + 6))
            
        # err = Error(1)
        # if err.isThrown():
        #     logs.append(err.get())
                            
        rect = pygame.Rect((width//2) + ((width//2) - 100), 10, 100, 50)
        pygame.draw.rect(screen, color, rect, 1)
        
        text_surface = font.render(f"AI Mode", True, color)
        screen.blit(text_surface, ((width//2) + ((width//2) - 87), 23))
        pygame.draw.rect(screen, WHITE, static_rect, 1)


        pygame.draw.circle(screen, red_button, (width//1.4, height//1.5), 10)
        pygame.draw.circle(screen, yellow_button, (width//1.5, height//1.5), 10)
        pygame.draw.circle(screen, green_button, (width//1.4, height//1.4), 10)
        pygame.draw.circle(screen, blue_button, (width//1.5, height//1.4), 10)
        
    
    pygame.display.flip()

pygame.quit()
sys.exit()
