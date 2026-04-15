
import pygame
import numpy as np

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

n = "1 1 1"
ns = n.split(" ")

A = (0,0,0)
B = (L*np.cos(A2)*np.cos(A1), L*np.cos(A2)*np.sin(A1), L*np.sin(A2))
C = np.add(B, (L*np.cos(A2 + A3)*np.cos(A1), L*np.cos(A2 + A3)*np.sin(A3), L*np.sin(A2 + A3)))
D = np.add(C, (L*np.cos(A2 + A3 + A4)*np.cos(A1), L*np.cos(A2 + A3 + A4)*np.sin(A1), L* np.sin(A2 + A3 + A4)))

N = (ns[0], ns[1], ns[2])

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
        # Map axes to vector components (scaled for visibility)
        x_val = j.get_axis(0) * 150
        y_val = j.get_axis(1) * 150
        # Use axis 2 or 3 for Z depending on controller type
        z_axis_idx = 3 if j.get_numaxes() > 3 else 2
        z_val = j.get_axis(z_axis_idx) * 150 if j.get_numaxes() > 2 else 0

    dx = float(ns[0]) 
    dy = float(ns[1])
    dz = float(ns[2])
    A1 = np.arctan2(dy, dx)
    r = np.hypot(dx, dy)            
    s = dz

    dist = np.hypot(r, s)
    max_reach = 3 * L - 1e-6       
    if dist > max_reach:
        scale = max_reach / dist
        r *= scale
        s *= scale

    if r < 0.01:
        if abs(s) > 0.01:
            A2 = np.arctan2(s, 0)
            A3 = 0.0
            A4 = 0.0
    else:
        c2 = (r*r + s*s - 3*L*L) / (2*L*r)
        c2 = np.clip(c2, -1.0, 1.0)  
        A2 = np.arctan2(s, r) - np.arctan2(np.sqrt(1 - c2*c2), c2)

        c23 = (r - L*np.cos(A2)) / (2*L)
        c23 = np.clip(c23, -1.0, 1.0)  
        A3 = np.arccos(c23) - A2              
        A4 = A3

    B = (L*np.cos(A2)*np.cos(A1), L*np.cos(A2)*np.sin(A1), L*np.sin(A2))
    C = np.array(B) + np.array([L*np.cos(A2+A3)*np.cos(A1),
                        L*np.cos(A2+A3)*np.sin(A1),
                        L*np.sin(A2+A3)])
    D = np.array(C) + np.array([L*np.cos(A2+A3+A4)*np.cos(A1),
                        L*np.cos(A2+A3+A4)*np.sin(A1),
                        L*np.sin(A2+A3+A4)])
        
    # 2. Handle Keyboard Input for Camera Rotation
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  angle_y -= 2 * dt
    if keys[pygame.K_RIGHT]: angle_y += 2 * dt
    if keys[pygame.K_UP]:    angle_x -= 2 * dt
    if keys[pygame.K_DOWN]:  angle_x += 2 * dt

    # 3. Define the vectors to draw
    point_a = np.array([0,0,0])
    point_b = np.array([B[0], B[1], B[2]])
    point_c = np.array([C[0], C[1], C[2]])
    point_d = np.array([D[0], D[1], D[2]])

    point_ab = point_b - point_a
    point_bc = point_c - point_b
    point_cd = point_d - point_c
    vectors = [
        {'color': (255, 0, 0), 'vec': np.array([100, 0, 0])},   # X (Red)
        {'color': (0, 255, 0), 'vec': np.array([0, 100, 0])},   # Y (Green)
        {'color': (0, 0, 255), 'vec': np.array([0, 0, 100])},   # Z (Blue)
        # Joystick/interactive vector — ensure numeric dtype (use current joystick values)
        {'color': (0, 255, 255), 'vec': np.array([point_ab[0], point_ab[1], point_ab[2]], dtype=float)},
        {'color': (255, 255, 0), 'vec': np.array([point_bc[0], point_bc[1], point_bc[2]], dtype=float)},
        {'color': (255, 0, 255), 'vec': np.array([point_cd[0], point_cd[1], point_cd[2]], dtype=float)}
    ]

    # 4. Drawing
    screen.fill((20, 20, 20))
    origin = (width/2, height/2)

    for v_info in vectors:
        end_pos = project(v_info['vec'], angle_x, angle_y)
        pygame.draw.line(screen, v_info['color'], origin, end_pos, 3)
        pygame.draw.circle(screen, v_info['color'], end_pos, 5)

    # UI Text
    font = pygame.font.SysFont(None, 24)
    instr = font.render('Arrows: Rotate Camera | Joystick: Move White Vector', True, (200, 200, 200))
    screen.blit(instr, (20, 20))
    
    pygame.display.flip()

pygame.quit()
