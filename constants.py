"""Constants"""

from math import cos, pi

# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
SCREEN_HALF_WIDTH = SCREEN_WIDTH // 2
SCREEN_HALF_HEIGHT = SCREEN_HEIGHT // 2
SCREEN_TOP_MARGIN = 80
SCREEN_BOTTOM_MARGIN = 80
SCREEN_LEFT_MARGIN = 150
SCREEN_RIGHT_MARGIN = 150

# Color
SIDE_COLORS = [
    (255, 0, 0),  # RED
    (0, 255, 0),  # GREEN
    (0, 0, 255),  # BLUE
    (255, 255, 0),  # YELLOW
    (255, 0, 255),  # PINK
    (0, 255, 255),  # CYAN
    (255, 165, 0),  # ORANGE
    (140, 52, 235)  # PURPLE
]

# Math
COS_60 = cos(60 * pi / 180)
