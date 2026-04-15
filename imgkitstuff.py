import pygame
import imgkit
from io import BytesIO

def main():
    config = imgkit.config(wkhtmltoimage=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe')

    pygame.init()
    screen = pygame.display.set_mode((600, 480))

    html = "<style type = 'text/css'> body { font-family: 'Arial' } </style><body><h1>Html rendering</h1><div><ul><li><em>using pygame</em></li><li><strong>using imgkit</strong></li></ul></div></body>"
    img = imgkit.from_string(html, False, config=config)
    surface = pygame.image.load(BytesIO(img)).subsurface((0,0,280,123))
    r = 0
    center = screen.get_rect().center
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return

        screen.fill('white')
        tmp = pygame.transform.rotozoom(surface, r, 1)
        tmp_r = tmp.get_rect(center=center)
        screen.blit(tmp, tmp_r)
        r += 1
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()    
