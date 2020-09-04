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
pygame.display.set_caption("Slitherlink Hexagons")

# Surfaces
baseSurface = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
vertexDotSurface = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
reqNumSurface = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
moveMsgSurface = pygame.Surface((500, 40))
baseSurface.set_colorkey(colors.BLACK, pygame.RLEACCEL)
vertexDotSurface.set_colorkey(colors.BLACK, pygame.RLEACCEL)
reqNumSurface.set_colorkey(colors.BLACK, pygame.RLEACCEL)
moveMsgSurface.set_colorkey(colors.PINK, pygame.RLEACCEL)

# Clock
clock = pygame.time.Clock()
FPS = 60


def render(game):
    """Draws the game board."""

    # Draw the base surface
    screen.blit(baseSurface, (0, 0))

    # Draw the sides
    for side in game.sides:
        lineWidth, isDashed, color = getSideDrawInfo(side)

        # The coordinates of the endpoints
        ep1 = side.endpoints[0].coords.get()
        ep2 = side.endpoints[1].coords.get()

        if not isDashed:
            # If not dashed, draw a straight line
            pygame.draw.line(screen, color, ep1, ep2, lineWidth)
        else:
            # Else, draw a dashed line
            pygame.draw.line(screen, colors.BLACK, ep1, ep2, 3)
            drawDashedLine(screen, color, ep1, ep2, lineWidth)

        # Add the dirty sides to the list
        if side.isDirty:
            side.isDirty = False

    # Overlay the vertex dots
    screen.blit(vertexDotSurface, (0, 0))

    # Overlay the cell numbser
    screen.blit(reqNumSurface, (0, 0))

    # Display FPS
    drawFps()

    # Display move msg
    drawMoveMsg(game)

    # Display clicked cell coords
    drawClickedCellCoords(game)

    # Update the screen
    pygame.display.update()


def drawFps():
    """Display the FPS on the screen."""
    fps = str(int(clock.get_fps()))
    fpsText = FPS_FONT.render(fps, 1, pygame.Color("coral"), colors.BLACK)
    screen.blit(fpsText, (10, 0))


def drawMoveMsg(game):
    """Display the explanation message of the previous move on the screen."""
    moveMsgSurface.fill(colors.BLACK)
    if len(game.moveHistory) > 0:
        prevMove = game.moveHistory[len(game.moveHistory) - 1]
        side = game.sides[prevMove.sideId]
        prevMoveStr = prevMove.msg
        if prevMoveStr is not None:
            locationStr = f"  {str(side)}"
            text = FPS_FONT.render(prevMoveStr + locationStr, 1, colors.WHITE)
            moveMsgSurface.blit(text, (0, 0))
    screen.blit(moveMsgSurface, (10, 80))


def drawClickedCellCoords(game):
    """Display the clicked cell coordinates."""
    rect = None
    if game.clickedCell is not None:
        text = FPS_FONT.render(str(game.clickedCell), 1, colors.WHITE, colors.BLACK)
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


def displayText(surface, text, coords, font, color):
    """Display text on the screen.

    Args:
        surface (pygame.Surface): The surface to draw on.
        text (string): The text to display.
        coords (Point): The center coordinates of the text rect.
        font (pygame.font): The font to be used.
        color (3-tuple): The text color.

    Returns:
        pygame.Rect: The rect of the font surface.
    """
    fontSurface = font.render(str(text), True, color)
    rect = fontSurface.get_rect(center=coords.get())
    surface.blit(fontSurface, rect)
    return rect


def drawDashedLine(surface, color, startPos, endPos, width=1, dashLength=5):
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
        pygame.draw.line(surface, color, start.get(), end.get(), width)

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


def reset(game):
    """Reset the board."""
    game.init()


def prepareBaseSurface(game):
    """Draw an unset game board to be used for the base surface."""

    # Background
    screen.fill(colors.BLACK)

    lineWidth = 2
    color = colors.GRAY

    for side in game.sides:
        # The coordinates of the endpoints
        ep1 = side.endpoints[0].coords.get()
        ep2 = side.endpoints[1].coords.get()
        drawDashedLine(baseSurface, color, ep1, ep2, lineWidth)


def prepareReqNumSurface(game):
    """Draw the cell numbers."""

    reqNumSurface.fill(colors.BLACK)

    for cell in game.reqCells:
        reqSidesFont = pygame.font.SysFont("Courier", 20)
        displayText(reqNumSurface, str(cell.reqSides), cell.center, reqSidesFont, colors.WHITE)


def prepareVertexDotSurface(game):
    """Draw the vertex dots."""

    # Background
    screen.fill(colors.BLACK)

    # Keep track of already drawn vertices
    drawnVertices = set()

    color = colors.WHITE
    radius = 2

    # Draw the cell vertices
    for cell in game.cells:
        for vertex in cell.vertices:
            if vertex not in drawnVertices:
                drawnVertices.add(vertex)
                pygame.draw.circle(vertexDotSurface, color, vertex.coords.get(), radius)


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

    print("Creating game...")
    game = HexGame((centerX, centerY), cellSideWidth, rows, dataStr)
    print("Created game with {} rows, {} cells, and {} sides.".format(
        game.rows, len(game.cells), len(game.sides)))

    # Prepare the surfaces
    prepareBaseSurface(game)
    prepareReqNumSurface(game)
    prepareVertexDotSurface(game)

    # Initialize the solver
    solver = HexSolver(game)

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

                # Ctrl-R
                if (kmods & pygame.KMOD_CTRL) and keys[pygame.K_r]:
                    reset(game)

                # RIGHT
                if keys[pygame.K_RIGHT]:
                    solveOne(game, solver)

                # LEFT
                if keys[pygame.K_LEFT]:
                    undoOne(game, solver)

        render(game)
        clock.tick(FPS)


if __name__ == "__main__":
    while True:
        main()
