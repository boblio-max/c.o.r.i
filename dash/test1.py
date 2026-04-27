import pygame
import sys
import math
import os
import numpy as np

# Define the IKSolver class directly in this cell
class IKSolver:
    """
    Headless Inverse Kinematics solver for the robotic arm.
    Calculates the joint angles (A1, A2, A3, A4) for a given target vector.
    """
    def __init__(self, L=1.0):
        self.L = L

    def solve(self, dx, dy, dz):
        """
        Solves the IK for given target coordinates dx, dy, dz.
        Returns a dictionary of angles in degrees.
        """
        A2, A3, A4 = 0.0, 0.0, 0.0
        L = self.L

        # Angle of base rotation
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
            # IK math for 3-link planar arm (ignoring base rotation which is handled by A1)
            c2 = (r*r + s*s - 3*L*L) / (2*L*r)
            c2 = np.clip(c2, -1.0, 1.0)  
            A2 = np.arctan2(s, r) - np.arctan2(np.sqrt(1 - c2*c2), c2)

            c23 = (r - L*np.cos(A2)) / (2*L)
            c23 = np.clip(c23, -1.0, 1.0)  
            A3 = np.arccos(c23) - A2              
            A4 = A3
            
        angles_deg = {
            'A1': float(np.degrees(A1)),
            'A2': float(np.degrees(A2)),
            'A3': float(np.degrees(A3)),
            'A4': float(np.degrees(A4)),
        }
        
        return angles_deg
        
    def update(self, vector):
        """
        Helper method to solve from a space-separated string "dx dy dz".
        """
        parts = vector.split(" ")
        dx = float(parts[0]) 
        dy = float(parts[1])
        dz = float(parts[2])
        return self.solve(dx, dy, dz)
    
    def solve_from_string(self, vector_str):
        """
        Helper method to solve from a space-separated string "dx dy dz".
        """
        parts = vector_str.split(" ")
        dx = float(parts[0]) 
        dy = float(parts[1])
        dz = float(parts[2])
        return self.solve(dx, dy, dz)

# Initialize IK Solver
L = 1.0 # Arm segment length
solver = IKSolver(L=L)

# Vector utility class for forward kinematics
class VectorCalculator:
    def __init__(self, L=1.0):
        self.L = L
    
    def calculate_positions_from_angles(self, angles_dict):
        """Calculate joint positions A, B, C, D from joint angles dictionary"""
        A1 = np.radians(angles_dict.get('A1', 0))
        A2 = np.radians(angles_dict.get('A2', 0))
        A3 = np.radians(angles_dict.get('A3', 0))
        A4 = np.radians(angles_dict.get('A4', 0))
        
        L = self.L
        
        # Forward kinematics to get joint positions
        # Joint A (Base)
        A = np.array([0.0, 0.0, 0.0])
        
        # Joint B (Shoulder)
        B = np.array([
            L * np.cos(A2) * np.cos(A1),
            L * np.cos(A2) * np.sin(A1),
            L * np.sin(A2)
        ])
        
        # Joint C (Elbow)
        C = B + np.array([
            L * np.cos(A2 + A3) * np.cos(A1),
            L * np.cos(A2 + A3) * np.sin(A1),
            L * np.sin(A2 + A3)
        ])
        
        # Joint D (Wrist)
        D = C + np.array([
            L * np.cos(A2 + A3 + A4) * np.cos(A1),
            L * np.cos(A2 + A3 + A4) * np.sin(A1),
            L * np.sin(A2 + A3 + A4)
        ])
        
        return A, B, C, D

# Initialize Pygame and Joystick
pygame.init()
pygame.joystick.init()

# Screen dimensions (adjusted for both views)
width, height = 1200, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("C.O.R.I DASHBOARD & 3D Visualizer")
clock = pygame.time.Clock()

# Modern color scheme
BACKGROUND = (18, 18, 30)
ACCENT_COLOR = (0, 200, 255)
SECONDARY_ACCENT = (100, 255, 200)
PANEL_BG = (30, 30, 45)
TEXT_COLOR = (220, 220, 255)
WARNING = (255, 180, 50)
DANGER = (255, 80, 80)
SUCCESS = (80, 220, 150)

