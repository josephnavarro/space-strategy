import pygame
class Text(object):
    def __init__(self, string, color = [255, 255, 255], size = 8, scrollable = False, bold=False):
        ## Render the font into a blittable surface
        if bold:
            self.font = pygame.font.Font('res/fon/bold.ttf', size)
        else:
            self.font = pygame.font.Font('res/fon/font.ttf', size)
        self.color = color
        self.text = string
        self.current = len(string) if not scrollable else 0
        self.scrollable = scrollable
        self.height = self.font.get_height()
        self.renderable = self.font.render(self.text[:self.current], False, self.color)
        self.shadow = self.font.render(self.text[:self.current], False, (38,38,38))
        self.width = self.renderable.get_width()

    def draw(self, surface, pos = (0, 0)):
        if self.scrollable:
            ## Blit an animated version of the text
            surface.blit(self.shadow, (pos[0]+1,pos[1]+1))
            surface.blit(self.renderable, pos)
            self.current = min(len(self.text), self.current+1)
            self.update()
        else:
            ## Blit the rendered text at the given position
            surface.blit(self.shadow, (pos[0]-1,pos[1]))
            surface.blit(self.shadow, (pos[0]+1,pos[1]))
            surface.blit(self.shadow, (pos[0],pos[1]+1))
            surface.blit(self.shadow, (pos[0], pos[1]-1))
            surface.blit(self.renderable, pos)

    def update(self, string=None, color=[255,255,255]):
        if self.scrollable:
            ## Animated text
            text = self.text[:self.current]
            self.renderable = self.font.render(text, False, (38,38,38))
            self.shadow = self.font.render(text, False, (144,144,144))
            self.width = self.renderable.get_width()
        ## Update the string only if the text is new
        elif string != None and string != self.text:
            self.text = string
            self.renderable = self.font.render(self.text, False, color)
            self.shadow = self.font.render(self.text, False, (38,38,38))
            self.width = self.renderable.get_width()
