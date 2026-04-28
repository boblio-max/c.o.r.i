
import pygame
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ik_solver import IKSolver

# Initialize IK Solver
solver = IKSolver(L=1.0)

# Initialize Pygame and Joystick
pygame.init()
pygame.joystick.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Setup Joysticks
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for joy in joysticks:
    joy.init()

# 3D View and Vector State
angle_x, angle_y = 0, 0
x_val, y_val, z_val = 0, 0, 0

L = 1
Lm = 1.57079
A1 = 0
A2 = 0
A3 = 0
A4 = 0
x = 0.5  # Movement step
x_val, y_val, z_val = 0.5, 0.5, 0.5
n = (x_val, y_val, z_val)

def project(vector, angle_x, angle_y):
    # Rotation Matrices
    ry = np.array([
        [np.cos(angle_y), 0, np.sin(angle_y)],
        [0, 1, 0],
        [-np.sin(angle_y), 0, np.cos(angle_y)]
    ])
    rx = np.array([
        [1, 0, 0],
        [0, np.cos(angle_x), -np.sin(angle_x)],
        [0, np.sin(angle_x), np.cos(angle_x)]
    ])
    # Apply rotations and center on screen
    rotated = rx @ (ry @ vector)
    return int(rotated[0] + width/2), int(rotated[1] + height/2)

running = True
while running:
    dt = clock.tick(60) / 1000.0


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Handle Joystick Input for Vector Position
    if joysticks:
        j = joysticks[0]
        # Map axes to vector components
        x_val = j.get_axis(0) * 2.0
        y_val = j.get_axis(1) * 2.0
        # Use axis 2 or 3 for Z depending on controller type
        if j.get_numaxes() > 3:
            z_axis_idx = 3  
        else:
            z_axis_idx = 2
        if j.get_numaxes() > 2:
            z_val = j.get_axis(z_axis_idx) * 2.0
        else:
            z_val = 0.0
    
    # Increment x_val each frame for continuous movement
    x_val = x_val
    
    # Update target vector
    n = (x_val * 30, y_val * 30, z_val * 30)

    # 2. Handle Keyboard Input for Camera Rotation
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  
        angle_y -= 2 * dt
    if keys[pygame.K_RIGHT]: 
        angle_y += 2 * dt
    if keys[pygame.K_UP]:    
        angle_x -= 2 * dt
    if keys[pygame.K_DOWN]:  
        angle_x += 2 * dt

    a, b, c, d = solver.update_vect(n)
    
    vectors = [
        {'color': (255, 0, 0), 'vec': np.array([100, 0, 0])},   # X (Red)
        {'color': (0, 255, 0), 'vec': np.array([0, 100, 0])},   # Y (Green)
        {'color': (0, 0, 255), 'vec': np.array([0, 0, 100])},   # Z (Blue)
        {'color': (255, 0, 0), 'vec': np.array([-100, 0, 0])},  # X (Red)
        {'color': (0, 255, 0), 'vec': np.array([0, -100, 0])},  # Y (Green)
        {'color': (0, 0, 255), 'vec': np.array([0, 0, -100])},   # Z (Blue)
        {'color': (255, 255, 255), 'vec': np.array([x_val* 30, y_val * 30, z_val * 30])},
        {'color': (0, 0, 255), 'vec': np.array([0, 0, -100])}
        ]   

    # 4. Drawing
    screen.fill((20, 20, 20))
    origin = (int(width/2), int(height/2))
    i = 0
    for v_info in vectors:
        i += 1
        end_pos = project(v_info['vec'], angle_x, angle_y)
        pygame.draw.line(screen, v_info['color'], origin, end_pos, 3)
        pygame.draw.circle(screen, v_info['color'], end_pos, 5)
        if i > 6:
            origin = end_pos
    pygame.display.flip()

pygame.quit()
