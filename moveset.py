class Set(object):
    def __init__(self, name, attack, defense, speed, mind, _range, movement, strict, uses, images):
        self.name = name
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.mind = mind
        self.range = _range
        self.movement = movement
        self.orig_range = _range
        self.orig_movement = movement
        self.images = images

        self.strict = strict
        self.uses = uses
