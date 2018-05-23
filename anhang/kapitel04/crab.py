import pgzrun
from pgzo import *

# screen size in pixels:
WIDTH = 560
HEIGHT = 460

# window title
TITLE = "Crab"

beach = Stage()
beach.background_image = "sand"
beach.show()

pgzrun.go()
