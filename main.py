"""A Hexagon Slitherlink Game"""

import pygame
from hexboard import HexBoard

# Initialize pygame
pygame.init()

# Screen
WIDTH = 800
HEIGHT = 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slitherlink")

# Game Board
board = HexBoard(5, "...24.2143..53...4.")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


def render():
    """Draws the game board."""
    win.fill(WHITE)


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
