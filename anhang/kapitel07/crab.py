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
    def __init__(self, pos, speed, drunkenness, jumpiness):
        self.image = "crab"
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
        for worm in self.stage.get_game_objects(Worm):
            if worm.overlaps(self):
                worm.leave_stage()
                sounds.blop.play()


class Worm(GameObj):
    def __init__(self, pos):
        self.image = "worm"
        self.pos = pos

    def act(self):
        new_pos = (self.pos[0] + random.uniform(-0.5, 0.5),
                   self.pos[1] + random.uniform(-0.5, 0.5))
        if not self.stage.is_beyond_edge(new_pos):
            self.pos = new_pos


def create_random_crab():
    return Crab((random.randrange(WIDTH), random.randrange(HEIGHT)),
                random.uniform(1, 5),
                random.uniform(1, 10),
                random.uniform(1, 25))


def create_random_worm():
    return Worm((random.randrange(WIDTH), random.randrange(HEIGHT)))


for dummy in range(20):
    w = create_random_worm()
    w.appear_on_stage(beach)
c = Crab((WIDTH / 2, HEIGHT / 2), 5, 7, 15)
c.appear_on_stage(beach)


def update():
    for o in beach.get_game_objects():
        o.act()


pgzrun.go()
