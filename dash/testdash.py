import pygame
import sys
import math
import os
import numpy as np
from vector import vector
# class vector:
#     def update(self, vector_str):
#         try:
#             ns = vector_str.split(' ')
#             dx, dy, dz = float(ns[0]), float(ns[1]), float(ns[2])
#             L = 1.0
#             A1 = np.degrees(np.arctan2(dy, dx))
#             r = np.hypot(dx, dy)
#             s = dz
#             dist = np.hypot(r, s)
#             max_reach = 3 * L - 1e-6
#             if dist > max_reach:
#                 scale = max_reach / dist
#                 r *= scale
#                 s *= scale
            
#             # IK calculation logic
#             c2 = (r*r + s*s - 3*L*L) / (2*L*r) if r > 0.01 else 0
#             c2 = np.clip(c2, -1.0, 1.0)
#             A2 = np.degrees(np.arctan2(s, r) - np.arctan2(np.sqrt(1 - c2*c2), c2))
#             c23 = (r - L*np.cos(np.radians(A2))) / (2*L)
#             c23 = np.clip(c23, -1.0, 1.0)
#             A3 = np.degrees(np.arccos(c23)) - A2
#             A4 = A3 # Wrist mirrors elbow in this simplified model
            
#             return {'A1': A1, 'A2': A2, 'A3': A3, 'A4': A4}
#         except:
#             return {'A1': 0, 'A2': 0, 'A3': 0, 'A4': 0}

pygame.init()
pygame.joystick.init()

width, height = 700, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("C.O.R.I DASHBOARD")

# Modern color scheme
BACKGROUND = (18, 18, 30)
ACCENT_COLOR = (0, 200, 255)
SECONDARY_ACCENT = (100, 255, 200)
PANEL_BG = (30, 30, 45)
TEXT_COLOR = (220, 220, 255)
WARNING = (255, 180, 50)
DANGER = (255, 80, 80)
SUCCESS = (80, 220, 150)

CIRCLE_R = 70
CIRCLE_BORDER = 3
NEEDLE_WIDTH = 3
GAUGE_BG = (40, 40, 60)
NEEDLE_COLOR = ACCENT_COLOR

logs = []
font = pygame.font.SysFont('Arial', 20, bold=True)
small_font = pygame.font.SysFont('Arial', 14)
logs_font = pygame.font.SysFont('Consolas', 15)

