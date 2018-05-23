import pgzrun
import pygame


def overlaps(self, other):
    if self.colliderect(other):
        ox = round(self.topleft[0] - other.topleft[0])
        oy = round(self.topleft[1] - other.topleft[1])
        offset = (ox, oy)
        my_mask = pygame.mask.from_surface(self._surf)
        other_mask = pygame.mask.from_surface(other._surf)
        if other_mask.overlap(my_mask, offset) is not None:
            return True
    return False


Actor.overlaps = overlaps

WIDTH = 400
HEIGHT = 300

me = Actor("mouth", midbottom=(WIDTH // 2, HEIGHT))
food = Actor("pizza")


def draw():
    screen.fill("blue")
    me.draw()
    food.draw()


def update():
    food.y = food.y + 3

    if keyboard.left:
        food.x = food.x - 5

    if keyboard.right:
        food.x = food.x + 5

    if food.overlaps(me):
        sounds.burp.play()


pgzrun.go()
