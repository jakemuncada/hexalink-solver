"""A Hexagon Slitherlink Game"""

import pygame
from hexboard import HexBoard

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

# Game Board
board = HexBoard.create(WIDTH, HEIGHT, 5, "...24.2143..53...4.")
# for rowArr in board.board:
#     for cell in rowArr:
#         print(cell.center)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


def render():
    """Draws the game board."""
    win.fill(BLACK)

    for rowArr in board.board:
        for cell in rowArr:
            pygame.draw.circle(win, WHITE, cell.center.get(), 2)
            for side in cell.sides:
                pygame.draw.aaline(win, GRAY, side.endpoints[0].get(), side.endpoints[1].get())
                pygame.draw.circle(win, RED, side.endpoints[0].get(), 2)
                pygame.draw.circle(win, RED, side.endpoints[1].get(), 2)

    pygame.display.update()


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
