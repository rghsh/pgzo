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


crab1 = Crab((WIDTH / 2, HEIGHT / 2), 5, 7, 15)
crab1.appear_on_stage(beach)
crab2 = Crab((WIDTH * 0.75, HEIGHT * 0.15), 1, 1, 25)
crab2.appear_on_stage(beach)


def update():
    crab1.act()
    crab2.act()


pgzrun.go()
