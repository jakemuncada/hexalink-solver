"""A Hexagon Slitherlink Game"""

import os
import re
import sys
import pygame

import colors
import constants
import helpers as helper

import input_file
from point import Point
from hex_game import HexGame
from hex_solver import HexSolver
from side_status import SideStatus

# Initialize window location
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (10, 20)

# Initialize pygame
pygame.init()

# Initialize font
FONT = pygame.font.SysFont("Courier", 15)
FPS_FONT = pygame.font.SysFont("Arial", 18)

# Screen
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Slitherlink")

# Clock
clock = pygame.time.Clock()
FPS = 30


def render(game):
    """Draws the game board."""

    # Background
    screen.fill(colors.BLACK)

    # Margin
    # drawMargins()

    updateRects = []

    # Draw the cell numbers
    for cell in game.reqCells:
        if cell.numDirty:
            reqSidesFont = pygame.font.SysFont("Courier", 20)
            rect = displayText(str(cell.reqSides), cell.center, reqSidesFont, colors.WHITE)
            updateRects.append(rect)
            cell.numDirty = False

    # Array of dirty HexVertices
    dirtyVertices = []

    # Draw the sides
    for side in game.sides:
        lineWidth, isDashed, color = getSideDrawInfo(side)

        # The coordinates of the endpoints
        ep1 = side.endpoints[0].coords.get()
        ep2 = side.endpoints[1].coords.get()

        if not isDashed:
            # If not dashed, draw a straight line
            rect = pygame.draw.line(screen, color, ep1, ep2, lineWidth)
        else:
            # Else, draw a dashed line
            rect = drawDashedLine(color, ep1, ep2, lineWidth)

        # Add the dirty sides to the list
        if side.isDirty:
            side.isDirty = False
            updateRects.append(rect)
            dirtyVertices.append(side.endpoints[0])
            dirtyVertices.append(side.endpoints[1])

    # Draw the dirty vertices last so that the dots are above any of the lines
    for dirtyVertex in dirtyVertices:
        radius, color = getVertexDrawInfo(dirtyVertex)
        rect = pygame.draw.circle(screen, color, dirtyVertex.coords.get(), radius)
        updateRects.append(rect)

    # Display FPS
    drawFps()
    updateRects.append((10, 0, 30, 30))

    # Display clicked cell coords
    rect = drawClickedCellCoords(game)
    if rect is not None:
        updateRects.append(rect)

    # Update the screen, but only the areas/rects that have changed
    pygame.display.update(updateRects)


def drawFps():
    """Draw the FPS on the screen."""
    fps = str(int(clock.get_fps()))
    fpsText = FPS_FONT.render(fps, 1, pygame.Color("coral"))
    screen.blit(fpsText, (10, 0))


def drawClickedCellCoords(game):
    """Display the clicked cell coordinates."""
    rect = None
    if game.clickedCell is not None:
        text = FPS_FONT.render(str(game.clickedCell), 1, colors.WHITE)
        game.prevClickedCell = game.clickedCell
        game.clickedCell = None
        rect = screen.blit(text, (10, 30))
        rect.width = 50  # Manually widen the rect
    return rect


def getSideDrawInfo(side):
    """Get the draw info of the side. Returns `(lineWidth, isDashed, color)`,
    which is a tuple containing the draw info.

    Args:
        side (HexSide): The side to be drawn.

    Returns:
        lineWidth (int): The width of the line.
        isDashed (bool): Whether or not the line is a dashed line.
        color (3-tuple): The color of the line.
    """
    if side.status == SideStatus.UNSET:
        isDashed = True
        lineWidth = 2
        color = colors.GRAY
    elif side.status == SideStatus.ACTIVE:
        isDashed = False
        lineWidth = 3
        color = colors.SIDE_COLORS[side.colorIdx % len(colors.SIDE_COLORS)]
    elif side.status == SideStatus.BLANK:
        isDashed = True
        lineWidth = 2
        color = colors.DARKER_GRAY
    else:
        raise AssertionError(f"Invalid side status: {side.status}")

    return lineWidth, isDashed, color


def getVertexDrawInfo(_):
    """Get the draw info of the vertex. Returns `radius, color`,
    which is a tuple containing the draw info.

    Args:
        vertex (HexVertex): The vertex to be drawn.

    Returns:
        radius (int): The radius of the vertex.
        color (3-tuple): The color of the vertex.
    """
    # for side in vertex.sides:
    #     if side.isActive():
    #         return colors.SIDE_COLORS[side.colorIdx]
    return 2, colors.WHITE


