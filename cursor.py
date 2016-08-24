import pygame
from constant import *

class Cursor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.s = TILE_WIDTH
        self.ds = 0.5

    ## Gets the current bounding box for the viewport
    def get_bounds(self, w, h):
        return (max(0, min(w*TILE_WIDTH-WIDTH,   self.x*TILE_WIDTH+TILE_WIDTH/2-WIDTH/2)),
                max(0, min(h*TILE_HEIGHT-HEIGHT, self.y*TILE_HEIGHT+TILE_HEIGHT/2-HEIGHT/2)),
                WIDTH, HEIGHT)

    ## Draws the cursor on the target surface
    def render(self, surface):
        self.s += self.ds
        if self.s < TILE_WIDTH*3/4 or self.s > TILE_WIDTH:
            self.ds *= -1

        pygame.draw.rect(surface, (38,38,38),    (int(self.x*TILE_WIDTH)+1+(TILE_WIDTH-int(self.s))/2, int(self.y*TILE_HEIGHT)  +(TILE_WIDTH-int(self.s))/2, self.s, self.s), 1)
        pygame.draw.rect(surface, (38,38,38),    (int(self.x*TILE_WIDTH)-1+(TILE_WIDTH-int(self.s))/2, int(self.y*TILE_HEIGHT)  +(TILE_WIDTH-int(self.s))/2, self.s, self.s), 1)
        pygame.draw.rect(surface, (38,38,38),    (int(self.x*TILE_WIDTH)  +(TILE_WIDTH-int(self.s))/2, int(self.y*TILE_HEIGHT)+1+(TILE_WIDTH-int(self.s))/2, self.s, self.s), 1)
        pygame.draw.rect(surface, (38,38,38),    (int(self.x*TILE_WIDTH)  +(TILE_WIDTH-int(self.s))/2, int(self.y*TILE_HEIGHT)-1+(TILE_WIDTH-int(self.s))/2, self.s, self.s), 1)
        pygame.draw.rect(surface, (200,200,200), (int(self.x*TILE_WIDTH)  +(TILE_WIDTH-int(self.s))/2, int(self.y*TILE_HEIGHT)  +(TILE_WIDTH-int(self.s))/2, self.s, self.s), 1)
