import pygame, random
from text import Text
from conversation import Conversation
from constant import *

class Map:
    ## Constructor for a map instance
    def __init__(self, filename):        
        ## Initialize an int matrix for the map
        self.map = []
        self.start_pos = []
        self.cursor = [0,0]
        self.mon = []
        self.post_pos = []
        self.post_cursor = [0,0]
        self.post_mon = []
        self.passable = ['00', '01', '02', '03', '04', '05', '16', '17', '18', '19', '1a', '1b',
                         '1c', '1d', '1e', '1f', '20', '21', '22', '23', '24', '25', '26', '2a',
                         '2b', '2c', '38', '45', '46', '47', '48', '49', '4b', '4f', '53', '57',
                         '5b', '64', '68', '69', '6a', '6b', '6c', '6d', '8a', '8b', '8c', '8d',
                         '8e', '8f']
        self.obj_text = ['Defeat all enemies!',
                         'Survive 10 turns!',
                         'Defeat the boss!']
        offset = 0
        x = 0
        y = 0
        process_text = False
        process_scroll = False

        prelevel = True
        strings = []
        self.pre_conversations = []
        self.post_conversations = []
        self.scroll = []

        ## Open the file and read in the ints
        with open(filename, 'r') as f:
            data = f.readlines()
            for line in data:
                line = line.lstrip().rstrip()
                if line.startswith('.cursor'):
                    param = line.split(' ')
                    if prelevel:
                        self.cursor = int(param[1]), int(param[2])
                    else:
                        self.post_cursor = int(param[1]), int(param[2])
                elif line.startswith('.objective'):
                    param = line.split(' ')
                    self.objective = int(param[1])
                elif line.startswith('.music'):
                    param = line.split(' ')
                    self.music = int(param[1])
                elif line.startswith('.block'):
                    ## Read in the offset index
                    param = line.split(' ')
                    offset = int(param[1])*144
                elif line.startswith('.start'):
                    param = line.split(' ')
                    pos = int(param[1]), int(param[2]), int(param[3])
                    if prelevel:
                        self.start_pos.append(pos)
                    else:
                        self.post_pos.append(pos)
                elif line.startswith('.monster'):
                    param = line.split(' ')
                    num = int(param[1])
                    x = int(param[2])
                    y = int(param[3])
                    boss = False
                    if len(param) == 5:
                        if param[4].lstrip().rstrip().lower() == 'boss':
                            boss = True
                    if prelevel:
                        self.mon.append((num,x,y,boss))
                    else:
                        self.post_mon.append((num,x,y,boss))
                elif line.startswith('.intro'):
                    process_scroll = True
                elif line.startswith('.endintro'):
                    process_scroll = False
                elif line.startswith('.prelevel'):
                    prelevel = True
                elif line.startswith('.postlevel'):
                    prelevel = False
                elif line.startswith('.talk'):
                    param = line.split(' ')
                    x, y = int(param[1]), int(param[2])
                    process_text = True
                elif line.startswith('.endtalk'):
                    process_text = False
                    conversation = Conversation(strings, (x, y))
                    if prelevel:
                        self.pre_conversations.append(conversation)
                    else:
                        self.post_conversations.append(conversation)
                    strings = []
                elif process_text:
                    strings.append(line)
                elif process_scroll:
                    self.scroll.append(Text(line))
                    
                else:
                    ## Read in integers to populate map
                    array = []
                    if len(line) > 0:
                        line = line.split(' ')
                        for h in line:
                            array.append(h)
                        self.map.append(array)

        self.height = len(self.map)
        self.width  = len(self.map[0])

        self.stars = [[random.randint(0,self.width*TILE_WIDTH),random.randint(0,self.height*TILE_HEIGHT)] for x in xrange(512)]

        self.images = {}
        keys = ['%02x'%(x) for x in xrange(210)]
        sheet = pygame.image.load('res/img/world.png').convert()
        sheet.set_colorkey((255,0,255))

        for y in xrange(6):
            for x in xrange(35):
                sub = sheet.subsurface(x*TILE_WIDTH, offset+y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
                key = keys[x+y*35]
                self.images[key] = sub

    def get_passable(self, x, y):
        tile = self.get_tile(x,y)
        if tile in self.passable:
            return True
        else:
            return False

    def get_cost(self, x, y):
        tile = self.get_tile(x,y)
        if tile in self.passable:
            return 1
        else:
            return 999

    ## Gets the integer value of a tile
    def get_tile(self, x, y):
        return self.map[int(round(y))][int(round(x))]

    ## Draws the map on the target surface
    def render(self, surface):
        for y in xrange(len(self.map)):
            for x in xrange(len(self.map[y])):
                surface.blit(self.images[self.map[y][x]], (x*TILE_WIDTH, y*TILE_HEIGHT))