def drawMargins():
    """Draw the margins on the screen."""

    screenWidth = constants.SCREEN_WIDTH
    screenHeight = constants.SCREEN_HEIGHT
    topMargin = constants.SCREEN_TOP_MARGIN
    botMargin = constants.SCREEN_BOTTOM_MARGIN
    leftMargin = constants.SCREEN_LEFT_MARGIN
    rightMargin = constants.SCREEN_RIGHT_MARGIN

    upperLeft = (leftMargin, topMargin)
    upperRight = (screenWidth - rightMargin, topMargin)
    lowerLeft = (leftMargin, screenHeight - botMargin)
    lowerRight = (screenWidth - rightMargin, screenHeight - botMargin)

    pygame.draw.line(screen, colors.WHITE, upperLeft, upperRight, 1)
    pygame.draw.line(screen, colors.WHITE, upperRight, lowerRight, 1)
    pygame.draw.line(screen, colors.WHITE, lowerRight, lowerLeft, 1)
    pygame.draw.line(screen, colors.WHITE, lowerLeft, upperLeft, 1)


def displayText(text, coords, font, color):
    """Display text on the screen.

    Args:
        text (string): The text to display.
        coords (Point): The center coordinates of the text rect.
        font (pygame.font): The font to be used.
        color (3-tuple): The text color.

    Returns:
        pygame.Rect: The rect of the font surface.
    """
    fontSurface = font.render(str(text), True, color)
    rect = fontSurface.get_rect(center=coords.get())
    screen.blit(fontSurface, rect)
    return rect


def drawDashedLine(color, startPos, endPos, width=1, dashLength=5):
    """Draw a dashed line on the window.

    Args:
        color (3-tuple): The line color.
        startPos (2-tuple): The start point of the line.
        endPos (2-tuple): The end point of the line.
        width (int): The line width.
        dashLength (int): The length of the dash.

    Returns:
        pygame.Rect: The rect of the dashed line.
    """
    origin = Point(startPos)
    target = Point(endPos)
    displacement = target - origin
    length = len(displacement)
    slope = Point((displacement.x / length, displacement.y / length))

    for index in range(0, length // dashLength, 2):
        start = origin + (slope * index * dashLength)
        end = origin + (slope * (index + 1) * dashLength)
        pygame.draw.line(screen, color, start.get(), end.get(), width)

    left = min(startPos[0], endPos[0])
    top = min(startPos[1], endPos[1])
    width = abs(startPos[0] - endPos[0])
    height = abs(startPos[1] - endPos[1])
    width += 3
    height += 3

    return pygame.Rect(left, top, width, height)


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


def solveOne(solver):
    """Get one move from the solver and apply it."""
    nextMove = solver.getNextMove()
    if nextMove is not None:
        side = solver.game.sides[nextMove.sideId]
        solver.game.setSideStatus(side, nextMove.newStatus)
        solver.inspectObviousVicinity(side)
        print(f"Side {side} was set to {nextMove.newStatus}.")
    else:
        print("No moves left.")


def reset(game):
    """Reset the board."""
    game.init()


def main():
    """Main function."""

    rows = input_file.INPUT1["rows"]
    dataStr = re.sub(r"\s+", "", input_file.INPUT1["dataStr"])

    horizontalMargin = constants.SCREEN_LEFT_MARGIN + constants.SCREEN_RIGHT_MARGIN
    verticalMargin = constants.SCREEN_TOP_MARGIN + constants.SCREEN_BOTTOM_MARGIN
    targetWidth = constants.SCREEN_WIDTH - horizontalMargin
    targetHeight = constants.SCREEN_HEIGHT - verticalMargin

    cellSideWidth = helper.calculateOptimalSideLength(targetWidth, targetHeight, rows)

    centerX = targetWidth // 2 + constants.SCREEN_LEFT_MARGIN
    centerY = targetHeight // 2 + constants.SCREEN_TOP_MARGIN

    game = HexGame((centerX, centerY), cellSideWidth, rows, dataStr)
    solver = HexSolver(game)

    # TODO Use pygame.display.get_active() to solve text disappearing after minimize window

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # clickSide(game)
                clickCell(game)
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                kmods = pygame.key.get_mods()

                # Ctrl-R
                if (kmods & pygame.KMOD_CTRL) and keys[pygame.K_r]:
                    reset(game)

                # RIGHT
                if keys[pygame.K_RIGHT]:
                    solveOne(solver)

        render(game)
        clock.tick(FPS)


if __name__ == "__main__":
    while True:
        main()
