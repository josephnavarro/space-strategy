import pygame
from constant import *
from moveset import Set

class Unit(object):
    def __init__(self, x, y, num, color, gray, _map, enemy=False, boss=False):
        self.pos      = [x, y]
        self.orig_pos = [x, y]
        self.num = num
        self.new_map(_map)
        self.modifier = [0,0,0,0,0]

        self.counter = 0
        self.experience = 0
        self.display_experience = 0
        self.directions = None
        self.moving = False
        self.has_moved = False
        self.end_move = False
        self.shake = False
        self.damage_buf = 0
        self.attack_target = None
        self.disappear = 0
        self.is_enemy = enemy
        self.is_boss = boss
        
        self.load_data(num, color, gray, enemy)

        self.alpha = 160
        self.alpha_mod = -2
        self.move_sound = pygame.mixer.Sound('res/snd/000.ogg')
        self.move_sound.set_volume(0.5)

        ## Blittable blue surface to show move range
        self.movebox = pygame.Surface((TILE_WIDTH,TILE_HEIGHT)).convert()
        self.movebox.fill((255,0,255))
        self.movebox.set_colorkey((255,0,255))
        pygame.draw.rect(self.movebox, (48,48,160), (TILE_WIDTH/8,TILE_HEIGHT/8,TILE_WIDTH*3/4,TILE_HEIGHT*3/4))
        self.movebox.set_alpha(160)

        ## Blittable blue surface to show hit range
        self.hitbox = pygame.Surface((TILE_WIDTH,TILE_HEIGHT)).convert()
        self.hitbox.fill((255,0,255))
        self.hitbox.set_colorkey((255,0,255))
        pygame.draw.rect(self.hitbox, (160,48,48), (TILE_WIDTH/8,TILE_HEIGHT/8,TILE_WIDTH*3/4,TILE_HEIGHT*3/4))
        self.hitbox.set_alpha(160)

    def refresh(self, item=False):
        self.has_moved = False
        self.end_move = False
        if item:
            self.has_used_item = False
        self.clear()
        
    def clear(self):
        self.base_movement = self.base_orig_movement
        self.base_range = self.base_orig_range
        self.sets[self.current].movement = self.sets[self.current].orig_movement
        self.sets[self.current].range = self.sets[self.current].orig_range
        self.attack_target = None
        self.new_mmap()
        self.new_dmap()

    def new_map(self, _map):
        self._map = _map
        self.new_dmap()
        self.new_mmap()

    def new_dmap(self):
        self.dmap = []
        for i in xrange(self._map.height):
            array = []
            for j in xrange(self._map.width):
                array.append(999)
            self.dmap.append(array)

    def new_mmap(self):
        self.mmap = []
        for i in xrange(self._map.height):
            array = []
            for j in xrange(self._map.width):
                array.append(999)
            self.mmap.append(array)

    def load_data(self, num, color, gray, enemy):
        self.level = 1
        self.hp = 1
        self.max_hp = 1
        self.base_attack = 0
        self.base_defense = 0
        self.base_speed = 0
        self.base_range = 0
        self.base_orig_range = 0
        self.base_movement = 0
        self.base_orig_movement = 0
        self.display_hp = 1
        self.name = ''
        
        self.sets = []
        self.current = 0
        self.orig_current = 0
        self.has_used_item = False
        process_set = False
        name = 'None'
        attack = 0
        defense = 0
        speed = 0
        mind = 0
        _range = 0
        movement = 0
        uses = 3
        images = None
        strict = False

        if enemy:
            filename = 'res/mon/%03d.mon' %num
        else:
            filename = 'res/data/%03d.char' %num
        
        with open(filename, 'r') as f:
            data = f.readlines()
            for line in data:
                line = line.lstrip().rstrip()
                params = line.split(' ')
                if line.startswith('.level'):
                    self.level = int(params[1])
                elif line.startswith('.name'):
                    self.name = params[1]
                elif line.startswith('.hp'):
                    ## Set the hit points
                    self.hp = int(params[1])
                    self.max_hp = self.hp
                    self.display_hp = self.hp
                elif line.startswith('.set'):
                    process_set = True
                    name = params[1]
                elif process_set:
                    if line.startswith('.atk'):
                        ## Set the set attack
                        attack = int(params[1])
                    elif line.startswith('.def'):
                        ## Set the set defense
                        defense = int(params[1])
                    elif line.startswith('.spd'):
                        ## Set the set speed
                        speed = int(params[1])
                    elif line.startswith('.mind'):
                        ## Set the set mind
                        mind = int(params[1])
                    elif line.startswith('.move'):
                        ## Set the set move distance
                        movement = int(params[1])
                    elif line.startswith('.range'):
                        ## Set the hit range
                        _range = int(params[1])
                        if len(params) >= 3:
                            strict = bool(int(params[2]))
                    elif line.startswith('.uses'):
                        ## Set the uses
                        uses = int(params[1])
                    elif line.startswith('.image'):
                        ## Set the character image
                        offset = int(params[1])*48, int(params[2])*24
                        sub1 = color.subsurface(offset[0], offset[1],    24, 24)
                        sub2 = color.subsurface(offset[0]+24, offset[1], 24, 24)
                        sub3 = gray.subsurface(offset[0], offset[1],    24, 24)
                        sub4 = gray.subsurface(offset[0]+24, offset[1], 24, 24)
                        images = [[sub1, sub2], [sub3, sub4]]
                    elif line.startswith('.end'):
                        process_set = False
                        temp_set = Set(name, attack, defense, speed, mind, _range, movement, strict, uses, images)
                        self.sets.append(temp_set)
                else:
                    if line.startswith('.atk'):
                        ## Set the base attack
                        self.base_attack = int(params[1])
                    elif line.startswith('.def'):
                        ## Set the base defense
                        self.base_defense = int(params[1])
                    elif line.startswith('.spd'):
                        ## Set the base speed
                        self.base_speed = int(params[1])
                    elif line.startswith('.mind'):
                        ## Set the set mind
                        self.base_mind = int(params[1])
                    elif line.startswith('.move'):
                        ## Set the set move distance
                        self.base_movement = int(params[1])+1
                        self.base_orig_movement = int(params[1])+1
                    elif line.startswith('.range'):
                        ## Set the hit range
                        self.base_range = int(params[1])
                        self.base_orig_range = int(params[1])

        self.anim = 0

    def render_move(self, units, surface):
        ## Draw the player to the target surface, along with move grid

        enemy_pos = []
        for unit in units:
            if unit.is_enemy != self.is_enemy:
                enemy_pos.append((int(round(unit.pos[1])), int(round(unit.pos[0]))))
        
        self.hitbox.set_alpha(self.alpha)
        self.movebox.set_alpha(self.alpha)
        self.alpha += self.alpha_mod
        if self.alpha <= 80 or self.alpha >= 160:
            self.alpha_mod *= -1

        lim = self.sets[self.current].movement+self.sets[self.current].range+self.base_movement+self.base_range
        m_lim = self.sets[self.current].movement+self.base_movement
        
        for i in xrange(len(self.mmap)):
            for j in xrange(len(self.mmap[i])):
                ir_st = self.sets[self.current].strict and self.mmap[i][j] == lim-1
                ir_ls = not self.sets[self.current].strict and self.mmap[i][j] < lim

                r_st  = self.sets[self.current].strict and self.mmap[i][j] == lim-1
                r_ls  = not self.sets[self.current].strict and m_lim <= self.mmap[i][j] <= lim
                
                if ((i,j) in enemy_pos and (ir_st or ir_ls)) or (r_st or r_ls):
                    surface.blit(self.hitbox, (int(j*TILE_WIDTH), int(i*TILE_HEIGHT)))
                elif self.mmap[i][j] < m_lim:
                    surface.blit(self.movebox, (int(j*TILE_WIDTH), int(i*TILE_HEIGHT)))
        
    def render(self, surface):
        if self.sets[self.current].images:
            if self.shake:
                x = random.choice((-3,-2,-1,1,2,3))
            else:
                x = 0

            i = 0 if not self.end_move else 1
                
            self.anim += 0.1
            surface.blit(self.sets[self.current].images[i][int(self.anim)%2], (int(self.pos[0]*TILE_WIDTH)+x, int(self.pos[1]*TILE_HEIGHT)))

    def reset(self, units):
        self.pos = self.orig_pos
        self.base_movement = self.base_orig_movement
        self.base_range = self.base_orig_range
        self.sets[self.current].movement = self.sets[self.current].orig_movement
        self.sets[self.current].range = self.sets[self.current].orig_range
        self.has_moved = False
        self.moving = False
        self.select(units)

    ## Select the unit and populate its movement grid for displaying onscreen
    def select(self, units, reset_pos=True, talk=False):
        self.new_mmap()

        if talk:
            self.base_movement = 1
            self.base_range = 1
            self.sets[self.current].movement = 0
            self.sets[self.current].range = 0
            
        elif reset_pos:
            ## If we want to reset the player's position due to a cancel
            self.orig_pos = [int(round(self.pos[0])), int(round(self.pos[1]))]
            self.base_movement = self.base_orig_movement
            self.base_range = self.base_orig_range
            self.sets[self.current].range = self.sets[self.current].orig_range
            self.sets[self.current].movement = self.sets[self.current].orig_movement
        else:
            ## If we have just moved, don't move anymore
            self.base_movement = 1
            self.sets[self.current].movement = 0

        ## Set the target cell to be the player's current position
        self.mmap[int(round(self.pos[1]))][int(round(self.pos[0]))] = 0
        changed = True

        enemy_pos = []
        for unit in units:
            if unit.is_enemy != self.is_enemy:
                enemy_pos.append((int(round(unit.pos[1])), int(round(unit.pos[0]))))        

        lim = self.sets[self.current].movement+self.sets[self.current].range+self.base_movement+self.base_range
        m_lim = self.sets[self.current].movement+self.base_movement
        
        while changed:
            changed = False
            ## Do a Dijkstra map transformation
            for i in xrange(len(self.mmap)):
                for j in xrange(len(self.mmap[i])):
                    
                    ## If the tile is not a wall, mutate its surrounding cells
                    if self._map.get_passable(j,i):
                        if self.mmap[i][j]+1 < lim:

                            cost = 1
                            if (i,j) in enemy_pos and self.mmap[i][j] < m_lim:
                                cost = m_lim - self.mmap[i][j] + 2
                            
                            ## Choose all orthogonally adjacent cells
                            for c in ORTHOGONAL:
                                try:
                                    if self._map.get_passable(j+c[0],i+c[1]) and self.mmap[i+c[1]][j+c[0]] - self.mmap[i][j] >= cost+1:
                                        self.mmap[i+c[1]][j+c[0]] = self.mmap[i][j]+cost
                                        changed = True
                                except IndexError:
                                    pass

    def attack_enemy(self, a, b, units):
        self_pos = int(round(self.pos[1])), int(round(self.pos[0]))
        r_lim = self.sets[self.current].range+self.base_range
        s_lim = self.sets[self.current].speed+self.base_speed
        a_lim = self.sets[self.current].attack+self.base_attack
        in_range_strict = self.sets[self.current].strict and self.mmap[b][a] == r_lim
        in_range_loose  = not self.sets[self.current].strict and self.mmap[b][a] <= r_lim + 1
        
        if in_range_strict or in_range_loose:
            for unit in units:
                pos = int(round(unit.pos[1])), int(round(unit.pos[0]))
                if (b,a) == pos and pos != self_pos and unit.is_enemy != self.is_enemy:
                    s_lim_u = unit.sets[unit.current].speed+unit.base_speed
                    d_lim_u = unit.sets[unit.current].defense+unit.base_defense
                    
                    ds = max(0, s_lim - s_lim_u + 1)
                    unit.damage_buf = int(max(0, max(1, (random.randint(-1,ds) + a_lim + self.modifier[1] - d_lim_u - unit.modifier[2]))))
                    gain = int(20 * unit.level / (float(self.level) + 1))
                    if unit.hp <= unit.damage_buf:
                        gain *= 2
                    self.experience += gain

                    if self.sets[self.current].uses > 0:
                        self.sets[self.current].uses -= 1
                    return True
        return False
    
    def set_target(self, a, b, units):
        self.new_dmap()
        m_lim = self.sets[self.current].movement+self.base_movement
        lim = self.sets[self.current].movement+self.sets[self.current].range+self.base_movement+self.base_range
        limit = self.mmap[b][a] < m_lim if not self.is_enemy else self.mmap[b][a] < lim
        unit_pos = [(int(round(unit.pos[1])), int(round(unit.pos[0]))) for unit in units]

        enemy_pos = []
        for unit in units:
            if unit.is_enemy != self.is_enemy:
                enemy_pos.append((int(round(unit.pos[1])), int(round(unit.pos[0]))))        
        
        if limit and self._map.get_passable(a,b) and (b,a) not in unit_pos:
            self.dmap[b][a] = 0
            changed = True

            while changed:
                changed = False
                for i in xrange(len(self.dmap)):
                    for j in xrange(len(self.dmap[i])):
                        if self._map.get_passable(j,i) and (i,j) not in enemy_pos and self.mmap[i][j]+1 < lim:

                            ## Choose all orthogonally adjacent cells
                            for c in ORTHOGONAL:
                                try:
                                    if self._map.get_passable(j+c[0],i+c[1]) and (i+c[1],j+c[0]) not in enemy_pos and\
                                       self.dmap[i+c[1]][j+c[0]] - self.dmap[i][j] >= 2:
                                        self.dmap[i+c[1]][j+c[0]] = self.dmap[i][j]+1
                                        changed = True
                                except IndexError:
                                    pass

            self.directions = [(self.dmap[int(round(self.pos[1])+1)][int(round(self.pos[0]))], (1,0)),
                               (self.dmap[int(round(self.pos[1])-1)][int(round(self.pos[0]))],(-1,0)),
                               (self.dmap[int(round(self.pos[1]))][int(round(self.pos[0])+1)], (0,1)),
                               (self.dmap[int(round(self.pos[1]))][int(round(self.pos[0])-1)],(0,-1))]

            self.moving = True
            return True
        return False

    def stop(self, units):
        self.select(units, reset_pos=False)
        self.new_dmap()
        self.moving = False
        self.has_moved = True
        self.pos = [int(round(self.pos[0])), int(round(self.pos[1]))]
        self.directions = None
        self.counter = 0
                            
    def move(self, units):
        if self.directions:
            d = min(self.directions, key=lambda x:x[0])

            short_move = False
            i = int(round(self.pos[1]))
            j = int(round(self.pos[0]))
            
            
            if d[0] < 999 and int(self.counter) < 1:
                if d[1][0] > 0:
                    self.pos[1] += 0.125 * (1 + (FPS - clock.get_fps()) / FPS)
                    self.counter += 0.125 * (1 + (FPS - clock.get_fps()) / FPS)
                    
                elif d[1][0] < 0:
                    self.pos[1] -= 0.125 * (1 + (FPS - clock.get_fps()) / FPS)
                    self.counter += 0.125 * (1 + (FPS - clock.get_fps()) / FPS)

                elif d[1][1] > 0:
                    self.pos[0] += 0.125 * (1 + (FPS - clock.get_fps()) / FPS)
                    self.counter += 0.125 * (1 + (FPS - clock.get_fps()) / FPS)
                    
                elif d[1][1] < 0:
                    self.pos[0] -= 0.125 * (1 + (FPS - clock.get_fps()) / FPS)
                    self.counter += 0.125 * (1 + (FPS - clock.get_fps()) / FPS)
            else:
                if int(self.counter) >= 1:
                    self.move_sound.play()
                    self.counter = 0
                    self.pos = [j,i]
                    self.directions = [(self.dmap[int(round(self.pos[1])+1)][int(round(self.pos[0]))], (1,0)),
                                       (self.dmap[int(round(self.pos[1])-1)][int(round(self.pos[0]))],(-1,0)),
                                       (self.dmap[int(round(self.pos[1]))][int(round(self.pos[0])+1)], (0,1)),
                                       (self.dmap[int(round(self.pos[1]))][int(round(self.pos[0])-1)],(0,-1))]
                elif d[0] == 999:
                    short_move = True
            
            full_move = (self.dmap[i][j] == 0) and self.counter == 0
            m_lim = self.sets[self.current].movement+self.base_movement
            lim = self.sets[self.current].movement+self.sets[self.current].range+self.base_movement+self.base_range
            if m_lim <= self.mmap[i][j]+1 <= lim:
                short_move = True
            
            if full_move or short_move or len(self.directions) == 0:
                self.stop(units)
                return True

        return False
        
