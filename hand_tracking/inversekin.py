from pygame.math import Vector2

a = Vector2(200, -100)
b = Vector2(200, 100)
c = a - b # or Vector2(0, -200)
alpha = a.angle_to(b)