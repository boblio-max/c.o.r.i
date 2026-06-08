# Pygame dashboard displaying joint states and controls for the robot.

import pygame
import sys
import math
import os
import numpy as np
import asyncio
import json
import websockets

# We need to add the parent directory to the path so we can grab the ik_solver.
# It's a bit of a hack, but it works perfectly for our file structure.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from math.ik_solver import IKSolver
from server.ws_client import PersistentWebSocketClient
try:
    from core.config import SERVER_HOST, SERVER_PORT
except ImportError:
    SERVER_HOST = "192.168.1.20"
    SERVER_PORT = 8765

# Networking setup - using centralized config
HOST = SERVER_HOST 
PORT = SERVER_PORT


# This class handles the math for converting vectors into joint positions.
# It's essentially doing the heavy lifting for the visual part of the dashboard.
class VectorCalculator:
    """Wrapper around IKSolver for convenient position calculations"""
    def __init__(self, L=1.0):
        self.L = L
        self.solver = IKSolver(L=L)
    
    def calculate_positions(self, target_vector_str):
        """Calculate joint positions A, B, C, D from target vector"""
        result = self.solver.get_joint_positions(*self._parse_vector(target_vector_str))
        return result['A'], result['B'], result['C'], result['D']
    
    def _parse_vector(self, vector_str):
        """Parse space-separated vector string to floats"""
        parts = vector_str.split()
        return float(parts[0]), float(parts[1]), float(parts[2])

# Initialize calculator
vec = VectorCalculator(L=1.0)

# Initialize WebSocket client
ws_client = PersistentWebSocketClient(host=HOST, port=PORT)
ws_client.start()
# Background WebSocket client used to publish joint angles to the server

# Initialize Pygame and Joystick
pygame.init()
pygame.joystick.init()

width, height = 700, 700
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
pygame.display.set_caption("C.O.R.I DASHBOARD")

# 3D View and Vector State
x_val, y_val, z_val = 0, 0, 0

L = 1
Lm = 1.57079
A1 = 0
A2 = 0
A3 = 0
A4 = 0
x = 0.5  # Movement step
x_val, y_val, z_val = 0.5, 0.5, 0.5
n = f"{x_val} {y_val} {z_val}"
a, b, c, d = vec.calculate_positions(n)



BACKGROUND = (18, 18, 30)
ACCENT_COLOR = (0, 200, 255)
SECONDARY_ACCENT = (100, 255, 200)
PANEL_BG = (30, 30, 45)
TEXT_COLOR = (220, 220, 255)
WARNING = (255, 180, 50)
DANGER = (255, 80, 80)
SUCCESS = (80, 220, 150)

# Gauge styling constants
CIRCLE_R = 70
CIRCLE_BORDER = 3
NEEDLE_WIDTH = 3
GAUGE_BG = (40, 40, 60)
NEEDLE_COLOR = ACCENT_COLOR

logs = []
font = pygame.font.SysFont('Arial', 20, bold=True)
small_font = pygame.font.SysFont('Arial', 14)
logs_font = pygame.font.SysFont('Consolas', 15)

joint_angles = [180.0, 180.0, 90.0, 90.0, 0.0, 0.0]
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

# Function to draw pretty rounded rectangles because standard pygame rects are too sharp.
def draw_rounded_rect(surface, rect, color, radius=10, border=0):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border > 0:
        pygame.draw.rect(surface, (255, 255, 255), rect, border, border_radius=radius)

