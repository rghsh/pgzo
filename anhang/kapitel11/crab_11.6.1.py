import random
import pgzrun
from pgzo import *

WIDTH = 560     # screen width
HEIGHT = 460    # screen height
TITLE = "Crab"  # window title

# "Schaltzentrale" für die Schwierigkeit des Spiels:
START_WITH_LOBSTERS = 1
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


def animate(gobj, get_image_name_func, image_count,
            travel_distance_between_image_flips):
    cls = type(gobj)
    if not hasattr(cls, "move") or not callable(cls.move):
        raise Exception("first parameter's type must provide 'move' method")

    # first prepare the class, if not done already
    # overwrite cls's 'move' method with a new one thereby
    # renaming the existing method to 'old_move'.
    # First check, if we have overwritten already in the past:
    if not hasattr(cls, "old_move"):
        # Not overwritten yet.
        # Let's first rename the current move method:
        cls.old_move = cls.move
        # define a new method:

        def new_move(self, distance):
            self.old_move(distance)  # call old move method
            # now after moving we perform image flip if needed:
            self.traveled += abs(distance)
            if self.traveled > travel_distance_between_image_flips:
                self._set_image_index((self.image_index + 1) % image_count)
                self.traveled -= travel_distance_between_image_flips
        # overwrite with the new method
        cls.move = new_move

        # add an additional helper method:
        def _set_image_index(self, image_index):
            self.image_index = image_index
            self.image = get_image_name_func(image_index)
        cls._set_image_index = _set_image_index

    gobj.traveled = 0
    gobj._set_image_index(0)


class Crab(GameObj):
    def __init__(self, pos):
        animate(self, lambda i: "crab" + str(i), 6, 5)
        self.pos = pos
        self.speed = 0

    def act(self):
        if self.can_move(self.speed):
            self.move(self.speed)
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


class Lobster(GameObj):
    def __init__(self, pos, speed, drunkenness, jumpiness):
        animate(self, lambda i: "lobster" + str(i), 2, 7)
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
