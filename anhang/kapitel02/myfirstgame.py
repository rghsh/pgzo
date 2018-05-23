import pgzrun

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

    if food.colliderect(me):
        sounds.burp.play()


pgzrun.go()
