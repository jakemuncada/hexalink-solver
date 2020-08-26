"""A Hexagon Slitherlink Game"""

import os

import pygame
import helpers
from point import Point
from hexgame import HexGame
from sidestatus import SideStatus

# Initialize window location
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (20, 50)

# Initialize pygame
pygame.init()

# Screen
WIDTH = 1280
HEIGHT = 960
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
CELL_SIDE_WIDTH = 20
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slitherlink")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
DARKER_GRAY = (35, 35, 35)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 0, 255)


def render(game):
    """Draws the game board."""
    win.fill(BLACK)

    for rowArr in game.board:
        for cell in rowArr:
            pygame.draw.circle(win, WHITE, cell.center.get(), 2)

    for side in game.sides:
        if side.status == SideStatus.UNSET:
            isDashed = True
            lineWidth = 4
            color = GRAY
        elif side.status == SideStatus.ACTIVE:
            isDashed = False
            lineWidth = 6
            color = BLUE
        elif side.status == SideStatus.BLANK:
            isDashed = True
            lineWidth = 4
            color = DARKER_GRAY

        ep1 = side.endpoints[0].get()
        ep2 = side.endpoints[1].get()

        if not isDashed:
            pygame.draw.line(win, color, ep1, ep2, lineWidth)
        else:
            drawDashedLine(color, ep1, ep2, lineWidth)

        pygame.draw.circle(win, WHITE, ep1, 4)
        pygame.draw.circle(win, WHITE, ep2, 4)

    pygame.display.update()


def drawDashedLine(color, startPos, endPos, width=1, dashLength=5):
    """Draw a dashed line on the window.

    Args:
        color (3-tuple): The line color.
        startPos (Point): The start point of the line.
        endPos (Point): The end point of the line.
        width (int): The line width.
        dashLength (int): The length of the dash.
    """
    origin = Point(startPos)
    target = Point(endPos)
    displacement = target - origin
    length = len(displacement)
    slope = Point((displacement.x / length, displacement.y / length))

    for index in range(0, length // dashLength, 2):
        start = origin + (slope * index * dashLength)
        end = origin + (slope * (index + 1) * dashLength)
        pygame.draw.line(win, color, start.get(), end.get(), width)


def handleClick(game):
    """Handle the mouse click event."""

    helpers.measureStart("Click")

    mouseX, mouseY = pygame.mouse.get_pos()
    mousePos = Point((mouseX, mouseY))

    side, dist = game.getNearestSide(mousePos)

    # If the distance is greather than this threshold, the click will not register.
    toggleDistanceThreshold = 20

    if dist < toggleDistanceThreshold:
        side.toggleStatus()

    execTime = helpers.measureEnd("Click")
    print(f"{execTime}ms")


def reset(game):
    """Reset the board."""
    game.init()


def main():
    """Main function."""

    run = True

    game = HexGame(WIDTH, HEIGHT, 5, "...24.2143..53...4.")

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                handleClick(game)
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                kmods = pygame.key.get_mods()

                # Ctrl-R
                if (kmods & pygame.KMOD_CTRL) and keys[pygame.K_r]:
                    reset(game)

        render(game)


if __name__ == "__main__":
    while True:
        main()
