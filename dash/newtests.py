import pygame
import sys
import math
import os
import numpy as np

# Integrated vector class to handle Inverse Kinematics locally
class vector:
    def update(self, vector_str):
        try:
            ns = vector_str.split(' ')
            dx, dy, dz = float(ns[0]), float(ns[1]), float(ns[2])
            L = 1.0
            A1 = np.degrees(np.arctan2(dy, dx))
            r = np.hypot(dx, dy)
            s = dz
            dist = np.hypot(r, s)
            max_reach = 3 * L - 1e-6
            if dist > max_reach:
                scale = max_reach / dist
                r *= scale
                s *= scale
            
            # IK calculation logic
            c2 = (r*r + s*s - 3*L*L) / (2*L*r) if r > 0.01 else 0
            c2 = np.clip(c2, -1.0, 1.0)
            A2 = np.degrees(np.arctan2(s, r) - np.arctan2(np.sqrt(1 - c2*c2), c2))
            c23 = (r - L*np.cos(np.radians(A2))) / (2*L)
            c23 = np.clip(c23, -1.0, 1.0)
            A3 = np.degrees(np.arccos(c23)) - A2
            A4 = A3 # Wrist mirrors elbow in this simplified model
            
            return {'A1': A1, 'A2': A2, 'A3': A3, 'A4': A4}
        except:
            return {'A1': 0, 'A2': 0, 'A3': 0, 'A4': 0}

pygame.init()
pygame.joystick.init()

width, height = 700, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("C.O.R.I DASHBOARD")

BACKGROUND = (18, 18, 30)
ACCENT_COLOR = (0, 200, 255)
PANEL_BG = (30, 30, 45)
TEXT_COLOR = (220, 220, 255)
WARNING, DANGER, SUCCESS = (255, 180, 50), (255, 80, 80), (80, 220, 150)

CIRCLE_R, CIRCLE_BORDER, NEEDLE_WIDTH = 70, 3, 3
GAUGE_BG, NEEDLE_COLOR = (40, 40, 60), ACCENT_COLOR

logs = []
font = pygame.font.SysFont('Arial', 20, bold=True)
small_font = pygame.font.SysFont('Arial', 14)
logs_font = pygame.font.SysFont('Consolas', 15)

joint_angles = [180, 180, 90, 90]
col_xs, row_ys = [width // 6, width // 2.5], [height // 12 + 40, height // 2 - 120]
circle_positions = [(col_xs[c], row_ys[r]) for r in range(2) for c in range(2)]
joint_labels = ["J1 (Base)", "J2 (Shoulder)", "J3 (Elbow)", "J4 (Wrist)"]

joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joy in joysticks: joy.init()

red_button = green_button = blue_button = yellow_button = PANEL_BG
is_clicked = is_clicked_ai = is_clicked2 = is_clicked3 = False

def draw_rounded_rect(surface, rect, color, radius=10, border=0):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border > 0: pygame.draw.rect(surface, (255, 255, 255), rect, border, border_radius=radius)

vec_processor = vector()
running = True
while running:
    screen.fill(BACKGROUND)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.JOYBUTTONDOWN]:
            logs.append("Input detected")

    if joysticks:
        j = joysticks[0]
        jx, jy = j.get_axis(0) * 2.0, -j.get_axis(1) * 2.0
        jz = -j.get_axis(3) * 2.0 if j.get_numaxes() > 3 else 0.0
        angles_dict = vec_processor.update(f"{jx} {jy} {jz}")
        joint_angles = [
            int(angles_dict['A1'] % 360),
            int(angles_dict['A2'] % 360),
            int(angles_dict['A3'] % 360),
            int(angles_dict['A4'] % 360)
        ]

    draw_rounded_rect(screen, (10, 10, width-20, height-20), PANEL_BG, 20, 2)
    
    for i, (pos, angle) in enumerate(zip(circle_positions, joint_angles)):
        pygame.draw.circle(screen, GAUGE_BG, pos, CIRCLE_R, CIRCLE_BORDER)
        rad = math.radians(angle)
        nx, ny = pos[0] + CIRCLE_R*0.8*math.cos(-rad), pos[1] + CIRCLE_R*0.8*math.sin(-rad)
        pygame.draw.line(screen, NEEDLE_COLOR, pos, (int(nx), int(ny)), NEEDLE_WIDTH)
        pygame.draw.circle(screen, ACCENT_COLOR, pos, 6)
        lbl = small_font.render(f"{joint_labels[i]} {angle}°", True, TEXT_COLOR)
        screen.blit(lbl, (pos[0] - lbl.get_width()//2, pos[1] + CIRCLE_R + 10))

    # Controls and Logs
    panel_rect = pygame.Rect(width//2 - 120, height - 100, 240, 80)
    draw_rounded_rect(screen, panel_rect, PANEL_BG, 15, 2)
    
    logs_rect = pygame.Rect(15, height//2 + 20, width//2 - 25, height//2 - 40)
    pygame.draw.rect(screen, PANEL_BG, logs_rect, width=2)
    for idx, line in enumerate(logs[-10:]):
        screen.blit(logs_font.render(f"> {line}", True, TEXT_COLOR), (25, height//2 + 30 + idx*20))

    pygame.display.flip()
pygame.quit()