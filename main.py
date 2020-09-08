"""A Hexagon Slitherlink Game"""

import os
import re
import sys
import pygame

from game_renderer import GameRenderer
import helpers as helper
import constants
import input_file

from point import Point
from hex_game import HexGame
from hex_solver import HexSolver

# Initialize window
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (10, 30)

# Initialize pygame
pygame.init()

# Initialize screen
SCREEN = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Slitherlink Hexagons")

# Clock
clock = pygame.time.Clock()

# FPS
FPS = 60


def clickSide(game):
    """Handle the mouse click event."""

    helper.measureStart("Click")

    mouseX, mouseY = pygame.mouse.get_pos()
    mousePos = Point((mouseX, mouseY))

    side, dist = helper.getNearestSide(game.sides, mousePos)

    # If the distance is greather than this threshold, the click will not register.
    toggleDistanceThreshold = 20

    if dist < toggleDistanceThreshold:
        game.toggleSideStatus(side)

    execTime = helper.measureEnd("Click")
    print("handleClick: {:.3f}ms".format(execTime))


def clickCell(game):
    """Save the coordinates of the nearest cell from a clicked point."""

    mouseX, mouseY = pygame.mouse.get_pos()
    mousePos = Point((mouseX, mouseY))

    cell, dist = helper.getNearestCell(game.cells, mousePos)

    clickCellDistanceThreshold = game.cellSideWidth
    if dist < clickCellDistanceThreshold:
        game.clickedCell = cell


def solveOne(game, solver):
    """Get one move from the solver and apply it."""
    prevMove = game.peekPrevMove()
    prevSide = game.sides[prevMove.sideId] if prevMove is not None else None
    prevSideCoords = prevSide.midpoint if prevSide is not None else None
    nextMove = solver.getNextMove(prevSideCoords)
    if nextMove is not None:
        side = game.sides[nextMove.sideId]
        game.setSideStatus(nextMove)
        solver.inspectObviousVicinity(side)
    else:
        print("No moves left.")


def undoOne(game, solver):
    """Undo the previous move."""
    if len(game.moveHistory) > 0:
        prevMove = game.moveHistory.pop()
        reverseMove = prevMove.reverse()
        game.setSideStatus(reverseMove, appendToHistory=False)
        if prevMove.fromSolver:
            solver.nextMoveList.insert(0, prevMove)


def reset(game, solver):
    """Reset the board."""
    game.init()
    solver.reset()


def solveAll(solver):
    """Solve the board."""
    solver.solveAll()


def main():
    """Main function."""

    rows = input_file.INPUT3["rows"]
    dataStr = re.sub(r"\s+", "", input_file.INPUT3["dataStr"])

    horizontalMargin = constants.SCREEN_LEFT_MARGIN + constants.SCREEN_RIGHT_MARGIN
    verticalMargin = constants.SCREEN_TOP_MARGIN + constants.SCREEN_BOTTOM_MARGIN
    targetWidth = constants.SCREEN_WIDTH - horizontalMargin
    targetHeight = constants.SCREEN_HEIGHT - verticalMargin

    cellSideWidth = helper.calculateOptimalSideLength(targetWidth, targetHeight, rows)

    centerX = targetWidth // 2 + constants.SCREEN_LEFT_MARGIN
    centerY = targetHeight // 2 + constants.SCREEN_TOP_MARGIN

    print("Creating game...")
    game = HexGame((centerX, centerY), cellSideWidth, rows, dataStr)
    print("Created game with {} rows, {} cells, and {} sides.".format(
        game.rows, len(game.cells), len(game.sides)))

    # Initialize the solver
    solver = HexSolver(game)

    gameRenderer = GameRenderer(game, SCREEN)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed() == (True, False, False):
                    # Left Click
                    clickSide(game)
                elif pygame.mouse.get_pressed() == (False, False, True):
                    # Right Click
                    clickCell(game)
            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                kmods = pygame.key.get_mods()

                # RIGHT
                if keys[pygame.K_RIGHT]:
                    solveOne(game, solver)

                # LEFT
                if keys[pygame.K_LEFT]:
                    undoOne(game, solver)

                # Ctrl-R
                if (kmods & pygame.KMOD_CTRL) and keys[pygame.K_r]:
                    reset(game, solver)

                # Ctrl-X
                if (kmods & pygame.KMOD_CTRL) and keys[pygame.K_x]:
                    solveAll(solver)

        gameRenderer.render()
        clock.tick(FPS)


if __name__ == "__main__":
    while True:
        main()
