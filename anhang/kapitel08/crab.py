import random
import pgzrun
from pgzo import *

WIDTH = 560
HEIGHT = 460
TITLE = "Crab"

beach = Stage()
beach.background_image = "sand"
beach.show()


class Crab(GameObj):
    def __init__(self, pos):
        self.image = "crab"
        self.pos = pos
        self.speed = 0   # Start at speed 0

    def act(self):
        if self.can_move(self.speed):
            self.move(self.speed)
        else:
            self.speed = 0
        for worm in self.stage.get_game_objects(Worm):
            if worm.overlaps(self):
                worm.leave_stage()
                sounds.blop.play()
        if keyboard.left:
            self.turn(10)
        if keyboard.right:
            self.turn(-10)
        if keyboard.up:
            self.speed_up()
        if keyboard.down:
            self.slow_down()


class Lobster(GameObj):
    def __init__(self, pos, speed, drunkenness, jumpiness):
        self.image = "lobster"
        self.pos = pos
        self.speed = speed
        self.drunkenness = drunkenness
        self.jumpiness = jumpiness

    def act(self):
        if self.can_move(self.speed):
            self.move(self.speed)
        else:
            self.turn(25)
        if random.randrange(10) < self.drunkenness:
            self.turn(random.uniform(-self.jumpiness, self.jumpiness))
        for crab in self.stage.get_game_objects(Crab):
            if crab.overlaps(self):
                crab.leave_stage()
                sounds.au.play()


class Worm(GameObj):
    def __init__(self, pos):
        self.image = "worm"
        self.pos = pos

    def act(self):
        new_pos = (self.pos[0] + random.uniform(-0.5, 0.5),
                   self.pos[1] + random.uniform(-0.5, 0.5))
        if not self.stage.is_beyond_edge(new_pos):
            self.pos = new_pos


def create_random_lobster(strength):
    result = Lobster((random.randrange(WIDTH), random.randrange(HEIGHT * 0.4)),
                     1 + strength * 4,
                     1 + strength * 9,
                     1 + strength * 24)
    result.turn(random.randrange(360))
    return result


def create_random_worm():
    return Worm((random.randrange(WIDTH), random.randrange(HEIGHT)))


crab = Crab((WIDTH / 2, HEIGHT * 0.7))
crab.appear_on_stage(beach)

for dummy in range(20):
    w = create_random_worm()
    w.appear_on_stage(beach)

for dummy in range(2):
    lobster = create_random_lobster(0.2)
    lobster.appear_on_stage(beach)


def update():
    for o in beach.get_game_objects():
        o.act()


pgzrun.go()
