"""A Hexagon Slitherlink Game"""

import os
import re
import sys

import pygame
import helpers
import constants
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
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Slitherlink")

# Clock
clock = pygame.time.Clock()
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
DARKER_GRAY = (35, 35, 35)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)


def render(game):
    """Draws the game board."""

    # Background
    screen.fill(BLACK)

    # Margin
    # drawMargins()

    for rowArr in game.board:
        for cell in rowArr:
            if cell.reqSides is not None:
                # reqSidesFont = pygame.font.SysFont("Courier", int(60 * game.cellSideWidth / 100))
                reqSidesFont = pygame.font.SysFont("Courier", 20)
                displayText(str(cell.reqSides), cell.center, reqSidesFont, WHITE)

    for side in game.sides:
        if side.status == SideStatus.UNSET:
            isDashed = True
            lineWidth = 2
            color = GRAY
        elif side.status == SideStatus.ACTIVE:
            isDashed = False
            lineWidth = 3
            color = constants.SIDE_COLORS[side.colorIdx]
        elif side.status == SideStatus.BLANK:
            isDashed = True
            lineWidth = 2
            color = DARKER_GRAY

        ep1 = side.endpoints[0].coords.get()
        ep2 = side.endpoints[1].coords.get()

        if not isDashed:
            pygame.draw.line(screen, color, ep1, ep2, lineWidth)
        else:
            drawDashedLine(color, ep1, ep2, lineWidth)

        pygame.draw.circle(screen, WHITE, ep1, 2)
        pygame.draw.circle(screen, WHITE, ep2, 2)

    for vertex in game.vertices:
        vtxCoord = vertex.coords.get()
        pygame.draw.circle(screen, WHITE, vtxCoord, 2)

    drawFps()
    pygame.display.update()


def drawFps():
    """Draw the FPS on the screen."""
    fps = str(int(clock.get_fps()))
    fpsText = FPS_FONT.render(fps, 1, pygame.Color("coral"))
    screen.blit(fpsText, (10, 0))


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

    pygame.draw.line(screen, WHITE, upperLeft, upperRight, 1)
    pygame.draw.line(screen, WHITE, upperRight, lowerRight, 1)
    pygame.draw.line(screen, WHITE, lowerRight, lowerLeft, 1)
    pygame.draw.line(screen, WHITE, lowerLeft, upperLeft, 1)


def displayText(text, coords, font, color):
    """Display text on the screen.

    Args:
        text (string): The text to display.
        coords (Point): The center coordinates of the text rect.
        font (pygame.font): The font to be used.
        color (3-tuple): The text color.
    """
    fontSurface = font.render(str(text), True, color)
    rect = fontSurface.get_rect(center=coords.get())
    screen.blit(fontSurface, rect)


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
        pygame.draw.line(screen, color, start.get(), end.get(), width)


def handleClick(game):
    """Handle the mouse click event."""

    helpers.measureStart("Click")

    mouseX, mouseY = pygame.mouse.get_pos()
    mousePos = Point((mouseX, mouseY))

    side, dist = game.getNearestSide(mousePos)

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

    horizontalMargin = constants.SCREEN_LEFT_MARGIN + constants.SCREEN_RIGHT_MARGIN
    verticalMargin = constants.SCREEN_TOP_MARGIN + constants.SCREEN_BOTTOM_MARGIN
    targetWidth = constants.SCREEN_WIDTH - horizontalMargin
    targetHeight = constants.SCREEN_HEIGHT - verticalMargin

    cellSideWidth = helpers.calculateOptimalSideLength(targetWidth, targetHeight, rows)

    centerX = targetWidth // 2 + constants.SCREEN_LEFT_MARGIN
    centerY = targetHeight // 2 + constants.SCREEN_TOP_MARGIN

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
