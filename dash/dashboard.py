# AI MODE TOGGLE
# LOGS DISPLAY
# ERRORS OBJECT FOR EASY ACCESS - TODAY
import pygame
import sys
from errors import *
pygame.init()


width, height = 700,700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Static Rect Example")
WHITE = (255, 255, 255)
BLUE = (0,0,255)
font = pygame.font.SysFont('Arial', 20)
static_rect = pygame.Rect(10, height//2, (width//2)-10, (height//2)-10)
logs = ["Hello", "how are you"]


# Game loop
is_clicked = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x,y = pygame.mouse.get_pos()
            if x <= (width//2) + ((width//2) - 100)+ 100 and x >=  (width//2) + ((width//2) - 100):
                if y <= 60 and y >= 10:
                    print("AI mode clicked")
                    is_clicked = not is_clicked
        i = 10
        for line in logs:
            text_surface = font.render(f"> {line}", True, WHITE)
            screen.blit(text_surface, (15, (height//2)+i))
            i += 20
        
        color = None
        if is_clicked:
            color = BLUE
        else:
            color = WHITE
        
        err = Error(1)
        if err.isThrown():
            logs.append(err.get())
                            
        rect = pygame.Rect((width//2) + ((width//2) - 100), 10, 100, 50)
        pygame.draw.rect(screen, color, rect, 1)
        
        text_surface = font.render(f"AI Mode", True, color)
        screen.blit(text_surface, ((width//2) + ((width//2) - 87), 23))
        pygame.draw.rect(screen, WHITE, static_rect, 1)
    
    
    pygame.display.flip()

pygame.quit()
sys.exit()
