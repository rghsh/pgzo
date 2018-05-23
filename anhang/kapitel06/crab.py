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


def create_random_crab():
    return Crab((random.randrange(WIDTH), random.randrange(HEIGHT)),
                random.uniform(1, 5),
                random.uniform(1, 10),
                random.uniform(1, 25))


all_crabs = []
for dummy in range(20):
    c = create_random_crab()
    all_crabs.append(c)

for c in all_crabs:
    c.appear_on_stage(beach)


def update():
    for c in all_crabs:
        c.act()


pgzrun.go()