# --- MAIN LOOP ---
# This is where all the logic happens every single frame.
while running:
    dt = clock.tick(60) / 1000.0
    n = f"0 0 0"
    a, b, c, d = vec.calculate_positions(n)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            # Check button collision for mouse clicks
            ai_mode_rect = pygame.Rect(width//2 - 90, height - 75, 80, 30)
            claw_rect = pygame.Rect(width//2 + 10, height - 75, 80, 30)
            home_rect = pygame.Rect(width//2 - 90, height - 35, 80, 30)
            pose_rect = pygame.Rect(width//2 + 10, height - 35, 80, 30)
            
            try:
                if ai_mode_rect.collidepoint(x, y):
                    is_clicked_ai = not is_clicked_ai
                    logs.append("AI Mode " + ("Activated" if is_clicked_ai else "Deactivated"))
                    red_button = DANGER if is_clicked_ai else PANEL_BG
                    
                elif claw_rect.collidepoint(x, y):
                    is_clicked = not is_clicked
                    logs.append("Claw Activated" if is_clicked else "Claw Deactivated")
                    green_button = SUCCESS if is_clicked else PANEL_BG
                    joint_angles[0] = 40.0 if is_clicked else 180.0
                    
                elif home_rect.collidepoint(x, y):
                    logs.append("Robot returned to original location")
                    blue_button = ACCENT_COLOR if not is_clicked2 else PANEL_BG
                    is_clicked2 = not is_clicked2
                    
                elif pose_rect.collidepoint(x, y):
                    logs.append("Predefined pose activated" if not is_clicked3 else "Predefined pose deactivated")
                    yellow_button = WARNING if not is_clicked3 else PANEL_BG
                    is_clicked3 = not is_clicked3
                    joint_angles = [40.0, 110.0, 150.0, 80.0, 0.0, 0.0] if is_clicked3 else [180.0, 180.0, 90.0, 90.0, 0.0, 0.0]

            except Exception:
                pass
                
        elif event.type == pygame.JOYBUTTONDOWN:
            try:
                if event.button == 0:
                    is_clicked = not is_clicked
                    logs.append("Claw Activated" if is_clicked else "Claw Deactivated")
                    green_button = SUCCESS if is_clicked else PANEL_BG
                    joint_angles[0] = 40.0 if is_clicked else 180.0
                    
                elif event.button == 1:
                    is_clicked_ai = not is_clicked_ai
                    logs.append("AI Mode " + ("Activated" if is_clicked_ai else "Deactivated"))
                    red_button = DANGER if is_clicked_ai else PANEL_BG
                    
                elif event.button == 2:
                    logs.append("Robot returned to original location")
                    blue_button = ACCENT_COLOR if not is_clicked2 else PANEL_BG
                    is_clicked2 = not is_clicked2
                    
                elif event.button == 3:
                    logs.append("Predefined pose activated" if not is_clicked3 else "Predefined pose deactivated")
                    yellow_button = WARNING if not is_clicked3 else PANEL_BG
                    is_clicked3 = not is_clicked3
                    joint_angles = [40.0, 110.0, 150.0, 80.0, 0.0, 0.0] if is_clicked3 else [180.0, 180.0, 90.0, 90.0, 0.0, 0.0]

            except Exception:
                pass    
        elif event.type == pygame.JOYHATMOTION:
            # event.hat is the hat index (usually 0)
            # event.value is the (x, y) tuple
            x, y = event.value
            if x == 1:
                print("D-pad Right")
            elif x == -1:
                print("D-pad Left")
            if y == 1:
                print("D-pad Up")
            elif y == -1:
                print("D-pad Down")
            

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
            n = f"{ax0} {ax1} {z}"
            angles = IKSolver().update(vector_pass)
        except Exception as e:
            logs.append(str(e))
    
    
    # Update joint angles
    if angles and not is_clicked3:
        try:
            a1 = float(angles.get("A1", joint_angles[0]))
            a2 = float(angles.get("A2", joint_angles[1]))
            a3 = float(angles.get("A3", joint_angles[2]))
            a4 = float(angles.get("A4", joint_angles[3]))
        except Exception:
            a1, a2, a3, a4, un, un1 = joint_angles

        def norm360(x):
            return (x % 360 + 360) % 360

        def clamp0_180(x):
            return max(0, min(180, x))

        joint_angles = [
            (round(norm360(a1))),
            round(clamp0_180(a2)),
            round(clamp0_180(a3)),
            round(clamp0_180(a4)),
            0.0,
            0.0
        ]

    # Send joint angles to server (non-blocking)
    ws_client.send(joint_angles)
    # Rendering
    screen.fill(BACKGROUND)
    a, b, c, d = vec.calculate_positions(n)
    
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
        #status_lbl = small_font.render(f"{label}: {value}mm", True, TEXT_COLOR)
        #screen.blit(status_lbl, (status_x - status_lbl.get_width(), status_y + i*25))
        pass
    pygame.display.flip()

# Cleanup
ws_client.stop()
pygame.quit()
sys.exit()
