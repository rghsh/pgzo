import random
import pgzrun
from pgzo import *

WIDTH = 560     # screen width
HEIGHT = 460    # screen height
TITLE = "Crab"  # window title

# "Schaltzentrale" für die Schwierigkeit des Spiels:
START_WITH_LOBSTERS = 0
START_LOBSTER_STRENGTH = 0.2
START_WITH_WORMS = 20


class Beach(Stage):
    def __init__(self):
        self._defeated = False
        self._victorious = False
        self._score = 0
        if not hasattr(self, "_level"):
            self._level = 1
        self.background_image = "sand"

        crab = Crab((WIDTH / 2, HEIGHT * 0.7))
        crab.appear_on_stage(self)

        for dummy in range(START_WITH_WORMS):
            w = Beach._create_random_worm()
            w.appear_on_stage(self)

        num_lobsters = START_WITH_LOBSTERS + self._level - 1
        for dummy in range(num_lobsters):
            lobster = Beach._create_random_lobster(START_LOBSTER_STRENGTH)
            lobster.appear_on_stage(self)

    def take_out_neighbouring_worms(self, crab):
        for w in self.get_game_objects(Worm):
            if w.overlaps(crab):
                w.leave_stage()
                sounds.blop.play()
                self._score += 1
        if not self._victorious and self.count_game_objects(Worm) == 0:
            self._victorious = True
            self.leave_all(Lobster)
            self.schedule_gameover()

    def take_out_neighbouring_crab(self, lobster):
        for c in self.get_game_objects(Crab):
            if c.overlaps(lobster):
                c.leave_stage()
                sounds.au.play()
                # There is only one crab on the beach, so we set
                # _defeated=True if we found at least one overlapping crab:
                self._defeated = True
                self.schedule_gameover()

    def restart(self):
        if self._victorious:
            self.leave_all()
            self._level += 1
            self.__init__()
        elif self._defeated:
            sys.exit()
        else:
            raise Exception("restart on unfinished game detected!")

    def schedule_gameover(self):
        clock.schedule_unique(self.restart, 4.0)

    @staticmethod
    def _create_random_lobster(strength):
        result = Lobster(
            (random.randrange(WIDTH), random.randrange(HEIGHT * 0.4)),
            1 + strength * 4,
            1 + strength * 9,
            1 + strength * 24)
        result.turn(random.randrange(360))
        return result

    @staticmethod
    def _create_random_worm():
        return Worm((random.randrange(WIDTH), random.randrange(HEIGHT)))

    def draw(self):
        screen.draw.text("Score: " + str(self._score), topleft=(10, 10),
                         color="black", fontsize=20, fontname="zachary")
        screen.draw.text("Level: " + str(self._level), topleft=(10, 35),
                         color="black", fontsize=20, fontname="zachary")
        if self._defeated:
            screen.draw.text(
                "You lose!",
                center=(WIDTH // 2, HEIGHT * 0.25),
                color="brown",
                fontsize=60,
                fontname="zachary")
        if self._victorious:
            screen.draw.text(
                "You win!",
                center=(WIDTH // 2, HEIGHT * 0.25),
                color="brown",
                fontsize=60,
                fontname="zachary")


class Crab(GameObj):

    IMAGE_PREFIX = "crab"
    IMAGE_COUNT = 6
    TRAVEL_DISTANCE_BETWEEN_IMAGE_FLIPS = 5

    def __init__(self, pos):
        self.image_index = 0    # initialize image by index via setter property
        self.pos = pos
        self.speed = 0
        self.traveled = 0

    @property
    def image_index(self):
        return self._image_index

    @image_index.setter
    def image_index(self, image_index):
        self._image_index = image_index
        self.image = Crab.IMAGE_PREFIX + str(image_index)

    def act(self):
        self.switch_image()
        if self.can_move(self.speed):
            self.move(self.speed)
            self.traveled += abs(self.speed)
        else:
            self.speed = 0
        self.stage.take_out_neighbouring_worms(self)
        if keyboard.left:
            self.turn(10)
        if keyboard.right:
            self.turn(-10)
        if keyboard.up:
            self.speed_up()
        if keyboard.down:
            self.slow_down()

    def switch_image(self):
        if self.traveled > Crab.TRAVEL_DISTANCE_BETWEEN_IMAGE_FLIPS:
            # The following line effectively induces an image flip via the
            # above setter property:
            self.image_index = (self.image_index + 1) % Crab.IMAGE_COUNT
            self.traveled -= Crab.TRAVEL_DISTANCE_BETWEEN_IMAGE_FLIPS


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
        self.stage.take_out_neighbouring_crab(self)


class Worm(GameObj):
    def __init__(self, pos):
        self.image = "worm"
        self.pos = pos

    def act(self):
        new_pos = (self.pos[0] + random.uniform(-0.5, 0.5),
                   self.pos[1] + random.uniform(-0.5, 0.5))
        if not self.stage.is_beyond_edge(new_pos):
            self.pos = new_pos


beach = Beach()
beach.show()


pgzrun.go()
