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
BACKGROUND = (30, 30, 30)
CIRCLE_COLOR = (200, 200, 200)
NEEDLE_COLOR = (0, 200, 200)
LABEL_COLOR = (180, 180, 255)
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
color = (255,255,255)

is_clicked_ai = False
is_clicked = False
is_clicked1 = False
is_clicked2 = False
is_clicked3 = False
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            x,y = pygame.mouse.get_pos()
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
                elif event.button == 1 or (x <= (width//2) + ((width//2) - 100)+ 100 and x >=  (width//2) + ((width//2) - 100)):
                    x,y = pygame.mouse.get_pos()
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
                        joint_angles = [40, 110, 150, 80]
                    else:
                        yellow_button = (255,255,255)
            except Exception:
                pass

    angles = None
    if len(joysticks) > 0:
        j0 = joysticks[0]
        naxes = j0.get_numaxes()
        if naxes > 0:
            
            ax0 = j0.get_axis(0) 
        else:
            ax0 = 0.0

        if naxes > 1:
            ax1 = j0.get_axis(1) 
        else:
            ax1 = 0.0

        z = 0.0
        if naxes > 3:
            z = j0.get_axis(3)
        elif naxes > 2:
            z = j0.get_axis(2)
        vector1 = [ax0 * 3.0, -ax1 * 3.0, z * 3.0]
        vector_pass = f"{float(vector1[0])} {float(vector1[1])} {float(vector1[2])}"
        try:
            angles = vector().update(vector_pass)
        except Exception as e:
            logs.append(str(e))

    # Safely update displayed joint angles only when we have valid angle data.
    if angles:
        try:
            a1 = float(angles.get("A1", joint_angles[0]))
            a2 = float(angles.get("A2", joint_angles[1]))
            a3 = float(angles.get("A3", joint_angles[2]))
            a4 = float(angles.get("A4", joint_angles[3]))
        except Exception:
            a1, a2, a3, a4 = joint_angles

        # Normalize/format angles for display:
        def norm360(x):
            return (x % 360 + 360) % 360

        def clamp0_180(x):
            return max(0, min(180, x))

        a1 = norm360(a1)
        a2 = clamp0_180(a2)
        a3 = clamp0_180(a3)
        a4 = clamp0_180(a4)

        joint_angles = [int(round(a1)), int(round(a2)), int(round(a3)), int(round(a4))]

    # Improved background color for better contrast
    screen.fill((30, 30, 30))

    i = 10
    for line in logs[-18:]:
        text_surface = font.render(f"> {line}", True, WHITE)
        screen.blit(text_surface, (15, (height//2)+i))
        i += 20

    pygame.draw.circle(screen, CIRCLE_COLOR, (circle_positions[0][0], circle_positions[0][1]), CIRCLE_R, 2)
    angle_rad = math.radians(joint_angles[0])
    nx = circle_positions[0][0] + CIRCLE_R * math.cos(-angle_rad)
    ny = circle_positions[0][1] + CIRCLE_R * math.sin(-angle_rad)
    pygame.draw.line(screen, NEEDLE_COLOR, (circle_positions[0][0], circle_positions[0][1]), (int(nx), int(ny)), 3)
    pygame.draw.circle(screen, CIRCLE_COLOR, (circle_positions[0][0], circle_positions[0][1]), 4)
    lbl = small_font.render(f"{joint_labels[0]}  {joint_angles[0]}°", True, LABEL_COLOR)
    screen.blit(lbl, (circle_positions[0][0] - lbl.get_width() // 2, circle_positions[0][1] + CIRCLE_R + 6))

    pygame.draw.circle(screen, CIRCLE_COLOR, (circle_positions[1][0], circle_positions[1][1]), CIRCLE_R, 2)
    angle_rad1 = math.radians(joint_angles[1])
    nx1 = circle_positions[1][0] + CIRCLE_R * math.cos(-angle_rad1)
    ny1 = circle_positions[1][1] + CIRCLE_R * math.sin(-angle_rad1)
    pygame.draw.line(screen, NEEDLE_COLOR, (circle_positions[1][0], circle_positions[1][1]), (int(nx1), int(ny1)), 3)
    pygame.draw.circle(screen, CIRCLE_COLOR, (circle_positions[1][0], circle_positions[1][1]), 4)
    lbl = small_font.render(f"{joint_labels[1]}  {joint_angles[1]}°", True, LABEL_COLOR)
    screen.blit(lbl, (circle_positions[1][0] - lbl.get_width() // 2, circle_positions[1][1] + CIRCLE_R + 6))

    pygame.draw.circle(screen, CIRCLE_COLOR, (circle_positions[2][0], circle_positions[2][1]), CIRCLE_R, 2)
    angle_rad2 = math.radians(joint_angles[2])
    nx2 = circle_positions[2][0] + CIRCLE_R * math.cos(-angle_rad2)
    ny2 = circle_positions[2][1] + CIRCLE_R * math.sin(-angle_rad2)
    pygame.draw.line(screen, NEEDLE_COLOR, (circle_positions[2][0], circle_positions[2][1]), (int(nx2), int(ny2)), 3)
    pygame.draw.circle(screen, CIRCLE_COLOR, (circle_positions[2][0], circle_positions[2][1]), 4)
    lbl = small_font.render(f"{joint_labels[2]}  {joint_angles[2]}°", True, LABEL_COLOR)
    screen.blit(lbl, (circle_positions[2][0] - lbl.get_width() // 2, circle_positions[2][1] + CIRCLE_R + 6))

    pygame.draw.circle(screen, CIRCLE_COLOR, (circle_positions[3][0], circle_positions[3][1]), CIRCLE_R, 2)
    angle_rad3 = math.radians(joint_angles[3])
    nx3 = circle_positions[3][0] + CIRCLE_R * math.cos(-angle_rad3)
    ny3 = circle_positions[3][1] + CIRCLE_R * math.sin(-angle_rad3)
    pygame.draw.line(screen, NEEDLE_COLOR, (circle_positions[3][0], circle_positions[3][1]), (int(nx3), int(ny3)), 3)
    pygame.draw.circle(screen, CIRCLE_COLOR, (circle_positions[3][0], circle_positions[3][1]), 4)
    lbl = small_font.render(f"{joint_labels[3]}  {joint_angles[3]}°", True, LABEL_COLOR)
    screen.blit(lbl, (circle_positions[3][0] - lbl.get_width() // 2, circle_positions[3][1] + CIRCLE_R + 6))

    
    

    rect = pygame.Rect((width//2) + ((width//2) - 100), 10, 100, 50)
    pygame.draw.rect(screen, red_button, rect, 1)
    text_surface = font.render("AI Mode", True, WHITE)

    screen.blit(text_surface, ((width//2) + ((width//2) - 87), 23))
    pygame.draw.rect(screen, WHITE, static_rect, 1)

    pygame.draw.circle(screen, red_button, (int(width*0.78)+28, int(height*0.78)+0), 15)
    pygame.draw.circle(screen, green_button, (int(width*0.78)+0, int(height*0.78)+28), 15)
    pygame.draw.circle(screen, blue_button, (int(width*0.78)-28, int(height*0.78)+0), 15)
    pygame.draw.circle(screen, yellow_button, (int(width*0.78)+0, int(height*0.78)-28), 15)

    pygame.display.flip()

pygame.quit()
sys.exit()
