"""A Hexagon Slitherlink Game"""

import os
import random
from datetime import datetime

import pygame
from point import Point
from hexboard import HexBoard
from sidestatus import SideStatus

# Initialize window location
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (20, 50)

# Initialize pygame
pygame.init()

# Seed the RNG
random.seed(datetime.now())

# Screen
WIDTH = 1280
HEIGHT = 960
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
CELL_SIDE_WIDTH = 20
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slitherlink")

# Game Board
board = HexBoard.create(WIDTH, HEIGHT, 5, "...24.2143..53...4.")
# for rowArr in board.board:
#     for cell in rowArr:
#         print(cell.center)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
DARKER_GRAY = (25, 25, 25)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


for rowArr2 in board.board:
    for cell2 in rowArr2:
        pygame.draw.circle(win, WHITE, cell2.center.get(), 2)
        for side2 in cell2.sides:
            asdf = random.randint(1, 3)
            if asdf == 1:
                side2.status = SideStatus.UNSET
            elif asdf == 2:
                side2.status = SideStatus.ACTIVE
            elif asdf == 3:
                side2.status = SideStatus.BLANK


def render():
    """Draws the game board."""
    win.fill(BLACK)

    for rowArr in board.board:
        for cell in rowArr:
            pygame.draw.circle(win, WHITE, cell.center.get(), 2)
            for side in cell.sides:
                if side.status == SideStatus.UNSET:
                    isDashed = True
                    lineWidth = 5
                    color = GRAY
                elif side.status == SideStatus.ACTIVE:
                    isDashed = False
                    lineWidth = 5
                    color = BLUE
                elif side.status == SideStatus.BLANK:
                    isDashed = True
                    lineWidth = 5
                    color = DARKER_GRAY

                ep1 = side.endpoints[0].get()
                ep2 = side.endpoints[1].get()

                if not isDashed:
                    pygame.draw.line(win, color, ep1, ep2, lineWidth)
                else:
                    drawDashedLine(color, ep1, ep2, lineWidth)

                pygame.draw.circle(win, RED, ep1, 4)
                pygame.draw.circle(win, RED, ep2, 4)

    pygame.display.update()


def drawDashedLine(color, startPos, endPos, width=1, dashLength=6):
    """Draw a dashed line on the window."""
    origin = Point(startPos)
    target = Point(endPos)
    displacement = target - origin
    length = len(displacement)
    slope = Point((displacement.x / length, displacement.y / length))

    for index in range(0, length // dashLength, 2):
        start = origin + (slope * index * dashLength)
        end = origin + (slope * (index + 1) * dashLength)
        pygame.draw.line(win, color, start.get(), end.get(), width)


def main():
    """Main function."""

    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass

        render()


if __name__ == "__main__":
    while True:
        main()
