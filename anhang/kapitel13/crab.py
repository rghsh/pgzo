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


class Button(GameObj):
    def __init__(self, image_normal, image_hover, pos, action):
        self.pos = pos
        self.image = image_normal
        self.image_normal = image_normal
        self.image_hover = image_hover
        self.action = action
        self.hover = False

    def on_mouse_move(self, pos):
        self.hover = self.collidepoint(mouse_state.pos)
        if self.hover:
            self.image = self.image_hover
        else:
            self.image = self.image_normal

    def on_mouse_down(self, pos, button):
        if button == mouse.LEFT and self.hover:
            self.action()


class Start(Stage):

    def __init__(self):
        self.background_image = "start"
        self.reset()

    def reset(self):
        self.leave_all()
        self.start_button = Button(
            "start_button_normal",
            "start_button_hover",
            (WIDTH * 0.5, HEIGHT * 0.5),
            self.start_game)
        self.quit_button = Button(
            "quit_button_normal",
            "quit_button_hover",
            (WIDTH * 0.1, HEIGHT * 0.9),
            sys.exit)
        self.start_button.appear_on_stage(self)
        self.quit_button.appear_on_stage(self)

    def draw(self):
        screen.draw.text(
            "The Crab Game",
            center=(WIDTH // 2, HEIGHT * 0.25),
            color="brown",
            fontsize=60,
            fontname="zachary")

    def on_key_up(self, key):
        if key == keys.SPACE:
            self.start_game()

    def start_game(self):
        beach_stage.reset_game()
        beach_stage.show()


class Beach(Stage):
    def __init__(self):
        self.background_image = "sand"

    def reset_game(self):
        self._level = 1
        self._score = 0
        self.prepare_beach()

    def prepare_beach(self):
        self._defeated = False
        self._victorious = False

        self.leave_all()

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
            if not c.shielded and c.overlaps(lobster):
                c.leave_stage()
                sounds.au.play()
                # There is only one crab on the beach, so we set
                # _defeated=True if we found at least one overlapping crab:
                self._defeated = True
                self.schedule_gameover()

    def restart(self):
        if self._victorious:
            self._level += 1
            self.prepare_beach()
        elif self._defeated:
            start_stage.reset()
            start_stage.show()
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
        self._set_image_index(0)
        self.pos = pos
        self.speed = 0
        self.traveled = 0
        self.shielded = False
        self.shield_energy = 10

    def _set_image_index(self, image_index):
        self.image_index = image_index
        self.image = Crab.IMAGE_PREFIX + str(image_index)

    def draw(self):
        if self.shielded:
            shield = Actor("shield", self.pos)
            shield.draw()

        energy_block = Actor("energy_block")
        x = WIDTH - 20
        y = 20
        for dummy in range(self.shield_energy):
            energy_block.topright = (x, y)
            energy_block.draw()
            x -= 10

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
        if keyboard.space and not self.shielded and self.shield_energy > 0:
            self.shielded = True
            self.shield_energy -= 1
            clock.schedule_unique(self.unshield, 3)

    def unshield(self):
        self.shielded = False

    def switch_image(self):
        if self.traveled > Crab.TRAVEL_DISTANCE_BETWEEN_IMAGE_FLIPS:
            self._set_image_index((self.image_index + 1) % Crab.IMAGE_COUNT)
            self.traveled -= Crab.TRAVEL_DISTANCE_BETWEEN_IMAGE_FLIPS


class Lobster(GameObj):

    IMAGE_PREFIX = "lobster"
    IMAGE_COUNT = 2
    TRAVEL_DISTANCE_BETWEEN_IMAGE_FLIPS = 7

    def __init__(self, pos, speed, drunkenness, jumpiness):
        self._set_image_index(0)
        self.pos = pos
        self.speed = speed
        self.traveled = 0
        self.drunkenness = drunkenness
        self.jumpiness = jumpiness

    def _set_image_index(self, image_index):
        self.image_index = image_index
        self.image = Lobster.IMAGE_PREFIX + str(image_index)

    def act(self):
        self.switch_image()
        if self.can_move(self.speed):
            self.move(self.speed)
            self.traveled += abs(self.speed)
        else:
            self.turn(25)
        if random.randrange(10) < self.drunkenness:
            self.turn(random.uniform(-self.jumpiness, self.jumpiness))
        self.stage.take_out_neighbouring_crab(self)

    def switch_image(self):
        if self.traveled > Lobster.TRAVEL_DISTANCE_BETWEEN_IMAGE_FLIPS:
            self._set_image_index((self.image_index + 1) % Lobster.IMAGE_COUNT)
            self.traveled -= Lobster.TRAVEL_DISTANCE_BETWEEN_IMAGE_FLIPS


class Worm(GameObj):

    IMAGE_PREFIX = "worm"
    IMAGE_COUNT = 2
    TRAVEL_DISTANCE_BETWEEN_IMAGE_FLIPS = 3

    def __init__(self, pos):
        self._set_image_index(0)
        self.pos = pos
        self.speed = 0.5
        if random.randrange(2) == 0:
            self.speed = -self.speed
        self.traveled = 0

    def _set_image_index(self, image_index):
        self.image_index = image_index
        self.image = Worm.IMAGE_PREFIX + str(image_index)

    def act(self):
        self.switch_image()
        if self.can_move(self.speed):
            self.move(self.speed)
            self.traveled += abs(self.speed)
        else:
            self.speed = -self.speed
        if random.randrange(100) < 10:
            self.speed += random.uniform(-1, 1) / 50

    def switch_image(self):
        if self.traveled > Worm.TRAVEL_DISTANCE_BETWEEN_IMAGE_FLIPS:
            self._set_image_index((self.image_index + 1) % Worm.IMAGE_COUNT)
            self.traveled -= Worm.TRAVEL_DISTANCE_BETWEEN_IMAGE_FLIPS


start_stage = Start()
beach_stage = Beach()
start_stage.show()


pgzrun.go()
