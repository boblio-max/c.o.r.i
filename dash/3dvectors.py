# 3D vector visualizer: projects vectors to 2D for inspection of IK results.

import pygame
import numpy as np
import sys
import os

# Making sure we can find the ik_solver in the parent directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from math.ik_solver import IKSolver

# Initialize the IK Solver - this is what calculates the arm's math.
solver = IKSolver(L=1.0)

# Standard Pygame setup for our window.
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

# This takes a 3D point and flattens it onto our 2D screen using rotation matrices.
# Rotation matrices are essentially just a bunch of trig that rotates points around an axis.
def project(vector, angle_x, angle_y):
    # Y-axis rotation (left/right)
    ry = np.array([
        [np.cos(angle_y), 0, np.sin(angle_y)],
        [0, 1, 0],
        [-np.sin(angle_y), 0, np.cos(angle_y)]
    ])
    # X-axis rotation (up/down)
    rx = np.array([
        [1, 0, 0],
        [0, np.cos(angle_x), -np.sin(angle_x)],
        [0, np.sin(angle_x), np.cos(angle_x)]
    ])
    # Apply the rotations and then shift it to the center of the screen.
    rotated = rx @ (ry @ vector)
    return int(rotated[0] + width/2), int(rotated[1] + height/2)

scale = 1.0
is_shown = True
reset = False

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
    # We use these keys to fly around the 3D space.
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  
        angle_y -= 2 * dt
    if keys[pygame.K_RIGHT]: 
        angle_y += 2 * dt
    if keys[pygame.K_UP]:    
        angle_x -= 2 * dt
    if keys[pygame.K_DOWN]: 
        angle_x += 2 * dt
    
    # Zoom controls
    if keys[pygame.K_PAGEUP]:
        scale += 0.1
    if keys[pygame.K_PAGEDOWN]:
        if scale > 0.0:
            scale -= 0.1
        else:
            scale = 0
            
    # Reset camera view
    if keys[pygame.K_r]:
        scale = 1.0
        angle_x, angle_y = 0, 0
    
    if keys[pygame.K_s]:
        reset = not reset
    # Preset camera angles (Top, Front, Side views)
    if keys[pygame.K_x]:
        angle_x, angle_y = 1.63, 1.57
    if keys[pygame.K_y]:
        angle_x, angle_y = 0.03, 0
    if keys[pygame.K_z]:
        angle_x, angle_y = 1.56, 0

    a, b, c = solver.update_vect(n)
    
    # Drawing vectors
    # first 6 are axes
    # next are arm vectors
    vectors = [
            {'color': (255, 0, 0), 'vec': np.array([100 * scale, 0, 0])},   # X (Red)
            {'color': (0, 255, 0), 'vec': np.array([0, 100 * scale, 0])},   # Y (Green)
            {'color': (0, 0, 255), 'vec': np.array([0, 0, 100 * scale])},   # Z (Blue)
            {'color': (255, 0, 0), 'vec': np.array([-100 * scale, 0, 0])},  # X (Red)
            {'color': (0, 255, 0), 'vec': np.array([0, -100 * scale, 0])},  # Y (Green)
            {'color': (0, 0, 255), 'vec': np.array([0, 0, -100 * scale])},   # Z (Blue)
            {'color': (255, 255, 255), 'vec': np.array([x_val* 40 * scale, y_val * 40 * scale, z_val * 40 * scale])}
        ]
    
    # If the vectors are toggled to be shown
    # the arm vectors are added to the end
    if is_shown:
        vectors = [
            {'color': (255, 0, 0), 'vec': np.array([100 * scale, 0, 0])},   # X (Red)
            {'color': (0, 255, 0), 'vec': np.array([0, 100 * scale, 0])},   # Y (Green)
            {'color': (0, 0, 255), 'vec': np.array([0, 0, 100 * scale])},   # Z (Blue)
            {'color': (255, 0, 0), 'vec': np.array([-100 * scale, 0, 0])},  # X (Red)
            {'color': (0, 255, 0), 'vec': np.array([0, -100 * scale, 0])},  # Y (Green)
            {'color': (0, 0, 255), 'vec': np.array([0, 0, -100 * scale])},   # Z (Blue)
            {'color': (255, 255, 255), 'vec': np.array([x_val* 40 * scale, y_val * 40 * scale, z_val * 40 * scale])},
            {'color': (0, 0, 255), 'vec': np.array([a[0] * 40 * scale, a[1] * 40 * scale, a[2] * 40 * scale])},
            {'color': (255, 255, 0), 'vec': np.array([b[0] * 40 * scale, b[1] * 40 * scale, b[2] * 40 * scale])},
            {'color': (255, 0, 255), 'vec': np.array([c[0] * 40 * scale, c[1] * 40 * scale, c[2] * 40 * scale])}
            ]   
    
    if reset:
        vectors = [
            {'color': (255, 0, 0), 'vec': np.array([100 * scale, 0, 0])},   # X (Red)
            {'color': (0, 255, 0), 'vec': np.array([0, 100 * scale, 0])},   # Y (Green)
            {'color': (0, 0, 255), 'vec': np.array([0, 0, 100 * scale])},   # Z (Blue)
            {'color': (255, 0, 0), 'vec': np.array([-100 * scale, 0, 0])},  # X (Red)
            {'color': (0, 255, 0), 'vec': np.array([0, -100 * scale, 0])},  # Y (Green)
            {'color': (0, 0, 255), 'vec': np.array([0, 0, -100 * scale])},   # Z (Blue)
            {'color': (255, 255, 255), 'vec': np.array([x_val* 40 * scale, y_val * 40 * scale, z_val * 40 * scale])},
            {'color': (0, 0, 255), 'vec': np.array([a[0] * 40 * scale, a[1] * 40 * scale, a[2] * 40 * scale])},
            {'color': (255, 255, 0), 'vec': np.array([b[0] * 40 * scale, b[1] * 40 * scale, b[2] * 40 * scale])},
            {'color': (255, 0, 255), 'vec': np.array([c[0] * 40 * scale, c[1] * 40 * scale, c[2] * 40 * scale])}
        ]
    # 4. Drawing
    screen.fill((20, 20, 20))
    origin = (int(width/2), int(height/2))
    # Keep track of center for arm vectors
    center = origin  
   
    i = 0
    # For chaining arm vectors
    accumulated_vec = np.array([0.0, 0.0, 0.0])  
    arm_start = center
    for v_info in vectors:
        i += 1
        current_vec = v_info['vec']
        
        # For arm vectors (indices 7, 8, 9 when is_shown), chain them together
        if is_shown and i > 7:
            end_pos = project(accumulated_vec + current_vec, angle_x, angle_y)
            pygame.draw.line(screen, v_info['color'], arm_start, end_pos, 3)
            pygame.draw.circle(screen, v_info['color'], end_pos, 5)
            accumulated_vec += current_vec
            arm_start = end_pos
        else:
            end_pos = project(current_vec, angle_x, angle_y)
            pygame.draw.line(screen, v_info['color'], origin, end_pos, 3)
            pygame.draw.circle(screen, v_info['color'], end_pos, 5)
            if i > 6:
                origin = end_pos
    # End of frame drawing
    pygame.display.flip()

pygame.quit()