joint_angles = [180, 180, 90, 90]
col_xs = [width // 6, width // 2.5]
row_ys = [height // 12 + 40, height // 2 - 120]
circle_positions = []
for r in range(2):
    for c in range(2):
        circle_positions.append((col_xs[c], row_ys[r]))

joint_labels = [f"J{i+1}" for i in range(4)]

joysticks = []
for i in range(pygame.joystick.get_count()):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    joysticks.append(joy)

# Button states with modern styling
red_button = PANEL_BG
green_button = PANEL_BG
blue_button = PANEL_BG
yellow_button = PANEL_BG
color = (255, 255, 255)

is_clicked_ai = False
is_clicked = False
is_clicked1 = False
is_clicked2 = False
is_clicked3 = False
running = True

def draw_rounded_rect(surface, rect, color, radius=10, border=0):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border > 0:
        pygame.draw.rect(surface, (255, 255, 255), rect, border, border_radius=radius)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            try:
                if event.button == 0:
                    is_clicked = not is_clicked
                    logs.append("Claw Activated" if is_clicked else "Claw Deactivated")
                    green_button = SUCCESS if is_clicked else PANEL_BG
                    joint_angles[0] = 40 if is_clicked else 180
                    
                elif event.button == 1:
                    is_clicked_ai = not is_clicked_ai
                    logs.append("AI Mode " + ("Activated" if is_clicked_ai else "Deactivated"))
                    red_button = DANGER if is_clicked_ai else PANEL_BG
                    
                elif event.button == 2:
                    logs.append("Robot returned to original location")
                    blue_button = ACCENT_COLOR if not is_clicked2 else PANEL_BG
                    is_clicked2 = not is_clicked2
                    
                elif event.button == 3:
                    logs.append("Predefined pose activated")
                    yellow_button = WARNING if not is_clicked3 else PANEL_BG
                    is_clicked3 = not is_clicked3
                    joint_angles = [40, 110, 150, 80] if is_clicked3 else [180, 180, 90, 90]
            except Exception:
                pass

    # Process joystick input
    angles = None
    if joysticks:
        j0 = joysticks[0]
        naxes = j0.get_numaxes()
        ax0 = j0.get_axis(0) if naxes > 0 else 0.0
        ax1 = j0.get_axis(1) if naxes > 1 else 0.0
        z = j0.get_axis(3) if naxes > 3 else (j0.get_axis(2) if naxes > 2 else 0.0)
        vector1 = [ax0 * 3.0, -ax1 * 3.0, z * 3.0]
        vector_pass = f"{float(vector1[0])} {float(vector1[1])} {float(vector1[2])}"
        try:
            angles = vector().update(vector_pass)
        except Exception as e:
            logs.append(str(e))

    # Update joint angles
    if angles:
        try:
            a1 = float(angles.get("A1", joint_angles[0]))
            a2 = float(angles.get("A2", joint_angles[1]))
            a3 = float(angles.get("A3", joint_angles[2]))
            a4 = float(angles.get("A4", joint_angles[3]))
        except Exception:
            a1, a2, a3, a4 = joint_angles

        def norm360(x):
            return (x % 360 + 360) % 360

        def clamp0_180(x):
            return max(0, min(180, x))

        joint_angles = [
            int(round(norm360(a1))),
            int(round(clamp0_180(a2))),
            int(round(clamp0_180(a3))),
            int(round(clamp0_180(a4)))
        ]

    # Rendering
    screen.fill(BACKGROUND)
    
    # Draw main panel
    draw_rounded_rect(screen, pygame.Rect(10, 10, width-20, height-20), PANEL_BG, 20, 2)
    
    # Draw gauges with modern styling
    for i, (pos, angle) in enumerate(zip(circle_positions, joint_angles)):
        # Gauge background
        pygame.draw.circle(screen, GAUGE_BG, pos, CIRCLE_R, CIRCLE_BORDER)
        
        # Value indicator
        angle_rad = math.radians(angle)
        nx = pos[0] + CIRCLE_R * 0.8 * math.cos(-angle_rad)
        ny = pos[1] + CIRCLE_R * 0.8 * math.sin(-angle_rad)
        
        # Needle with dynamic width
        needle_width = 2 + (angle % 30) / 30  # Pulse effect
        pygame.draw.line(screen, NEEDLE_COLOR, pos, (int(nx), int(ny)), int(needle_width))
        
        # Center point
        pygame.draw.circle(screen, ACCENT_COLOR, pos, 6)
        
        # Value label
        lbl = small_font.render(f"{joint_labels[i]} {angle}°", True, TEXT_COLOR)
        screen.blit(lbl, (pos[0] - lbl.get_width()//2, pos[1] + CIRCLE_R + 10))
        
        # Add scale markers
        for j in range(0, 361, 30):
            rad = math.radians(j)
            marker_x = pos[0] + (CIRCLE_R - 5) * math.cos(rad)
            marker_y = pos[1] + (CIRCLE_R - 5) * math.sin(rad)
            pygame.draw.circle(screen, TEXT_COLOR, (int(marker_x), int(marker_y)), 2)

    # Draw control panel
    panel_rect = pygame.Rect(width//2 - 120, height - 100, 240, 80)
    draw_rounded_rect(screen, panel_rect, PANEL_BG, 15, 2)
    
    # Draw control buttons with icons
    buttons = [
        (red_button, "AI MODE", (width//2 - 90, height - 75)),
        (green_button, "CLAW", (width//2 + 10, height - 75)),
        (blue_button, "HOME", (width//2 - 90, height - 35)),
        (yellow_button, "POSE", (width//2 + 10, height - 35))
    ]
    
    for color, text, (x, y) in buttons:
        # Button background
        button_rect = pygame.Rect(x, y, 80, 30)
        draw_rounded_rect(screen, button_rect, color, 8)
        
        # Text label
        text_surf = small_font.render(text, True, TEXT_COLOR)
        screen.blit(text_surf, (x + 40 - text_surf.get_width()//2, y + 8))
        
        # Active indicator
        if color != PANEL_BG:
            pygame.draw.rect(screen, ACCENT_COLOR, (x-3, y-3, 6, 6))

    # Draw logs with style
    logs_rect = pygame.Rect(15, height//2 + 20, width//2 - 25, height//2 - 40)
    pygame.draw.rect(screen, PANEL_BG, logs_rect, width=2)
    
    for i, line in enumerate(logs[-15:]):
        text_surface = logs_font.render(f"> {line}", True, TEXT_COLOR)
        screen.blit(text_surface, (25, height//2 + 30 + i*20))

    # Draw status indicators
    status_x = width - 40
    status_y = height//2 - 40
    for i, (label, value) in enumerate([("X", 42), ("Y", 180), ("Z", 90)]):
        status_lbl = small_font.render(f"{label}: {value}mm", True, TEXT_COLOR)
        screen.blit(status_lbl, (status_x - status_lbl.get_width(), status_y + i*25))

    pygame.display.flip()

pygame.quit()
sys.exit()
