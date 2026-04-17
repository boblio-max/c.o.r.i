
import pygame
import numpy as np
from tvect import vector
vec = vector()
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

n = "50 50 50"
ns = n.split(" ")

N = (ns[0], ns[1], ns[2])
a, b, c, d = vec.update(n)
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

    a, b, c, d = vec.update(n)
    print(f"Updated Vectors: A={a}, B={b}, C={c}, D={d}")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Handle Joystick Input for Vector Position
    if joysticks:
        j = joysticks[0]
        # Map axes to vector components
        x_val = j.get_axis(0) * 150
        y_val = j.get_axis(1) * 150
        # Use axis 2 or 3 for Z depending on controller type
        if j.get_numaxes() > 3:
            z_axis_idx = 3  
        else:
            z_axis_idx = 2
        if j.get_numaxes() > 2:
            z_val = j.get_axis(z_axis_idx) * 150
        else:
            z_val = 0

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

    ab = np.array(b) - np.array(a)
    bc = np.array(c) - np.array(b)
    cd = np.array(d) - np.array(c)
    vectors = [
        {'color': (255, 0, 0), 'vec': np.array([100, 0, 0])},   # X (Red)
        {'color': (0, 255, 0), 'vec': np.array([0, 100, 0])},   # Y (Green)
        {'color': (0, 0, 255), 'vec': np.array([0, 0, 100])},   # Z (Blue)
        {'color': (255, 0, 0), 'vec': np.array([-100, 0, 0])},  # X (Red)
        {'color': (0, 255, 0), 'vec': np.array([0, -100, 0])},  # Y (Green)
        {'color': (0, 0, 255), 'vec': np.array([0, 0, -100])},   # Z (Blue)
        {'color': (255, 255, 255), 'vec': np.array([float(ns[0]), float(ns[1]), float(ns[2])], dtype=float)},
        {'color': (0, 0, 255), 'vec': np.array([a[0] * 50, a[1] * 50, a[2] * 50])},
        {"color": (255, 0, 0), 'vec': np.array(ab) * 50},
        {"color": (0, 255, 0), 'vec': np.array(bc) * 50},
        {"color": (0, 0, 255), 'vec': np.array(cd) * 50},
        ]   

    # 4. Drawing
    screen.fill((20, 20, 20))
    origin = (int(width/2), int(height/2))

    for v_info in vectors:
        end_pos = project(v_info['vec'], angle_x, angle_y)
        pygame.draw.line(screen, v_info['color'], origin, end_pos, 3)
        pygame.draw.circle(screen, v_info['color'], end_pos, 5)

    pygame.display.flip()

pygame.quit()
