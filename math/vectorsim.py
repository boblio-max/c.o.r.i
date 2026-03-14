import pygame, math, sys
import numpy as np

pygame.init()
W, H = 900, 600
screen = pygame.display.set_mode((W, H))
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("consolas", 14)

# ------------------ 3D helpers ------------------
def project(p3d, fov=600):
    """simple perspective projection (camera at origin, looks along -Z)"""
    x, y, z = p3d
    if z <= 0: z = 0.01          # avoid div-by-zero behind camera
    scale = fov / z
    return pygame.Vector2(x * scale + W//2, -y * scale + H//2)

def rotate_yaw_pitch(v, yaw, pitch):
    """rotate vector v by yaw (around Y) and pitch (around X)"""
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    x, y, z = v
    # yaw
    x1 = x * cy - z * sy
    z1 = x * sy + z * cy
    # pitch
    y1 = y * cp - z1 * sp
    z2 = y * sp + z1 * cp
    return pygame.Vector3(x1, y1, z2)

# ------------------ Arrow in 3D ------------------
class Arrow3D:
    def __init__(self):
        self.pos = pygame.Vector3(0, 0, 40)          # 3D position
        self.vel = pygame.Vector3(2, 1, -1)            # 3D velocity
        self.colour = (50, 200, 50)
        self.shaft_len = 6
        self.head_len = 2.5
        self.head_wid  = 2

    def update(self, dt):
        # integrate
        self.pos += self.vel * dt
        # bounce inside invisible box [-40..40] on each axis
        for ax in range(3):
            if abs(self.pos[ax]) > 40:
                self.vel[ax] *= -0.9        # damp a bit

    def draw(self, surf, yaw, pitch):
        # build 5 points: base, tip, head-left, head-right, head-base
        base = pygame.Vector3(-self.shaft_len/2, 0, 0)
        tip  = pygame.Vector3( self.shaft_len/2, 0, 0)
        hb   = tip - pygame.Vector3(self.head_len, 0, 0)
        hl   = hb + pygame.Vector3(0,  self.head_wid/2, 0)
        hr   = hb + pygame.Vector3(0, -self.head_wid/2, 0)

        # rotate to point along velocity direction
        if self.vel.length_squared() > 0.01:
            fwd = self.vel.normalize()
            # pick an arbitrary up-vector not parallel to fwd
            up  = pygame.Vector3(0, 1, 0) if abs(fwd.y) < 0.99 else pygame.Vector3(1, 0, 0)
            right = fwd.cross(up).normalize()
            up    = right.cross(fwd)
            # build 3x3 rotation matrix
            R = np.column_stack([right, up, -fwd])  # neg so arrow points +Z of local coords
        else:
            R = np.eye(3)

        def xform(v):
            v3 = pygame.Vector3(*R.dot(v)) + self.pos
            return rotate_yaw_pitch(v3, yaw, pitch)

        # project to 2D
        pbase = project(xform(base))
        ptip  = project(xform(tip))
        phl   = project(xform(hl))
        phr   = project(xform(hr))
        phb   = project(xform(hb))

        # draw
        pygame.draw.line(surf, self.colour, pbase, phb, 3)
        pygame.draw.polygon(surf, self.colour, [ptip, phl, phb, phr])

# ------------------ main ------------------
arrow = Arrow3D()
yaw, pitch = 0, 0
keys = set()

while True:
    dt = clock.tick(60)/1000.0
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        elif e.type == pygame.KEYDOWN: keys.add(e.key)
        elif e.type == pygame.KEYUP:   keys.discard(e.key)
        elif e.type == pygame.MOUSEMOTION:
            yaw   += e.rel[0] * 0.005
            pitch += e.rel[1] * 0.005
            pitch = max(-math.pi/2, min(math.pi/2, pitch))

    # camera move (moves the arrow, not the camera, for simplicity)
    speed = 20
    if pygame.K_w in keys: arrow.pos.z -= speed * dt
    if pygame.K_s in keys: arrow.pos.z += speed * dt
    if pygame.K_a in keys: arrow.pos.x -= speed * dt
    if pygame.K_d in keys: arrow.pos.x += speed * dt
    if pygame.K_q in keys: arrow.pos.y -= speed * dt
    if pygame.K_e in keys: arrow.pos.y += speed * dt

    arrow.update(dt)

    screen.fill((10, 10, 20))
    arrow.draw(screen, yaw, pitch)

    # HUD
    txt = font.render(f"pos: {arrow.pos}   vel: {arrow.vel}", 1, (200, 200, 200))
    screen.blit(txt, (10, 10))
    pygame.display.flip()