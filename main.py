"""A Hexagon Slitherlink Game"""

import os
import re
import sys

import pygame
import Colors
import helpers
import Constants
import inputfile
from point import Point
from hexgame import HexGame
from sidestatus import SideStatus

# Initialize window location
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (10, 20)

# Initialize pygame
pygame.init()

# Initialize font
FONT = pygame.font.SysFont("Courier", 15)
FPS_FONT = pygame.font.SysFont("Arial", 18)

# Screen
screen = pygame.display.set_mode((Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))
pygame.display.set_caption("Slitherlink")

# Clock
clock = pygame.time.Clock()
FPS = 30


def render(game):
    """Draws the game board."""

    # Background
    screen.fill(Colors.BLACK)

    # Margin
    # drawMargins()

    updateRects = []

    # Draw the cell numbers
    for cell in game.cells:
        if cell.reqSides is not None:
            if cell.numDirty:
                reqSidesFont = pygame.font.SysFont("Courier", 20)
                rect = displayText(str(cell.reqSides), cell.center, reqSidesFont, Colors.WHITE)
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

    # Draw the FPS display
    drawFps()
    updateRects.append((10, 0, 30, 30))

    # Update the screen, but only the areas/rects that have changed
    pygame.display.update(updateRects)


def drawFps():
    """Draw the FPS on the screen."""
    fps = str(int(clock.get_fps()))
    fpsText = FPS_FONT.render(fps, 1, pygame.Color("coral"))
    screen.blit(fpsText, (10, 0))


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
        color = Colors.GRAY
    elif side.status == SideStatus.ACTIVE:
        isDashed = False
        lineWidth = 3
        color = Colors.SIDE_COLORS[side.colorIdx % len(Colors.SIDE_COLORS)]
    elif side.status == SideStatus.BLANK:
        isDashed = True
        lineWidth = 2
        color = Colors.DARKER_GRAY
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
    #         return Colors.SIDE_COLORS[side.colorIdx]
    return 2, Colors.WHITE


def drawMargins():
    """Draw the margins on the screen."""

    screenWidth = Constants.SCREEN_WIDTH
    screenHeight = Constants.SCREEN_HEIGHT
    topMargin = Constants.SCREEN_TOP_MARGIN
    botMargin = Constants.SCREEN_BOTTOM_MARGIN
    leftMargin = Constants.SCREEN_LEFT_MARGIN
    rightMargin = Constants.SCREEN_RIGHT_MARGIN

    upperLeft = (leftMargin, topMargin)
    upperRight = (screenWidth - rightMargin, topMargin)
    lowerLeft = (leftMargin, screenHeight - botMargin)
    lowerRight = (screenWidth - rightMargin, screenHeight - botMargin)

    pygame.draw.line(screen, Colors.WHITE, upperLeft, upperRight, 1)
    pygame.draw.line(screen, Colors.WHITE, upperRight, lowerRight, 1)
    pygame.draw.line(screen, Colors.WHITE, lowerRight, lowerLeft, 1)
    pygame.draw.line(screen, Colors.WHITE, lowerLeft, upperLeft, 1)


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


def handleClick(game):
    """Handle the mouse click event."""

    helpers.measureStart("Click")

    mouseX, mouseY = pygame.mouse.get_pos()
    mousePos = Point((mouseX, mouseY))

    side, dist = helpers.getNearestSide(game.sides, mousePos)

    # If the distance is greather than this threshold, the click will not register.
    toggleDistanceThreshold = 20

    if dist < toggleDistanceThreshold:
        game.toggleSideStatus(side)

    execTime = helpers.measureEnd("Click")
    print("handleClick: {:.3f}ms".format(execTime))


def reset(game):
    """Reset the board."""
    game.init()


def main():
    """Main function."""

    rows = inputfile.INPUT1["rows"]
    dataStr = re.sub(r"\s+", "", inputfile.INPUT1["dataStr"])

    horizontalMargin = Constants.SCREEN_LEFT_MARGIN + Constants.SCREEN_RIGHT_MARGIN
    verticalMargin = Constants.SCREEN_TOP_MARGIN + Constants.SCREEN_BOTTOM_MARGIN
    targetWidth = Constants.SCREEN_WIDTH - horizontalMargin
    targetHeight = Constants.SCREEN_HEIGHT - verticalMargin

    cellSideWidth = helpers.calculateOptimalSideLength(targetWidth, targetHeight, rows)

    centerX = targetWidth // 2 + Constants.SCREEN_LEFT_MARGIN
    centerY = targetHeight // 2 + Constants.SCREEN_TOP_MARGIN

    game = HexGame((centerX, centerY), cellSideWidth, rows, dataStr)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                handleClick(game)
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                kmods = pygame.key.get_mods()

                # Ctrl-R
                if (kmods & pygame.KMOD_CTRL) and keys[pygame.K_r]:
                    reset(game)

        render(game)
        clock.tick(FPS)


if __name__ == "__main__":
    while True:
        main()