# Dashboard Gauge parameters
CIRCLE_R = 70
CIRCLE_BORDER = 3
NEEDLE_WIDTH = 3
GAUGE_BG = (40, 40, 60)
NEEDLE_COLOR = ACCENT_COLOR

logs = []
font = pygame.font.SysFont('Arial', 20, bold=True)
small_font = pygame.font.SysFont('Arial', 14)
logs_font = pygame.font.SysFont('Consolas', 15)

joint_angles = [180, 180, 90, 90] # Initial joint angles for gauges

# Positions for the gauges on the left side of the screen
dashboard_width = width // 2 - 50 # Allocate left half for dashboard
col_xs = [dashboard_width // 4, dashboard_width // 4 + dashboard_width // 2]
row_ys = [height // 12 + 40, height // 2 - 120]
circle_positions = []
for r in range(2):
    for c in range(2):
        circle_positions.append((col_xs[c], row_ys[r]))

joint_labels = [f"J{i+1}" for i in range(4)]

# Joysticks initialization
joysticks = []
for i in range(pygame.joystick.get_count()):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    joysticks.append(joy)

# Button states for dashboard
red_button = PANEL_BG
green_button = PANEL_BG
blue_button = PANEL_BG
yellow_button = PANEL_BG

is_clicked_ai = False
is_clicked = False
is_clicked1 = False
is_clicked2 = False
is_clicked3 = False

# 3D View and Vector State
angle_x, angle_y = 0, 0 # Camera rotation angles

# Initialize calculator for 3D visualization
vec_calculator = VectorCalculator(L=L)

def draw_rounded_rect(surface, rect, color, radius=10, border=0):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border > 0:
        pygame.draw.rect(surface, (255, 255, 255), rect, border, border_radius=radius)

def project(vector, angle_x, angle_y, screen_center_x, screen_center_y, scale=150):
    """Projects a 3D vector to 2D screen coordinates with rotation and scaling."""
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
    
    # Apply rotations and scale
    rotated = rx @ (ry @ (vector * scale)) 
    
    # Add screen offset
    return int(rotated[0] + screen_center_x), int(rotated[1] + screen_center_y)

running = True
while running:
    dt = clock.tick(60) / 1000.0

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
                    # This updates J1 directly for claw, potentially overridden by IK later
                    joint_angles[0] = 40 if is_clicked else 180 

                elif event.button == 1:
                    is_clicked_ai = not is_clicked_ai
                    logs.append("AI Mode " + ("Activated" if is_clicked_ai else "Deactivated"))
                    red_button = DANGER if is_clicked_ai else PANEL_BG

                elif event.button == 2:
                    logs.append("Robot returned to original location")
                    blue_button = ACCENT_COLOR if not is_clicked2 else PANEL_BG
                    is_clicked2 = not is_clicked2
                    # Reset joint angles to default (or home position)
                    joint_angles = [180, 180, 90, 90]

                elif event.button == 3:
                    logs.append("Predefined pose activated")
                    yellow_button = WARNING if not is_clicked3 else PANEL_BG
                    is_clicked3 = not is_clicked3
                    joint_angles = [40, 110, 150, 80] if is_clicked3 else [180, 180, 90, 90]
            except Exception: # Handle cases where event.button might not be present (e.g. keyboard)
                pass
        
        # Keyboard input for 3D camera rotation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                angle_y -= 0.1 # Smaller step for smoother rotation
            if event.key == pygame.K_RIGHT:
                angle_y += 0.1
            if event.key == pygame.K_UP:
                angle_x -= 0.1
            if event.key == pygame.K_DOWN:
                angle_x += 0.1

    # Process joystick input for IK
    ik_angles = None
    if joysticks:
        j0 = joysticks[0]
        naxes = j0.get_numaxes()
        ax0 = j0.get_axis(0) if naxes > 0 else 0.0
        ax1 = j0.get_axis(1) if naxes > 1 else 0.0
        # Use axis 2 or 3 for Z depending on controller type, clamped to -1 to 1
        if naxes > 3: # PS4/Xbox often have 4+ axes
            z = j0.get_axis(3) 
        elif naxes > 2: # Older/simpler joysticks might have 3 axes
            z = j0.get_axis(2)
        else:
            z = 0.0
        
        # Scale joystick input to a reasonable range for the arm (e.g., -2 to 2 units)
        # Note: The original had 3.0, let's keep it consistent.
        vector_pass = f"{ax0 * 2.0} {ax1 * 2.0} {z * 2.0}"
        try:
            ik_angles = solver.solve_from_string(vector_pass)
        except Exception as e:
            logs.append(f"IK Error: {e}")

    # Update joint angles from IK solver if available
    if ik_angles:
        try:
            # Apply transformations from IK (norm360, clamp0_180)
            def norm360(x): # Keeps angle between 0 and 360
                return (x % 360 + 360) % 360

            def clamp0_180(x): # Clamps angle between 0 and 180 (for some joints)
                return max(0, min(180, x))
            
            joint_angles[0] = int(round(norm360(ik_angles.get("A1", joint_angles[0])))) # A1 for base rotation
            joint_angles[1] = int(round(clamp0_180(ik_angles.get("A2", joint_angles[1])))) # A2 for shoulder
            joint_angles[2] = int(round(clamp0_180(ik_angles.get("A3", joint_angles[2])))) # A3 for elbow
            joint_angles[3] = int(round(clamp0_180(ik_angles.get("A4", joint_angles[3])))) # A4 for wrist

        except Exception as e:
            logs.append(f"Angle update error: {e}")

    # Calculate 3D joint positions from current joint_angles
    # Convert list of angles to a dictionary for VectorCalculator
    angles_dict_for_fk = {f'A{i+1}': angle for i, angle in enumerate(joint_angles)}
    a, b, c, d = vec_calculator.calculate_positions_from_angles(angles_dict_for_fk)

    # --- Rendering --- 
    screen.fill(BACKGROUND)

    # Draw main panel background for dashboard section
    draw_rounded_rect(screen, pygame.Rect(10, 10, dashboard_width - 20, height-20), PANEL_BG, 20, 2)

    # Draw gauges with modern styling (Left half)
    for i, (pos, angle) in enumerate(zip(circle_positions, joint_angles)):
        # Gauge background
        pygame.draw.circle(screen, GAUGE_BG, pos, CIRCLE_R, CIRCLE_BORDER)

        # Value indicator
        angle_rad = math.radians(angle) # Angles for gauges are 0-180 or 0-360
        nx = pos[0] + CIRCLE_R * 0.8 * math.cos(math.radians(270) - angle_rad) # Start at 270 deg (top) for 0 value
        ny = pos[1] + CIRCLE_R * 0.8 * math.sin(math.radians(270) - angle_rad)

        # Needle with dynamic width (simplified, just constant width)
        pygame.draw.line(screen, NEEDLE_COLOR, pos, (int(nx), int(ny)), NEEDLE_WIDTH)

        # Center point
        pygame.draw.circle(screen, ACCENT_COLOR, pos, 6)

        # Value label
        lbl = small_font.render(f"{joint_labels[i]} {angle}°", True, TEXT_COLOR)
        screen.blit(lbl, (pos[0] - lbl.get_width()//2, pos[1] + CIRCLE_R + 10))

        # Add scale markers (simplified, just a few)
        for j_mark in range(0, 181, 45): # Example: 0, 45, 90, 135, 180
            mark_rad = math.radians(270) - math.radians(j_mark)
            marker_x = pos[0] + (CIRCLE_R - 8) * math.cos(mark_rad)
            marker_y = pos[1] + (CIRCLE_R - 8) * math.sin(mark_rad)
            pygame.draw.circle(screen, TEXT_COLOR, (int(marker_x), int(marker_y)), 2)

    # Draw control panel (below gauges)
    panel_rect = pygame.Rect(dashboard_width//2 - 120, height - 100, 240, 80) # Centered in dashboard half
    draw_rounded_rect(screen, panel_rect, PANEL_BG, 15, 2)

    # Draw control buttons with icons
    buttons = [
        (red_button, "AI MODE", (dashboard_width//2 - 90, height - 75)),
        (green_button, "CLAW", (dashboard_width//2 + 10, height - 75)),
        (blue_button, "HOME", (dashboard_width//2 - 90, height - 35)),
        (yellow_button, "POSE", (dashboard_width//2 + 10, height - 35))
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

    # Draw logs with style (below dashboard elements, in its own panel)
    logs_rect = pygame.Rect(15, height//2 + 20, dashboard_width - 25, height//2 - 40)
    draw_rounded_rect(screen, logs_rect, PANEL_BG, 10, 2) # Use draw_rounded_rect

    for i, line in enumerate(logs[-15:]): # Display last 15 logs
        text_surface = logs_font.render(f"> {line}", True, TEXT_COLOR)
        screen.blit(text_surface, (25, height//2 + 30 + i*20))

    # Draw status indicators (Top right of dashboard section)
    status_x = dashboard_width - 40
    status_y = 30
    # Note: X, Y, Z values here are just placeholders from old code. 
    # A more sophisticated integration would compute these from end effector D position.
    end_effector_pos = d * L # Scale by L to get actual length values
    
    for i, (label, value) in enumerate([("X", f"{end_effector_pos[0]:.1f}"), 
                                        ("Y", f"{end_effector_pos[1]:.1f}"), 
                                        ("Z", f"{end_effector_pos[2]:.1f}") ]):
        status_lbl = small_font.render(f"{label}: {value}mm", True, TEXT_COLOR)
        screen.blit(status_lbl, (status_x - status_lbl.get_width(), status_y + i*25))

    # --- 3D Visualization Rendering (Right half of the screen) --- 
    view_center_x = width * 0.75 # Center of the right half
    view_center_y = height / 2
    view_scale = 150 # Adjust scale for visual size

    # Draw coordinate axes for 3D view
    axis_length = L * view_scale * 0.5 # Scale axes relative to arm length
    pygame.draw.line(screen, (255, 0, 0), project(np.array([0,0,0]), angle_x, angle_y, view_center_x, view_center_y, 0), project(np.array([1,0,0]), angle_x, angle_y, view_center_x, view_center_y, axis_length), 2)
    pygame.draw.line(screen, (0, 255, 0), project(np.array([0,0,0]), angle_x, angle_y, view_center_x, view_center_y, 0), project(np.array([0,1,0]), angle_x, angle_y, view_center_x, view_center_y, axis_length), 2)
    pygame.draw.line(screen, (0, 0, 255), project(np.array([0,0,0]), angle_x, angle_y, view_center_x, view_center_y, 0), project(np.array([0,0,1]), angle_x, angle_y, view_center_x, view_center_y, axis_length), 2)

    # Project the joint positions
    pA = project(a, angle_x, angle_y, view_center_x, view_center_y, view_scale)
    pB = project(b, angle_x, angle_y, view_center_x, view_center_y, view_scale)
    pC = project(c, angle_x, angle_y, view_center_x, view_center_y, view_scale)
    pD = project(d, angle_x, angle_y, view_center_x, view_center_y, view_scale)

    # Draw lines representing arm segments
    pygame.draw.line(screen, SECONDARY_ACCENT, pA, pB, 7) # Base to Shoulder
    pygame.draw.line(screen, ACCENT_COLOR, pB, pC, 7)    # Shoulder to Elbow
    pygame.draw.line(screen, WARNING, pC, pD, 7)         # Elbow to Wrist

    # Draw joints as circles
    pygame.draw.circle(screen, TEXT_COLOR, pA, 10) # Base joint
    pygame.draw.circle(screen, TEXT_COLOR, pB, 10) # Shoulder joint
    pygame.draw.circle(screen, TEXT_COLOR, pC, 10) # Elbow joint
    pygame.draw.circle(screen, DANGER, pD, 12)    # End effector (wrist)

    pygame.display.flip()

pygame.quit()
sys.exit()