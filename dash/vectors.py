import pygame
import math

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("3D Vectors in Pygame")

# Camera settings
camera_pos = [0, 0, 5]  # [x, y, z]
screen_width, screen_height = 800, 600

# 3D vectors (start_point, end_point)
vectors = [
    ([0, 0, 0], [1, 1, 1]),  # Vector 1
    ([0, 0, 0], [2, -1, 0.5])  # Vector 2
]

def project_point(point, camera_z):
    """Project 3D point to 2D screen coordinates."""
    x, y, z = point
    # Perspective projection
    scale = 500 / (z - camera_z + 1)  # Adjust denominator for depth effect
    x_proj = int(x * scale + screen_width // 2)
    y_proj = int(-y * scale + screen_height // 2)
    return (x_proj, y_proj)

def draw_arrow(surface, start, end, color=(255, 0, 0)):
    """Draw a vector with arrowhead."""
    pygame.draw.line(surface, color, start, end, 2)
    
    # Calculate arrowhead direction
    direction = [end[0] - start[0], end[1] - start[1]]
    length = math.sqrt(direction[0]**2 + direction[1]**2)
    if length > 0:
        direction = [direction[0]/length, direction[1]/length]
        
    # Arrowhead points
    arrow_size = 10
    p1 = (
        end[0] - direction[0] * arrow_size - direction[1] * arrow_size,
        end[1] - direction[1] * arrow_size + direction[0] * arrow_size
    )
    p2 = (
        end[0] - direction[0] * arrow_size + direction[1] * arrow_size,
        end[1] - direction[1] * arrow_size - direction[0] * arrow_size
    )
    
    pygame.draw.polygon(surface, color, [end, p1, p2])

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((15, 15, 30))  # Dark background
    
    # Draw axes
    origin = project_point([0, 0, 0], camera_pos[2])
    x_axis = project_point([5, 0, 0], camera_pos[2])
    y_axis = project_point([0, 5, 0], camera_pos[2])
    z_axis = project_point([0, 0, 5], camera_pos[2])
    
    pygame.draw.line(screen, (255, 0, 0), origin, x_axis)  # X-axis (red)
    pygame.draw.line(screen, (0, 255, 0), origin, y_axis)  # Y-axis (green)
    pygame.draw.line(screen, (0, 0, 255), origin, z_axis)  # Z-axis (blue)
    
    # Draw vectors
    for start, end in vectors:
        start_2d = project_point(start, camera_pos[2])
        end_2d = project_point(end, camera_pos[2])
        draw_arrow(screen, start_2d, end_2d)
    
    pygame.display.flip()

pygame.quit()
