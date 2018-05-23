import pgzrun

from pgzo import *

WIDTH = 300
HEIGHT = 300

sun = GameObj(
    "sun", (WIDTH / 2, HEIGHT / 2), pos_drawing_color="red")
earth = GameObj(
    "earth", (WIDTH * 0.8, HEIGHT / 2),
    pos_drawing_color="red", orbit_center=sun)
mars = GameObj(
    "mars", (WIDTH / 2, HEIGHT * 0.9),
    pos_drawing_color="red", orbit_center=sun)


def draw():
    screen.fill("darkblue")
    sun.draw()
    earth.draw()
    mars.draw()


def update():
    earth.orbit(1)
    mars.orbit(0.53)
    print("Earth orbits:", earth.full_orbits())
    print("Mars orbits:", mars.full_orbits())


pgzrun.go()
