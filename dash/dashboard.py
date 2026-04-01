# AI MODE TOGGLE
# LOGS DISPLAY
# ERRORS OBJECT FOR EASY ACCESS - TODAY
import pygame
import sys
from errors import *
import math
import os
from vector import vector

pygame.init()
pygame.joystick.init()

width, height = 700,700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("C.O.R.I DASHBOARD")

WHITE = (255, 255, 255)
BLUE = (0,0,255)
font = pygame.font.SysFont('Arial', 20)
static_rect = pygame.Rect(10, height//2, (width//2)-10, (height//2)-10)
logs = []

font       = pygame.font.SysFont('Consolas', 18)
small_font = pygame.font.SysFont('Consolas', 13)

joint_angles = [180, 180, 90, 90]

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
is_clicked_ai = False
is_clicked = False
is_clicked1 = False
is_clicked2 = False
is_clicked3 = False
running = True
while running:
    # -- Event processing (only handle state changes) --
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            try:
                if event.button == 0:
                    is_clicked= not is_clicked
                    if is_clicked:
                        logs.append("Claw Activated")
                        green_button = (0,255,0)
                        joint_angles[0] = 40
                    else:
                        logs.append("Claw Deactivated")
                        green_button = (255,255,255)
                        joint_angles[0] = 180
                elif event.button == 1:
                    is_clicked1 = not is_clicked1
                    is_clicked_ai = is_clicked1
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
                        blue_button = (255,255,255)
                
                elif event.button == 3:
                    is_clicked3 = not is_clicked3
                    logs.append("Predefined pose activated")
                    if is_clicked3:
                        yellow_button = (255, 250, 0)
                        joint_angles = [40, 110, 150, 80]
                    else:
                        yellow_button = (255,255,255)
            except Exception:
                pass

    # -- Poll joysticks each frame to build a full 3D vector for IK --
    if len(joysticks) > 0:
        j0 = joysticks[0]
        naxes = j0.get_numaxes()
        ax0 = j0.get_axis(0) if naxes > 0 else 0.0
        ax1 = j0.get_axis(1) if naxes > 1 else 0.0
        # prefer axis 3 for right-stick Y, else axis 2 (triggers) as Z
        z = 0.0
        if naxes > 3:
            z = j0.get_axis(3)
        elif naxes > 2:
            z = j0.get_axis(2)
        vector1 = [ax0 * 3.0, -ax1 * 3.0, z * 3.0]
        vector_pass = f"{float(vector1[0])} {float(vector1[1])} {float(vector1[2])}"
        try:
            angles = vector().update(vector_pass)
            joint_angles = [angles['A1'], angles['A2'], angles['A3'], angles['A4']]
        except Exception as e:
            logs.append(str(e))

    # -- Drawing (one pass per frame) --
    screen.fill((0,0,0))

    i = 10
    for line in logs[-18:]:
        text_surface = font.render(f"> {line}", True, WHITE)
        screen.blit(text_surface, (15, (height//2)+i))
        i += 20

    color = BLUE if is_clicked_ai else WHITE
    for i, (cx, cy) in enumerate(circle_positions):
        angle_rad = math.radians(joint_angles[i])
        # clamp angles
        if joint_angles[i] >= 180 or joint_angles[i] <= 0:
            joint_angles[i] = max(1, min(joint_angles[i], 179))

        pygame.draw.circle(screen, WHITE, (cx, cy), CIRCLE_R, 2)

        nx = cx + CIRCLE_R * math.cos(-angle_rad)
        ny = cy + CIRCLE_R * math.sin(-angle_rad)
        pygame.draw.line(screen, WHITE, (cx, cy), (int(nx), int(ny)), 2)

        pygame.draw.circle(screen, WHITE, (cx, cy), 4)

        lbl = small_font.render(f"{joint_labels[i]}  {joint_angles[i]}°", True, BLUE)
        screen.blit(lbl, (cx - lbl.get_width() // 2, cy + CIRCLE_R + 6))

    rect = pygame.Rect((width//2) + ((width//2) - 100), 10, 100, 50)
    pygame.draw.rect(screen, color, rect, 1)
    text_surface = font.render("AI Mode", True, color)
    screen.blit(text_surface, ((width//2) + ((width//2) - 87), 23))
    pygame.draw.rect(screen, WHITE, static_rect, 1)

    pygame.draw.circle(screen, yellow_button, (int(width*0.78)+28, int(height*0.78)+0), 15)
    pygame.draw.circle(screen, blue_button, (int(width*0.78)+0, int(height*0.78)+28), 15)
    pygame.draw.circle(screen, red_button, (int(width*0.78)-28, int(height*0.78)+0), 15)
    pygame.draw.circle(screen, green_button, (int(width*0.78)+0, int(height*0.78)-28), 15)

    pygame.display.flip()

pygame.quit()
sys.exit()
