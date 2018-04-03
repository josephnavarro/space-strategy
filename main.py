import pygame, random, os, math
from text import Text
from conversation import Conversation
from cursor import Cursor
from moveset import Set
from gamemap import Map
from unit import Unit
from pygame.locals import *
from constant import *
os.environ['SDL_VIDEO_CENTERED'] = '1'

## Initialize pygame and stuff
pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()
pygame.display.set_caption('Space Emblem Saga')
clock = pygame.time.Clock()

class Main:
    ## Constructor for the main method wrapper
    def __init__(self):
        self.window = pygame.display.set_mode((S_WIDTH, S_HEIGHT), SWSURFACE)
        self.screen = pygame.Surface((MAP_WIDTH, MAP_HEIGHT)).convert()
        self.map = Map('res/map/000.map')
        self.cursor = Cursor(self.map.cursor[0],self.map.cursor[1])

        ## The player characters
        self.colorsheet = pygame.image.load('res/img/char00.png').convert()
        self.colorsheet.set_colorkey((255,0,255))
        self.graysheet = pygame.image.load('res/img/char01.png').convert()
        self.graysheet.set_colorkey((255,0,255))

        self.menu_sound = pygame.mixer.Sound('res/snd/001.ogg')
        self.select_sound = pygame.mixer.Sound('res/snd/002.ogg')
        self.turn_sound = pygame.mixer.Sound('res/snd/003.ogg')
        self.hurt_sound = pygame.mixer.Sound('res/snd/004.ogg')
        self.cancel_sound = pygame.mixer.Sound('res/snd/005.ogg')
        self.text_sound = pygame.mixer.Sound('res/snd/006.ogg')
        self.cursor_sound = pygame.mixer.Sound('res/snd/007.ogg')
        self.exp_sound = pygame.mixer.Sound('res/snd/008.ogg')
        self.menu_sound.set_volume(0.35)
        self.select_sound.set_volume(0.35)
        self.turn_sound.set_volume(0.35)
        self.hurt_sound.set_volume(0.35)
        self.cancel_sound.set_volume(0.35)
        self.text_sound.set_volume(0.35)
        self.cursor_sound.set_volume(0.35)
        self.exp_sound.set_volume(0.35)

        self.channel = pygame.mixer.Channel(0)

        self.state = SCROLL
        self.units = []

        for pos in self.map.start_pos:
            unit = Unit(pos[0],pos[1],pos[2],self.colorsheet,self.graysheet,self.map)
            self.units.append(unit)

        for mon in self.map.mon:                
            unit = Unit(mon[1],mon[2],mon[0],self.colorsheet,self.graysheet,self.map,enemy=True,boss=mon[3])
            self.units.append(unit)

        frame = pygame.image.load('res/img/frame.png').convert()
        frame.set_colorkey((255,0,255))

        self.frame = []
        self.bubble = []
        for y in range(3):
            self.frame.append([])
            self.bubble.append([])
            for x in range(3):
                self.frame[y].append(frame.subsurface(56+x*8,y*8,8,8))
                self.bubble[y].append(frame.subsurface(80+x*8,y*8,8,8))

        self.hp_bar = []
        for x in range(8):
            self.hp_bar.append(frame.subsurface(x*2,0,2,12))
        self.hp_fill = [[],[],[]]
        for x in range(6):
            self.hp_fill[0].append(frame.subsurface(x*2,12,2,12))
            self.hp_fill[1].append(frame.subsurface(12+x*2,12,2,12))
            self.hp_fill[2].append(frame.subsurface(24+x*2,12,2,12))

        ## Fade mask
        self.fade_mask = pygame.Surface((WIDTH,HEIGHT)).convert()
        self.fade_mask.fill((38,38,38))
        self.fade_mask.set_alpha(0)
        
        ## Text box
        self.info_box = pygame.Surface((152,60)).convert()
        self.info_box.fill((255,0,255))
        self.info_box.set_colorkey((255,0,255))
        self.draw_box(self.info_box)

        self.rate_box = pygame.Surface((152,64)).convert()
        self.rate_box.fill((255,0,255))
        self.rate_box.set_colorkey((255,0,255))
        self.draw_box(self.rate_box)

        ## Menu box
        self.menu_box = pygame.Surface((72,116)).convert()
        self.menu_box.fill((255,0,255))
        self.menu_box.set_colorkey((255,0,255))
        self.draw_box(self.menu_box)
        
        self.font_text = Text('')
        self.bold_text = Text('', bold=True)

        ## Turn Box
        self.turn_box = pygame.Surface((152,32)).convert()
        self.turn_box.fill((255,0,255))
        self.turn_box.set_colorkey((255,0,255))
        self.draw_box(self.turn_box)

        ## Set Box
        self.stat_box = pygame.Surface((192,148)).convert()
        self.stat_box.fill((255,0,255))
        self.stat_box.set_colorkey((255,0,255))
        self.draw_box(self.stat_box)

        ## Set Box
        self.set_box = pygame.Surface((96,148)).convert()
        self.set_box.fill((255,0,255))
        self.set_box.set_colorkey((255,0,255))
        self.draw_box(self.set_box)

        ## Objective box
        self.obj_box = pygame.Surface((256,32)).convert()
        self.obj_box.fill((255,0,255))
        self.obj_box.set_colorkey((255,0,255))
        self.draw_box(self.obj_box)

        ## Speech Box
        self.speech_box = pygame.Surface((388,128)).convert()
        self.speech_box.fill((255,0,255))
        self.speech_box.set_colorkey((255,0,255))

    def draw_hp(self, surface, unit, pos, index, length=BAR_WIDTH):

        if index == 1:
            width_2 = width = int(length * unit.display_experience / 100.0)
        elif index == 2:
            width = int(length * unit.display_hp / float(unit.max_hp+unit.modifier[0]))
            width_2 = int(length * unit.hp / float(unit.max_hp+unit.modifier[0]))
        
        for x in range(length+1):
            if x == 0 or x == length:
                surface.blit(self.hp_bar[0], (pos[0]+x,pos[1]))
            elif x == 3 or x == length - 3:
                surface.blit(self.hp_bar[3], (pos[0]+x,pos[1]))
            elif x == 2 or x == length - 2:
                surface.blit(self.hp_bar[2], (pos[0]+x,pos[1]))
            elif x == 1 or x == length - 1:
                surface.blit(self.hp_bar[1], (pos[0]+x,pos[1]))
            else:
                surface.blit(self.hp_bar[4], (pos[0]+x,pos[1]))
                
        for x in range(length+1):
            if x == width-1:
                if x == 1 or x == length-1:
                    surface.blit(self.hp_fill[0][0], (pos[0]+x-1,pos[1]))
                elif x == 2 or x == length-2:
                    surface.blit(self.hp_fill[0][1], (pos[0]+x-1,pos[1]))
                else:
                    surface.blit(self.hp_fill[0][2], (pos[0]+x-1,pos[1]))
            elif 2 < x < width-1:
                if x == 3 or x == length-1:
                    surface.blit(self.hp_fill[0][3], (pos[0]+x-1,pos[1]))
                elif x == 4 or x == length-2:
                    surface.blit(self.hp_fill[0][4], (pos[0]+x-1,pos[1]))
                elif 2 < x < length-2:
                    surface.blit(self.hp_fill[0][5], (pos[0]+x-1,pos[1]))
                
        for x in range(length+1):
            if x == width_2-1:
                if x == 1 or x == length-1:
                    surface.blit(self.hp_fill[index][0], (pos[0]+x-1,pos[1]))
                elif x == 2 or x == length-2:
                    surface.blit(self.hp_fill[index][1], (pos[0]+x-1,pos[1]))
                else:
                    surface.blit(self.hp_fill[index][2], (pos[0]+x-1,pos[1]))
            elif 2 < x < width_2-1:
                if x == 3 or x == length-1:
                    surface.blit(self.hp_fill[index][3], (pos[0]+x-1,pos[1]))
                elif x == 4 or x == length-2:
                    surface.blit(self.hp_fill[index][4], (pos[0]+x-1,pos[1]))
                elif 2 < x < length-2:
                    surface.blit(self.hp_fill[index][5], (pos[0]+x-1,pos[1]))

    def draw_bubble(self, surface, pos, target, box, bounds):
        height = box.get_height()//8
        width = box.get_width()//8

        box.fill((255,0,255))

        for y in range(height//2,height):
            for x in range(width):
                if (x,y) == (0,height/2):
                    box.blit(self.bubble[0][0], (x*8,y*8))
                elif (x,y) == (width-1,height/2):
                    box.blit(self.bubble[0][2], (x*8,y*8))
                elif y == height/2:
                    box.blit(self.bubble[0][1], (x*8,y*8))
                elif (x,y) == (0,height-1):
                    box.blit(self.bubble[2][0], (x*8,y*8))
                elif (x,y) == (width-1,height-1):
                    box.blit(self.bubble[2][2], (x*8,y*8))
                elif y == height-1:
                    box.blit(self.bubble[2][1], (x*8,y*8))
                elif x == 0:
                    box.blit(self.bubble[1][0], (x*8,y*8))
                elif x == width-1:
                    box.blit(self.bubble[1][2], (x*8,y*8))
                else:
                    box.blit(self.bubble[1][1], (x*8,y*8))

        c3 = [255,255,255]

        p1a = (target[0]*TILE_WIDTH + TILE_WIDTH/4 - bounds[0], target[1]*TILE_HEIGHT - bounds[1] - TILE_HEIGHT/4 - box.get_height() + 1)
        p2a = (box.get_width()*2/4 - 6, box.get_height()/2 + 1)
        p3a = (box.get_width()*2/4 + 6, box.get_height()/2 + 1)
        pygame.draw.polygon(box, c3, (p1a,p2a,p3a))

        box.set_alpha(192)

        surface.blit(box, pos)        
        
    def draw_box(self, surface):
        height = surface.get_height()//8
        width = surface.get_width()//8
        
        for y in range(height):
            for x in range(width):
                if (x,y) == (0,0):
                    surface.blit(self.frame[0][0], (x*8,y*8))
                elif (x,y) == (width-1,0):
                    surface.blit(self.frame[0][2], (x*8,y*8))
                elif y == 0:
                    surface.blit(self.frame[0][1], (x*8,y*8))
                elif (x,y) == (0,height-1):
                    surface.blit(self.frame[2][0], (x*8,y*8))
                elif (x,y) == (width-1,height-1):
                    surface.blit(self.frame[2][2], (x*8,y*8))
                elif y == height-1:
                    surface.blit(self.frame[2][1], (x*8,y*8))
                elif x == 0:
                    surface.blit(self.frame[1][0], (x*8,y*8))
                elif x == width-1:
                    surface.blit(self.frame[1][2], (x*8,y*8))
                else:
                    surface.blit(self.frame[1][1], (x*8,y*8))

        surface.set_alpha(192)
                
    def main(self):
        ## Music
        pygame.mixer.music.load('res/mus/000.ogg')
        pygame.mixer.music.set_volume(0.5)
        #pygame.mixer.music.play()
        ## Movement variables
        move_up = False
        move_down = False
        move_right = False
        move_left = False

        ## Unit selection variables
        selected = None
        unit_follow = False
        unit_shake = 0
        unit_lean = 0
        lean_coord = None
        lean_orig = None
        attack_target = None

        ## Cursor movement variables
        cursor_dx = 0
        cursor_dy = 0

        ## Damage countdown display
        damage_count = 0.0
        turn = PLAYER_TURN
        turn_wait = 0

        ## Turn change effect
        scale = 1.0
        target_scale = 1.0
        cooldown = 0.0
        turn_count = 0

        ## Whether to end the game
        player_win = False
        enemy_win = False

        ## Current menu selection
        set_choice = 0
        menu_choice = 0
        menu_string = {0:'Attack', 1:'Move', 2:'Equip', 3:'Stats', 4:'Wait', 5:'Cancel'}
        stat_string = {0:'HP ',
                       1:'Atk',
                       2:'Def',
                       3:'Spd',
                       4:'Rng',
                       5:'Mov'}
        stat_up = [0,0,0,0,0,0]

        ## Unit cycling
        cycle = 0
        scroll_y = 0
        fade_out = 0
        post_fade = -1
        exp_wait = -1
        keybuffer = 0.0

        ## Conversation target
        conversation_target = None
        
        while True:
            #if not pygame.mixer.music.get_busy():
                #pygame.mixer.music.play()
                
            tick = clock.tick(FPS) / 1000.0

            ## Render everything to the screen
            self.screen.fill((38,38,38))
            for star in self.map.stars:
                star[0] += 1
                if star[0] >= self.map.width*TILE_WIDTH:
                    star[0] = 0
                pygame.draw.rect(self.screen, (200,200,200), (star[0],star[1],2,2))

            if self.state != SCROLL:
                self.map.render(self.screen)

            if self.state == INTRO and len(self.map.pre_conversations) == 0:
                if fade_out == 0:
                    target_scale = 2.0
                    fade_out = -3.0
                elif fade_out < 0:
                    fade_out += tick
                    if fade_out >= 0:
                        self.state = IDLE

            if conversation_target:
                if abs(self.cursor.x - conversation_target[0]) > abs(cursor_dx * 0.25) or abs(self.cursor.y - conversation_target[1]) > abs(cursor_dy * 0.25):
                    self.cursor.x += cursor_dx * 0.5
                    self.cursor.y += cursor_dy * 0.5
                else:
                    self.cursor.x = int(round(self.cursor.x))
                    self.cursor.y = int(round(self.cursor.y))
                    cursor_dx = 0
                    cursor_dy = 0
                    conversation_target = None

            unit_follow = False
            for unit in self.units:
                if unit.disappear > 0:
                    unit.disappear -= 15
                    for bank in unit.sets[unit.current].images:
                        for image in bank:
                            image.set_alpha(min(255,unit.disappear))
                    if unit.disappear <= 0:
                        self.units.remove(unit)
                        
                elif int(round(unit.display_hp)) <= 0:
                    unit.disappear = 512
                    
                elif unit.moving:
                    if abs(self.cursor.x - unit.pos[0]) > 1 or abs(self.cursor.y - unit.pos[1]) > 1:
                        self.cursor.x += cursor_dx * 0.5
                        self.cursor.y += cursor_dy * 0.5
                    else:
                        cursor_dx = 0
                        cursor_dy = 0
                        menu_choice = 0
                        unit_follow = True
                        unit.move(self.units, clock)
                        self.cursor.x = unit.pos[0]
                        self.cursor.y = unit.pos[1]
                        
                elif selected == unit:
                    render = True
                    if unit.has_moved and self.state not in [DAMAGE, BREAK, LEVELUP]:
                        if unit.is_enemy and turn == ENEMY_TURN:
                            self.state = ATTACK
                            if unit.attack_target and unit.attack_enemy(unit.attack_target[1],unit.attack_target[0],self.units):
                                attack_target = unit.attack_target
                                self.state = DAMAGE
                                damage_count = 0.5
                            elif turn_wait <= 0:
                                unit.clear()
                                unit.stop(self.units)
                                unit.end_move = True
                                turn_wait = 0.25
                                
                        elif not unit.is_enemy and turn == PLAYER_TURN and turn_wait <= 0:
                            if self.state not in [ATTACK, ITEM, SCROLL, INTRO, STATS]:
                                self.state = MENU

                        if turn_wait > 0:
                            turn_wait -= tick
                            if turn_wait <= 0:
                                turn_wait = 0
                                
                                selected = None
                                attack_target = None
                                self.state = IDLE
                            
                    if render:
                        unit.render_move(self.units, self.screen)

            if self.state != SCROLL:
                if not unit_follow and self.state != DAMAGE and scale == 1.0 and turn_wait <= 0:
                    if len(self.map.post_conversations) > 0:
                        self.cursor.render(self.screen)

                for unit in self.units:
                    unit.render(self.screen)

            ## Get the viewport and blit it to the window
            bounds = self.cursor.get_bounds(self.map.width, self.map.height)
            surface = self.screen.subsurface(bounds)

            if post_fade > 0:
                self.fade_mask.set_alpha(int(255*(3.0-post_fade)/3.0))
                surface.blit(self.fade_mask, (0,0))

            if self.state == DAMAGE:
                if unit_shake == 0:
                    damaged = False
                    for unit in self.units:
                        if unit == selected:
                            unit_lean = 8
                            
                        elif unit.damage_buf > 0:
                            unit.shake = True
                            unit_shake = 0.25
                            damaged = True
                            self.channel.play(self.hurt_sound)
                            lean_coord = unit.pos
                            lean_orig = selected.pos[:]

                    if not damaged:
                        if damage_count > 0:
                            damage_count -= tick
                        else:
                            unit_shake = 0
                            
                            selected.clear()
                            selected.stop(self.units)
                            selected.end_move = True
                            
                            attack_target = None
                            self.state = IDLE
                else:
                    if unit_lean > 0:
                        rx, ry = int(round(lean_coord[0])) - int(round(lean_orig[0])), int(round(lean_coord[1])) - int(round(lean_orig[1]))
                        drx = -1 if rx < 0 else (1 if rx > 0 else 0)
                        dry = -1 if ry < 0 else (1 if ry > 0 else 0)
                        selected.pos[0] += drx * tick * (-5 if unit_lean <= 4 else 5)
                        selected.pos[1] += dry * tick * (-5 if unit_lean <= 4 else 5)
                        unit_lean -= 1

                    else:
                        if lean_orig:
                            for unit in self.units:
                                if unit.damage_buf > 0:
                                    unit.hp = max(0, unit.hp - unit.damage_buf)
                                    unit.damage_buf = 0
                            selected.pos = lean_orig
                            unit_lean = 0
                            lean_orig = None
                            lean_coord = None
                        
                        unit_shake -= tick
                        if unit_shake <= 0:
                            for unit in self.units:
                                if unit.shake:
                                    unit.shake = False
                            
                            tick_down = True
                            for unit in self.units:
                                if unit.hp < unit.display_hp:
                                    unit.display_hp = max(unit.hp, unit.display_hp - tick * 50)
                                    tick_down = False
                                    
                            if tick_down:
                                if damage_count > 0:
                                    damage_count -= tick
                                else:
                                    do_clear = True
                                    if selected.experience > selected.display_experience:
                                        selected.display_experience = min(selected.experience, selected.display_experience + tick * 50)
                                        if not self.channel.get_busy():
                                            self.channel.play(self.exp_sound, -1)

                                        if selected.display_experience >= selected.experience:
                                            self.channel.stop()
                                            
                                            if selected.display_experience >= 99:
                                                selected.display_experience = 0
                                                selected.experience = 0
                                                selected.level += 1

                                                stat_up = [random.randint(0,1), random.randint(0,1), random.randint(0,1), random.randint(0,1), 0, 0]
                                                selected.modifier[0] += stat_up[0]
                                                selected.modifier[1] += stat_up[1]
                                                selected.modifier[2] += stat_up[2]
                                                selected.modifier[3] += stat_up[3]

                                                selected.hp = selected.max_hp+selected.modifier[0]

                                                self.state = LEVELUP
                                           
                                        do_clear = False
                                        
                                    elif exp_wait == -1:
                                        exp_wait = 0.5
                                        do_clear = False
                                        
                                    elif exp_wait > 0:
                                        exp_wait -= tick
                                        do_clear = False
                                        
                                    if do_clear:
                                        exp_wait = -1
                                        unit_shake = 0
                                        self.state = BREAK
                                    else:
                                        pos = (WIDTH/2-self.info_box.get_width()/2, HEIGHT/2-self.info_box.get_height()/2)
                                        surface.blit(self.info_box, pos)
                                        self.draw_hp(surface, selected, (pos[0]+12-1,pos[1]+22), 1)
                                        
                                        self.bold_text.update('%s' %(selected.name))
                                        self.bold_text.draw(surface, (pos[0]+12,pos[1]+4))
                                        self.font_text.update('Lv.%d' %(selected.level))
                                        self.font_text.draw(surface, (pos[0]+12+self.bold_text.width+4, pos[1]+4))
                                        
                                        self.font_text.update('%02d/99' %(int(round(selected.display_experience))))
                                        self.font_text.draw(surface, (pos[0]+12,pos[1]+32))

            elif self.state == LEVELUP:
                if selected.hp > selected.display_hp:
                    selected.display_hp = min(selected.hp, selected.display_hp + tick * 50)
                    
                pos = (WIDTH/2-self.info_box.get_width()/2, HEIGHT/2-self.info_box.get_height()/2)
                surface.blit(self.info_box, pos)
                self.draw_hp(surface, selected, (pos[0]+12-1,pos[1]+22), 1)
                
                self.bold_text.update('%s' %(selected.name))
                self.bold_text.draw(surface, (pos[0]+12,pos[1]+4))
                self.font_text.update('Lv.%d' %(selected.level))
                self.font_text.draw(surface, (pos[0]+12+self.bold_text.width+4, pos[1]+4))
                
                self.font_text.update('%02d/99' %(int(round(selected.display_experience))))
                self.font_text.draw(surface, (pos[0]+12,pos[1]+32))
                
                top = 4+self.turn_box.get_height()+2
                left = 8
                surface.blit(self.set_box, (left,top))
                select_stats = [selected.base_attack,
                                selected.base_defense,
                                selected.base_speed,
                                selected.base_orig_range,
                                selected.base_orig_movement-1
                                ]
                self.bold_text.update('Level up!')
                self.bold_text.draw(surface, (left+12,top+4))
                
                for x in range(5):
                    self.bold_text.update('%s' %(stat_string[x]))
                    self.bold_text.draw(surface, (left+12,top+30+16*x))
                    self.font_text.update('+%d' %(stat_up[x]), color = [0,248,0] if stat_up[x] > 0 else [255,255,255])
                    self.font_text.draw(surface, (left+12+self.set_box.get_width()/2,top+30+16*x))

            elif self.state == BREAK:
                if selected.sets[selected.current].uses == 0:
                    pos = (WIDTH/2-self.obj_box.get_width()/2, HEIGHT/2-self.obj_box.get_height()/2)
                    surface.blit(self.obj_box, pos)
                    self.font_text.update('%s\'s %s broke.' %(selected.name, selected.sets[selected.current].name))
                    self.font_text.draw(surface, (pos[0]+self.obj_box.get_width()/2-self.font_text.width/2,pos[1]+4))
                else:
                    selected.clear()
                    selected.stop(self.units)
                    selected.end_move = True
                    
                    attack_target = None
                    self.state = IDLE

            elif self.state == STATS:
                top = 8+self.turn_box.get_height()
                left = 8
                surface.blit(self.stat_box, (left,top))
                select_stats = [selected.base_attack+selected.modifier[1],
                                selected.base_defense+selected.modifier[2],
                                selected.base_speed+selected.modifier[3],
                                selected.base_orig_range,
                                selected.base_orig_movement-1
                                ]
                select_sets = [selected.sets[selected.current].attack,
                               selected.sets[selected.current].defense,
                               selected.sets[selected.current].speed,
                               selected.sets[selected.current].orig_range,
                               selected.sets[selected.current].orig_movement
                               ]

                self.draw_hp(surface, selected, (left+12-1, top+22), 2, length=82)
                self.font_text.update('%02d/%02d' %(int(round(selected.display_hp)),selected.max_hp+selected.modifier[0]))
                self.font_text.draw(surface, (left+12,top+32))
                
                self.draw_hp(surface, selected, (left+16+82-1, top+22), 1, length=82)
                self.font_text.update('%02d/99' %int(round(selected.display_experience)))
                self.font_text.draw(surface, (left+16+82,top+32))

                self.bold_text.update('%s' %(selected.name))
                self.bold_text.draw(surface, (left+12,top+4))
                self.font_text.update('Lv.%d' %(selected.level))
                self.font_text.draw(surface, (left+12+self.bold_text.width+4, top+4))
                
                for x in range(3):
                    self.bold_text.update('%s' %(stat_string[x+1]))
                    self.bold_text.draw(surface, (left+12,top+60+16*x))
                    self.font_text.update('%d+%d' %(select_stats[x], select_sets[x]))
                    self.font_text.draw(surface, (left+12+self.stat_box.get_width()/4,top+60+16*x))
                    
                for x in range(2):
                    self.bold_text.update('%s' %(stat_string[x+4]))
                    self.bold_text.draw(surface, (left+100,top+60+16*x))
                    self.font_text.update('%d+%d' %(select_stats[x+3], select_sets[x+3]))
                    self.font_text.draw(surface, (left+100+self.stat_box.get_width()/4,top+60+16*x))

                if selected.is_boss:
                    self.bold_text.update('Boss!', color=[255,255,0])
                    self.bold_text.draw(surface, (left+100,top+60+16*2))

                self.font_text.update('%s' %(selected.sets[selected.current].name))
                self.font_text.draw(surface, (left+12, top+68+16*3))

            if self.state not in [INTRO, SCROLL, STATS]:
                for unit in self.units:
                    if self.state == ATTACK:
                        if selected != unit and self.cursor.x == int(round(unit.pos[0])) and self.cursor.y == int(round(unit.pos[1])):
                            top = HEIGHT-self.info_box.get_height()-self.rate_box.get_height()-4
                            left = 8
                            
                            select_stats = [selected.base_attack+selected.modifier[1],
                                            selected.base_defense+selected.modifier[2],
                                            selected.base_speed+selected.modifier[3]]
                            select_sets  = [selected.sets[selected.current].attack,
                                            selected.sets[selected.current].defense,
                                            selected.sets[selected.current].speed]
                            unit_stats   = [unit.base_attack+unit.modifier[1],
                                            unit.base_defense+unit.modifier[2],
                                            unit.base_speed+unit.modifier[3]]
                            unit_sets    = [unit.sets[unit.current].attack,
                                            unit.sets[unit.current].defense,
                                            unit.sets[unit.current].speed]

                            surface.blit(self.rate_box, (left,top))
                            for x in range(3):
                                self.bold_text.update('%s' %(stat_string[x+1]))
                                self.bold_text.draw(surface, (left+12,top+4+16*x))
                                self.font_text.update('%d+%d' %(select_stats[x], select_sets[x]))
                                self.font_text.draw(surface, (left+12+self.rate_box.get_width()/4,top+4+16*x))
                                
                            left = WIDTH-self.rate_box.get_width()-8
                            surface.blit(self.rate_box, (left,top))
                            for x in range(3):
                                self.bold_text.update('%s' %(stat_string[x+1]))
                                self.bold_text.draw(surface, (left+12,top+4+16*x))
                                self.font_text.update('%d+%d' %(unit_stats[x], unit_sets[x]))
                                self.font_text.draw(surface, (left+12+self.rate_box.get_width()/4,top+4+16*x))
                            
                    if not selected:
                        if self.cursor.x == int(round(unit.pos[0])) and self.cursor.y == int(round(unit.pos[1])) and not (player_win or enemy_win):
                            top = HEIGHT-self.info_box.get_height()-4
                            surface.blit(self.info_box, (8,top))
                            self.bold_text.update('%s' %(unit.name))
                            self.bold_text.draw(surface, (20,top+4))
                            self.font_text.update('Lv.%d' %(unit.level))
                            self.font_text.draw(surface, (20+self.bold_text.width+4, top+4))
                            
                            self.font_text.update('%02d/%02d' %(int(round(unit.display_hp)),unit.max_hp+unit.modifier[0]))
                            self.font_text.draw(surface, (20,top+32))

                            left = 24+self.font_text.width

                            self.font_text.update('%s' %(unit.sets[unit.current].name))
                            self.font_text.draw(surface, (left,top+32))

                            self.draw_hp(surface, unit, (20-1, top+22), 2)
                            #self.draw_hp(surface, unit, (20, top+34), 1)
                    else:
                        if selected == unit:
                            top = HEIGHT-self.info_box.get_height()-4
                            surface.blit(self.info_box, (8,top))
                            self.bold_text.update('%s' %(unit.name))
                            self.bold_text.draw(surface, (20,top+4))
                            self.font_text.update('Lv.%d' %(unit.level))
                            self.font_text.draw(surface, (20+self.bold_text.width+4, top+4))

                            self.font_text.update('%02d/%02d' %(int(round(unit.display_hp)),unit.max_hp+unit.modifier[0]))
                            self.font_text.draw(surface, (20,top+32))

                            left = 24+self.font_text.width

                            self.font_text.update('%s' %(unit.sets[unit.current].name))
                            self.font_text.draw(surface, (left,top+32))
                            
                            self.draw_hp(surface, unit, (20-1, top+22), 2)
                            #self.draw_hp(surface, unit, (20, top+34), 1)
                            
                        elif self.cursor.x == int(round(unit.pos[0])) and self.cursor.y == int(round(unit.pos[1])) and not selected.moving:
                            top = HEIGHT-self.info_box.get_height()-4
                            left = WIDTH-self.info_box.get_width()-8
                            surface.blit(self.info_box, (left,top))
                            
                            self.bold_text.update('%s' %(unit.name))
                            self.bold_text.draw(surface, (left+12,top+4))
                            self.font_text.update('Lv.%d' %(unit.level))
                            self.font_text.draw(surface, (left+12+self.bold_text.width+4, top+4))

                            self.font_text.update('%02d/%02d' %(int(round(unit.display_hp)),unit.max_hp+unit.modifier[0]))
                            self.font_text.draw(surface, (left+12,top+32))

                            w = self.font_text.width

                            self.font_text.update('%s' %(unit.sets[unit.current].name))
                            self.font_text.draw(surface, (left+w+16,top+32))
                            
                            self.draw_hp(surface, unit, (left+12-1, top+22), 2)
                            #self.draw_hp(surface, unit, (left+12, top+34), 1)

                        elif attack_target == (int(round(unit.pos[1])), int(round(unit.pos[0]))):
                            top = HEIGHT-self.info_box.get_height()-4
                            left = WIDTH-self.info_box.get_width()-8
                            surface.blit(self.info_box, (left,top))

                            self.bold_text.update('%s' %(unit.name))
                            self.bold_text.draw(surface, (left+12,top+4))
                            self.font_text.update('Lv.%d' %(unit.level))
                            self.font_text.draw(surface, (left+12+self.bold_text.width+4, top+4))

                            self.font_text.update('%02d/%02d' %(int(round(unit.display_hp)),unit.max_hp+unit.modifier[0]))
                            self.font_text.draw(surface, (left+12,top+32))

                            w = self.font_text.width

                            self.font_text.update('%s' %(unit.sets[unit.current].name))
                            self.font_text.draw(surface, (left+w+16,top+32))
                            
                            self.draw_hp(surface, unit, (left+12-1, top+22), 2)
                            #self.draw_hp(surface, unit, (left+12, top+34), 1)
                            
            if self.state in [MENU, ITEM, STATS]:
                top = 8
                left = WIDTH-self.menu_box.get_width()-8
                surface.blit(self.menu_box, (left,top))
                for x in range(len(menu_string)):
                    color = [255,255,255]
                    if x == menu_choice and not (x == 2 and selected.has_used_item) and not (x == 1 and selected.has_moved):
                        color = [248,248,0]
                    elif x in [0,1,2,4] and (selected.is_enemy or selected.end_move):
                        color = [160,160,160]
                    elif x == 1 and selected.has_moved:
                        color = [160,160,160]
                    elif x == 2 and selected.has_used_item:
                        color = [160,160,160]
                        
                    self.font_text.update(menu_string[x], color)
                    self.font_text.draw(surface, (left+12, top+4+x*16))

                if self.state == ITEM:
                    top = 8+self.turn_box.get_height()
                    left = 8
                    surface.blit(self.set_box, (left,top))
                    surface.blit(self.set_box, (left+self.set_box.get_width(),top))
                    
                    for x in range(8):
                        color = [255,255,255]
                        if x == selected.current:
                            color = [248,248,0]

                        if x < len(selected.sets):
                            self.font_text.update(selected.sets[x].name, color)
                        else:
                            self.font_text.update('---')
                        
                        self.font_text.draw(surface, (left+12, top+4+x*16))

                    for x in range(8):
                        if x == 0:
                            string1 = '+%d' %(selected.sets[selected.current].attack)
                            string2 = 'Atk'
                            color = [0,248,0] if selected.sets[selected.current].attack > 0 else [255,255,255]
                        elif x == 1:
                            string1 = '+%d' %(selected.sets[selected.current].defense)
                            string2 = 'Def'
                            color = [0,248,0] if selected.sets[selected.current].defense > 0 else [255,255,255]
                        elif x == 2:
                            string1 = '+%d' %(selected.sets[selected.current].speed)
                            string2 = 'Spd'
                            color = [0,248,0] if selected.sets[selected.current].speed > 0 else [255,255,255]
                        elif x == 3:
                            string1 = '+%d' %(selected.sets[selected.current].orig_range)
                            string2 = 'Rng'
                            color = [0,248,0] if selected.sets[selected.current].orig_range > 0 else [255,255,255]
                        elif x == 4:
                            string1 = '+%d' %(selected.sets[selected.current].orig_movement)
                            string2 = 'Mov'
                            color = [0,248,0] if selected.sets[selected.current].orig_movement > 0 else [255,255,255]
                        elif x == 5 and selected.sets[selected.current].uses > 0:
                            string1 = '%d' %(selected.sets[selected.current].uses)
                            string2 = 'Uses'
                            color = [255,255,255]
                        else:
                            string1 = ''
                            string2 = ''
                            color = [255,255,255]
                            
                        self.bold_text.update(string2)
                        self.bold_text.draw(surface, (left+12+self.set_box.get_width(), top+4+x*16))
                        self.font_text.update(string1, color)
                        self.font_text.draw(surface, (left+12+self.set_box.get_width()+self.set_box.get_width()/2, top+4+x*16))
                    

            if self.state not in [SCROLL, INTRO, DAMAGE]:
                if self.state != LEVELUP:
                    if player_win:
                        if post_fade == -2:
                            if len(self.map.post_conversations) > 0:
                                top = HEIGHT-self.speech_box.get_height()-8
                                c = self.map.post_conversations[0]
                                if int(round(self.cursor.x)) == c.pos[0] and int(round(self.cursor.y)) == c.pos[1]:
                                    if cursor_dx == 0 and cursor_dy == 0:
                                        self.draw_bubble(surface, (8,top), c.pos, self.speech_box, bounds)
                                    
                                    c.draw(surface, (20,top+4+self.speech_box.get_height()/2))
                                    if c.dialogue[c.current][0].current == 1:
                                        self.channel.play(self.text_sound, -1)
                                    elif c.dialogue[c.current][0].current == len(c.dialogue[c.current][0].text) and\
                                         c.dialogue[c.current][1].current == len(c.dialogue[c.current][1].text) and\
                                         c.dialogue[c.current][2].current == len(c.dialogue[c.current][2].text):
                                        self.channel.stop()
                            else:
                                top = HEIGHT/2 - self.turn_box.get_height()/2 - self.info_box.get_height()/2
                                left = WIDTH/2 - self.turn_box.get_width()/2
                                surface.blit(self.turn_box, (left,top))
                                self.bold_text.update('Victory!')
                                self.bold_text.draw(surface, (WIDTH/2-self.bold_text.width/2,top+6))
                                
                        elif post_fade == -1:
                            post_fade = 3.0
                        elif post_fade > 0:
                            post_fade -= tick
                        else:
                            surface.blit(self.fade_mask, (0,0))
                            self.units = []
                            
                            for pos in self.map.post_pos:
                                unit = Unit(pos[0],pos[1],pos[2],self.colorsheet,self.graysheet,self.map)
                                self.units.append(unit)

                            for mon in self.map.post_mon:                
                                unit = Unit(mon[1],mon[2],mon[0],self.colorsheet,self.graysheet,self.map,enemy=True,boss=mon[3])
                                self.units.append(unit)

                            self.cursor.x = self.map.post_cursor[0]
                            self.cursor.y = self.map.post_cursor[1]
                            if len(self.map.post_conversations) > 0:
                                conversation_target = self.map.post_conversations[0].pos
                                dx = self.map.post_conversations[0].pos[0] - self.cursor.x
                                dy = self.map.post_conversations[0].pos[1] - self.cursor.y
                                d  = math.sqrt(dx*dx + dy*dy)
                                if d > 0:
                                    cursor_dx = dx / d
                                    cursor_dy = dy / d

                            self.map.objective = -1
                            post_fade = -2
                            
                    elif enemy_win:
                        top = HEIGHT/2 - self.turn_box.get_height()/2 - self.info_box.get_height()/2
                        left = WIDTH/2 - self.turn_box.get_width()/2
                        surface.blit(self.turn_box, (left,top))
                        self.bold_text.update('Defeated...')
                        self.bold_text.draw(surface, (WIDTH/2-self.bold_text.width/2,top+6))
                        
                if not player_win and not enemy_win:
                    surface.blit(self.turn_box, (8,8))
                    if turn == PLAYER_TURN:
                        self.bold_text.update(' Player\'s Turn')
                    else:
                        self.bold_text.update(' Enemy\'s Turn')
                    self.bold_text.draw(surface, (12,14))

            if self.state == INTRO:
                if len(self.map.pre_conversations) > 0:
                    top = HEIGHT-self.speech_box.get_height()-8
                    c = self.map.pre_conversations[0]
                    if int(round(self.cursor.x)) == c.pos[0] and int(round(self.cursor.y)) == c.pos[1]:
                        if len(c.dialogue) > 0:
                            if cursor_dx == 0 and cursor_dy == 0:
                                self.draw_bubble(surface, (8,top), c.pos, self.speech_box, bounds)
                            
                            c.draw(surface, (20,top+4+self.speech_box.get_height()/2))
                            if c.dialogue[c.current][0].current == 1:
                                self.channel.play(self.text_sound, -1)
                            elif c.dialogue[c.current][0].current == len(c.dialogue[c.current][0].text) and\
                                 c.dialogue[c.current][1].current == len(c.dialogue[c.current][1].text) and\
                                 c.dialogue[c.current][2].current == len(c.dialogue[c.current][2].text):
                                self.channel.stop()
                else:
                    cursor_dx = 0
                    cursor_dy = 0
                    top = HEIGHT/2 - self.obj_box.get_height()/2
                    left = WIDTH/2 - self.obj_box.get_width()/2
                    surface.blit(self.obj_box, (left,top))
                    self.bold_text.update(self.map.obj_text[self.map.objective])
                    self.bold_text.draw(surface, (WIDTH/2-self.bold_text.width/2,top+6))

            if self.state == SCROLL:
                scroll_y += 0.5
                if fade_out <= 0:
                    for x in range(len(self.map.scroll)):
                        self.map.scroll[x].draw(surface, (WIDTH/2-self.map.scroll[x].width/2,HEIGHT-int(scroll_y)+x*16))
                        if x == len(self.map.scroll) - 1 and HEIGHT-scroll_y+x*16 <= -64:
                            fade_out = 3.0

                else:
                    fade_out -= tick
                    surface.blit(self.fade_mask, (0,0))
                    self.fade_mask.set_alpha(int(255*(3.0-fade_out)/3.0))
                    if fade_out <= 0:
                        if len(self.map.pre_conversations) > 0:
                            conversation_target = self.map.pre_conversations[0].pos
                            dx = self.map.pre_conversations[0].pos[0] - self.cursor.x
                            dy = self.map.pre_conversations[0].pos[1] - self.cursor.y
                            d  = math.sqrt(dx*dx + dy*dy)
                            if d > 0:
                                cursor_dx = dx / d
                                cursor_dy = dy / d
                        fade_out = 0
                        self.state = INTRO
                        ## Music
                        pygame.mixer.music.load('res/mus/%03d.ogg' %(self.map.music))
                        pygame.mixer.music.set_volume(0.5)
                        #pygame.mixer.music.play()

            surface_1 = pygame.transform.scale(surface, (S_WIDTH, S_HEIGHT))
            self.window.blit(surface_1, (0,0))
            
            if scale > 1:
                surface_2 = pygame.transform.scale(surface, (int(S_WIDTH*scale), int(S_HEIGHT*scale))).convert()
                surface_2.set_alpha(int(64*(2.0-scale)))
                self.window.blit(surface_2, surface_2.get_rect(center=(S_WIDTH/2,S_HEIGHT/2)))

            ## Update the display
            pygame.display.flip()

            ## Update the turns
            if not player_win and not enemy_win:
                change_turn = True if turn_wait <= 0 else False
                for unit in self.units:
                    if turn == PLAYER_TURN and not unit.is_enemy and not unit.end_move:
                        change_turn = False
                    elif turn == ENEMY_TURN and unit.is_enemy and not unit.end_move:
                        change_turn = False

                if change_turn:
                    if turn == PLAYER_TURN:
                        for unit in self.units:
                            if unit.is_enemy:
                                unit.refresh(item=True)
                            else:
                                unit.clear()
                                unit.end_move = False
                        turn = ENEMY_TURN
                        target_scale = 2.0
                        self.channel.play(self.turn_sound)
                    else:
                        for unit in self.units:
                            if not unit.is_enemy:
                                unit.refresh(item=True)
                            else:
                                unit.clear()
                                unit.end_move = False
                        turn = PLAYER_TURN
                        target_scale = 2.0
                        self.channel.play(self.turn_sound)
                        turn_count += 1
                        
            if target_scale > scale:
                scale += 0.025
                
                if scale >= target_scale:
                    scale = 1.0
                    target_scale = 1.0
                    cooldown = 0.5

            cooldown -= tick

            ## Check to see if game done
            if self.map.objective == 0:
                player_win = True
                enemy_win = True
                for unit in self.units:
                    if not unit.is_enemy:
                        enemy_win = False
                    elif unit.is_enemy:
                        player_win = False
                        
            elif self.map.objective == 1:
                player_win = True
                enemy_win = True
                if turn_count >= 10:
                    player_win = True
                else:
                    for unit in self.units:
                        if not unit.is_enemy:
                            enemy_win = False
                        elif unit.is_enemy:
                            player_win = False

            elif self.map.objective == 2:
                player_win = True
                enemy_win = True
                for unit in self.units:
                    if not unit.is_enemy:
                        enemy_win = False
                    elif unit.is_boss:
                        player_win = False
            
            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit()
                    raise SystemExit
                elif e.type == KEYUP:
                    if self.state in [MOVE, IDLE, ATTACK] and keybuffer >= 0.25:
                        self.channel.stop()
                elif e.type == KEYDOWN:
                    if (keybuffer < 0.25 and turn == PLAYER_TURN and turn_wait <= 0) or self.state in [LEVELUP, BREAK]:
                        ## Keypress Up
                        if e.key == K_UP:
                            if not (player_win or enemy_win):
                                if self.state == MENU:
                                    self.channel.play(self.menu_sound)
                                    if not selected.is_enemy and not selected.end_move:
                                        menu_choice = max(0, menu_choice - 1)
                                    else:
                                        menu_choice = 3 if menu_choice == 5 else 5
                                        
                                    if menu_string[menu_choice] == 'Equip' and selected.has_used_item:
                                        if menu_choice > 0:
                                            menu_choice -= 1
                                        else:
                                            menu_choice += 1
                                            
                                    if menu_string[menu_choice] == 'Move' and selected.has_moved:
                                        if menu_choice > 0:
                                            menu_choice -= 1
                                        else:
                                            menu_choice += 1
                                        
                                elif self.state == ITEM:
                                    self.channel.play(self.menu_sound)
                                    selected.current = max(0, selected.current - 1)
                                    selected.select(self.units, reset_pos = not selected.has_moved)
                                elif self.state in [IDLE, MOVE, ATTACK]:
                                    self.channel.stop()
                                    self.channel.play(self.cursor_sound)
                                    self.cursor.y = max(0, self.cursor.y - 1)
                                
                        ## Keypress Down
                        elif e.key == K_DOWN:
                            if not (player_win or enemy_win):
                                if self.state == MENU:
                                    self.channel.play(self.menu_sound)
                                    if not selected.is_enemy and not selected.end_move:
                                        menu_choice = min(MAX_OPTION, menu_choice + 1)
                                    else:
                                        menu_choice = 3 if menu_choice == 5 else 5

                                    if menu_string[menu_choice] == 'Move' and selected.has_moved:
                                        if menu_choice < len(menu_string):
                                            menu_choice += 1
                                        else:
                                            menu_choice -= 1

                                    if menu_string[menu_choice] == 'Equip' and selected.has_used_item:
                                        if menu_choice < len(menu_string):
                                            menu_choice += 1
                                        else:
                                            menu_choice -= 1
                                            
                                elif self.state == ITEM:
                                    self.channel.play(self.menu_sound)
                                    selected.current = min(len(selected.sets)-1, selected.current + 1)
                                    selected.select(self.units, reset_pos = not selected.has_moved)
                                elif self.state in [IDLE, MOVE, ATTACK]:
                                    self.channel.stop()
                                    self.channel.play(self.cursor_sound)
                                    self.cursor.y = min(self.map.height-1, self.cursor.y + 1)

                        ## Keypress Left
                        elif e.key == K_LEFT:
                            if self.state in [IDLE, MOVE, ATTACK] and not (player_win or enemy_win):
                                self.channel.stop()
                                self.channel.play(self.cursor_sound)
                                self.cursor.x = max(0, self.cursor.x - 1)

                        ## Keypress Right
                        elif e.key == K_RIGHT:
                            if self.state in [IDLE, MOVE, ATTACK] and not (player_win or enemy_win):
                                self.channel.stop()
                                self.channel.play(self.cursor_sound)
                                self.cursor.x = min(self.map.width-1, self.cursor.x + 1)

                        elif e.key == K_a:
                            if not (player_win or enemy_win):
                                if self.state == IDLE:
                                    unit = self.units[cycle]
                                    if not unit.is_enemy and not unit.end_move:
                                        if unit != selected:
                                            self.cursor.x = unit.pos[0]
                                            self.cursor.y = unit.pos[1]
                                            selected = unit
                                            selected.clear()
                                            self.channel.play(self.select_sound)
                                            cycle += 1
                                            if cycle >= len(self.units):
                                                cycle = 0
                                            while self.units[cycle].is_enemy or self.units[cycle].end_move:
                                                cycle += 1
                                                if cycle >= len(self.units):
                                                    cycle = 0
                                    else:
                                        while self.units[cycle].is_enemy or self.units[cycle].end_move:
                                            cycle += 1
                                            if cycle >= len(self.units):
                                                cycle = 0
                                
                        elif e.key == K_z:
                            if post_fade == -2:
                                if len(self.map.post_conversations) > 0:
                                    c = self.map.post_conversations[0]
                                    if int(round(self.cursor.x)) == c.pos[0] and int(round(self.cursor.y)) == c.pos[1]:
                                        self.channel.play(self.select_sound)
                                        c.current += 1
                                        if c.current >= len(c.dialogue):
                                            self.map.post_conversations.remove(c)
                                            self.channel.stop()
                                            if len(self.map.post_conversations) > 0:
                                                conversation_target = self.map.post_conversations[0].pos
                                                dx = self.map.post_conversations[0].pos[0] - self.cursor.x
                                                dy = self.map.post_conversations[0].pos[1] - self.cursor.y
                                                d  = math.sqrt(dx*dx + dy*dy)
                                                if d > 0:
                                                    cursor_dx = dx / d
                                                    cursor_dy = dy / d
                                                    
                            elif self.state == IDLE:
                                if not (player_win or enemy_win):
                                    x = int(round(self.cursor.x))
                                    y = int(round(self.cursor.y))
                                    for unit in self.units:
                                        if x == unit.pos[0] and y == unit.pos[1]:
                                            selected = unit
                                            selected.select(self.units)
                                            self.channel.play(self.select_sound)
                                            menu_choice = 0
                                            if selected.is_enemy or selected.end_move:
                                                menu_choice = 3
                                            self.state = MENU

                            elif self.state == INTRO:
                                if len(self.map.pre_conversations) > 0:
                                    c = self.map.pre_conversations[0]
                                    if int(round(self.cursor.x)) == c.pos[0] and int(round(self.cursor.y)) == c.pos[1]:
                                        self.channel.play(self.select_sound)
                                        c.current += 1
                                        if c.current >= len(c.dialogue):
                                            self.channel.stop()
                                            self.map.pre_conversations.remove(c)
                                            if len(self.map.pre_conversations) > 0:
                                                conversation_target = self.map.pre_conversations[0].pos
                                                dx = self.map.pre_conversations[0].pos[0] - self.cursor.x
                                                dy = self.map.pre_conversations[0].pos[1] - self.cursor.y
                                                d  = math.sqrt(dx*dx + dy*dy)
                                                if d > 0:
                                                    cursor_dx = dx / d
                                                    cursor_dy = dy / d
                                                    
                            elif self.state == ITEM:
                                if not (player_win or enemy_win):
                                    self.channel.play(self.select_sound)
                                    if selected.current != selected.orig_current:
                                        selected.orig_current = selected.current
                                        selected.has_used_item = True
                                    menu_choice = 0
                                    self.state = MENU

                            elif self.state == STATS:
                                if not (player_win or enemy_win):
                                    self.channel.play(self.select_sound)
                                    self.state = MENU

                            elif self.state == LEVELUP:
                                unit_shake = 0
                                self.state = BREAK

                            elif self.state == BREAK:
                                selected.clear()
                                self.channel.play(self.select_sound)
                                selected.stop(self.units)
                                selected.end_move = True
                                selected.sets.remove(selected.sets[selected.current])
                                selected.current = 0
                                
                                attack_target = None
                                self.state = IDLE
                                        
                            elif self.state == MENU:
                                if not (player_win or enemy_win):
                                    if menu_string[menu_choice] == 'Attack':
                                        if not selected.is_enemy:
                                            selected.select(self.units, reset_pos=False)
                                            self.channel.play(self.select_sound)
                                            self.state = ATTACK
                                    
                                    elif menu_string[menu_choice] == 'Move':
                                        if not selected.has_moved and not selected.is_enemy:
                                            self.channel.play(self.select_sound)
                                            self.state = MOVE
                                            menu_choice = 0
                                            selected.select(self.units)
                                            
                                    elif menu_string[menu_choice] == 'Equip':
                                        if not selected.is_enemy and not selected.has_used_item:
                                            self.channel.play(self.select_sound)
                                            selected.orig_current = selected.current
                                            self.state = ITEM
                                        
                                    elif menu_string[menu_choice] == 'Stats':
                                        self.channel.play(self.select_sound)
                                        self.state = STATS
                                    
                                    elif menu_string[menu_choice] == 'Wait':
                                        if not selected.is_enemy:
                                            self.channel.play(self.select_sound)
                                            selected.clear()
                                            selected.stop(self.units)
                                            selected.end_move = True
                                            self.state = IDLE
                                            turn_wait = 0.25
                                    
                                    elif menu_string[menu_choice] == 'Cancel':
                                        self.channel.play(self.select_sound)
                                        if not selected.moving and not selected.end_move:
                                            if selected.has_moved and not selected.is_enemy:
                                                selected.reset(self.units)
                                                self.cursor.x = selected.pos[0]
                                                self.cursor.y = selected.pos[1]
                                                selected.refresh()
                                                selected.select(self.units)
                                            else:
                                                selected = None
                                                self.state = IDLE
                                        else:
                                            selected = None
                                            self.state = IDLE
                                
                            elif self.state == MOVE:
                                if not (player_win or enemy_win) and selected:
                                    if not selected.moving:
                                        x = int(round(self.cursor.x))
                                        y = int(round(self.cursor.y))
                                        if x != int(round(selected.pos[0])) or y != int(round(selected.pos[1])):
                                            if selected.set_target(x, y, self.units):
                                                self.channel.play(self.select_sound)
                                                dx = selected.pos[0] - self.cursor.x
                                                dy = selected.pos[1] - self.cursor.y
                                                d  = math.sqrt(dx*dx + dy*dy)
                                                if d > 0:
                                                    cursor_dx = dx / d
                                                    cursor_dy = dy / d

                            elif self.state == ATTACK:
                                if not (player_win or enemy_win):
                                    if selected:
                                        x = int(round(self.cursor.x))
                                        y = int(round(self.cursor.y))
                                        if selected.attack_enemy(x,y,self.units):
                                            self.state = DAMAGE
                                            damage_count = 0.5
                                            turn_wait = 0.25
                                        
                        elif (e.key == K_x or e.key == K_ESCAPE) and not (player_win or enemy_win):
                            if self.state == IDLE:
                                if selected:
                                    self.channel.play(self.cancel_sound)
                                    selected = None
                                    
                            elif self.state == MOVE or self.state == ATTACK:
                                if not selected.moving:
                                    self.channel.play(self.cancel_sound)
                                    self.cursor.x = selected.pos[0]
                                    self.cursor.y = selected.pos[1]
                                    if selected.has_moved or self.state == ATTACK:
                                        self.state = MENU
                                        menu_choice = 0
                                    else:
                                        selected.reset(self.units)
                                        selected = None
                                        self.state = IDLE

                            elif self.state == STATS:
                                self.channel.play(self.cancel_sound)
                                self.state = MENU

                            elif self.state == LEVELUP:
                                unit_shake = 0
                                self.state = BREAK

                            elif self.state == BREAK:
                                self.channel.play(self.cancel_sound)
                                selected.clear()
                                selected.stop(self.units)
                                selected.end_move = True
                                selected.sets.remove(selected.sets[selected.current])
                                selected.current = 0
                                
                                attack_target = None
                                self.state = IDLE
                                        
                            elif self.state == MENU:
                                self.channel.play(self.cancel_sound)
                                if not selected.moving and not selected.end_move:
                                    if selected.has_moved and not selected.is_enemy:
                                        selected.reset(self.units)
                                        self.cursor.x = selected.pos[0]
                                        self.cursor.y = selected.pos[1]
                                        selected.refresh()
                                        selected.select(self.units)
                                    else:
                                        selected = None
                                        self.state = IDLE
                                else:
                                    selected = None
                                    self.state = IDLE

                            elif self.state == ITEM:
                                self.channel.play(self.cancel_sound)
                                selected.current = selected.orig_current
                                selected.select(self.units, reset_pos = not selected.has_moved)
                                self.state = MENU

            if turn == ENEMY_TURN and scale == 1.0 and cooldown <= 0 and not enemy_win:
                e_units    = [u for u in self.units if u.is_enemy and not u.has_moved]
                
                for unit in e_units:
                    if not selected:
                        found = False
                        selected = unit
                        
                    else:
                        target_pos = unit.pos[:]
                        dx = target_pos[0] - self.cursor.x
                        dy = target_pos[1] - self.cursor.y
                        d  = math.sqrt(dx*dx + dy*dy)
                        if d > 0:
                            cursor_dx = dx / d
                            cursor_dy = dy / d
                        
                        if abs(round(self.cursor.x - target_pos[0] - cursor_dx * 0.25)) != 0 or abs(round(self.cursor.y - target_pos[1] - cursor_dy * 0.25)) != 0:
                            self.cursor.x += cursor_dx * 0.5
                            self.cursor.y += cursor_dy * 0.5
                        else:
                            self.cursor.x = target_pos[0]#int(round(self.cursor.x))
                            self.cursor.y = target_pos[1]#int(round(self.cursor.y))

                            selected.select(self.units)
                            other_units = self.units[:]
                            random.shuffle(other_units)

                            for other in other_units:
                                if other != unit and not other.is_enemy:
                                    y = int(round(other.pos[1]))
                                    x = int(round(other.pos[0]))
                                    z = unit.sets[unit.current].range + unit.base_range
                                    r_lim = selected.sets[selected.current].range+selected.base_range
                                    m_lim = selected.sets[selected.current].movement+selected.base_movement
                                    lim = m_lim + r_lim
                                    
                                    for i in range(len(self.map.map)):
                                        for j in range(len(self.map.map[i])):

                                            if not found and x == j and y == i:
                                                in_range_strict = selected.sets[selected.current].strict and selected.mmap[i][j] == r_lim
                                                in_range_loose  = not selected.sets[selected.current].strict and selected.mmap[i][j] <= r_lim
                                                
                                                if in_range_strict or in_range_loose:
                                                    selected.stop(self.units)
                                                    selected.attack_target = i, j
                                                    found = True
                                                else:
                                                    for p in range(-z,z+1):
                                                        for q in range(-z,z+1):
                                                            if abs(p)+abs(q) <= z and not found:
                                                                try:
                                                                    ir_st = selected.sets[selected.current].strict and selected.mmap[i+p][j+q] == r_lim+1
                                                                    ir_ls = not selected.sets[selected.current].strict and selected.mmap[i+p][j+q] <= lim
                                                                    if (ir_st or ir_ls) and selected.set_target(j+q,i+p,self.units):
                                                                        selected.attack_target = i, j
                                                                        found = True
                                                                except IndexError:
                                                                    pass
                                
                            if not found:
                                unit.stop(self.units)
                                unit.end_move = True
                                turn_wait = 0.25

            k = pygame.key.get_pressed()
            if self.state == SCROLL and (k[K_z] or k[K_x] or k[K_a] or k[K_SPACE] or k[K_RETURN]):
                scroll_y += 4.75
            elif self.state in [IDLE, MOVE, ATTACK] and (k[K_UP] or k[K_DOWN] or k[K_RIGHT] or k[K_LEFT]):
                keybuffer += tick * (1 + (FPS - clock.get_fps()) / FPS)
            elif cursor_dx == 0 and cursor_dy == 0:
                keybuffer = 0.0
                self.cursor.x = round(self.cursor.x)
                self.cursor.y = round(self.cursor.y)

            ## Move the cursor up
            if keybuffer >= 0.25 and cursor_dx == 0 and cursor_dy == 0 and turn == PLAYER_TURN:
                if not self.channel.get_busy():
                    self.channel.play(self.cursor_sound, -1)
                if k[K_UP]:
                    self.cursor.y = max(0, self.cursor.y - 0.25 * (1 + (FPS - clock.get_fps()) / FPS))
                elif k[K_DOWN]:
                    self.cursor.y = min(self.map.height-1, self.cursor.y + 0.25 * (1 + (FPS - clock.get_fps()) / FPS))
                else:
                    self.cursor.y = round(self.cursor.y)
                    
                if k[K_LEFT]:
                    self.cursor.x = max(0, self.cursor.x - 0.25 * (1 + (FPS - clock.get_fps()) / FPS))
                elif k[K_RIGHT]:
                    self.cursor.x = min(self.map.width-1, self.cursor.x + 0.25 * (1 + (FPS - clock.get_fps()) / FPS))
                else:
                    self.cursor.x = round(self.cursor.x)

            pygame.display.set_caption("%.2d" %(clock.get_fps()))

if __name__ == '__main__':
    main = Main()
    main.main()       
        
