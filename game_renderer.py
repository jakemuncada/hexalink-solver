"""Main renderer"""

import pygame

from point import Point
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from colors import SIDE_COLORS, WHITE, BLACK, PINK, GRAY, DARKER_GRAY, ORANGE

# Initialize pygame
pygame.init()

# Clock
clock = pygame.time.Clock()


class GameRenderer:
    """The class responsible for drawing stuff on the screen."""

    # Surfaces
    BASE_SURFACE = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    VERTEX_SURFACE = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    CELL_NUM_SURFACE = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    MOVE_MSG_SURFACE = pygame.Surface((500, 40))

    # Font
    CELL_FONT = pygame.font.SysFont("Courier", 20)
    INFO_FONT = pygame.font.SysFont("Courier", 18)

    # Line Width and Dot Radius
    ACTIVE_LINE_WIDTH = 3
    BLANK_LINE_WIDTH = 2
    UNSET_LINE_WIDTH = 2
    DASH_LENGTH = 5
    VERTEX_RADIUS = 2

    # Line Colors
    BLANK_LINE_COLOR = DARKER_GRAY
    UNSET_LINE_COLOR = GRAY
    VERTEX_COLOR = WHITE
    FPS_TEXT_COLOR = ORANGE
    INFO_TEXT_COLOR = WHITE

    def __init__(self, game, screen, ):

        self.screen = screen
        self.game = game

        # Initialize the surfaces.
        GameRenderer.BASE_SURFACE.set_colorkey(BLACK, pygame.RLEACCEL)
        GameRenderer.VERTEX_SURFACE.set_colorkey(BLACK, pygame.RLEACCEL)
        GameRenderer.CELL_NUM_SURFACE.set_colorkey(BLACK, pygame.RLEACCEL)
        GameRenderer.MOVE_MSG_SURFACE.set_colorkey(PINK, pygame.RLEACCEL)

        self.__initializeBaseSurface__()
        self.__initializeCellNumSurface__()
        self.__initializeVertexSurface__()

    def render(self):
        """Draws the game board."""

        self.screen.fill(BLACK)

        self.__drawBase__()
        self.__drawSides__()
        self.__drawVertices__()
        self.__drawCellNumbers__()
        self.__drawFps__()
        self.__drawMoveMsg__()
        self.__drawClickedCellCoords__()

        # Update the screen
        pygame.display.update()

    ################################################################################
    # INITIALIZE
    ################################################################################

    def __initializeBaseSurface__(self):
        """
        Initialize the base surface.
        The base surface is the entire board with all the sides UNSET.
        """

        GameRenderer.BASE_SURFACE.fill(BLACK)

        for side in self.game.sides:
            GameRenderer.__drawUnsetSide__(side, GameRenderer.BASE_SURFACE)

    def __initializeVertexSurface__(self):
        """Initialize the surface containing the vertex dots."""

        # Background
        GameRenderer.VERTEX_SURFACE.fill(BLACK)

        # Keep track of already drawn vertices
        drawnVertices = set()

        # Draw the cell vertices
        for cell in self.game.cells:
            for vertex in cell.vertices:
                if vertex not in drawnVertices:
                    drawnVertices.add(vertex)
                    pygame.draw.circle(GameRenderer.VERTEX_SURFACE, GameRenderer.VERTEX_COLOR,
                                       vertex.coords.get(), GameRenderer.VERTEX_RADIUS)

    def __initializeCellNumSurface__(self):
        """Initialize the surface containing the cell numbers."""

        GameRenderer.CELL_NUM_SURFACE.fill(BLACK)

        for cell in self.game.reqCells:
            GameRenderer.drawText(GameRenderer.CELL_NUM_SURFACE, str(cell.reqSides),
                                  cell.center, GameRenderer.CELL_FONT, WHITE)

    ################################################################################
    # DRAW BOARD PARTS
    ################################################################################

    def __drawBase__(self):
        """Draw the board base. The board base is the entire board with all sides UNSET."""
        self.screen.blit(GameRenderer.BASE_SURFACE, (0, 0))

    def __drawSides__(self):
        """Draw the blank and active sides of the board."""
        for side in self.game.sides:
            if side.isBlank():
                self.__drawBlankSide__(side, self.screen)
            elif side.isActive():
                self.__drawActiveSide__(side, self.screen)

    def __drawVertices__(self):
        """Draw the vertices."""
        self.screen.blit(GameRenderer.VERTEX_SURFACE, (0, 0))

    def __drawCellNumbers__(self):
        """Draw the vertices."""
        self.screen.blit(GameRenderer.CELL_NUM_SURFACE, (0, 0))

    def __drawFps__(self):
        """Draw the FPS."""
        fps = str(int(clock.get_fps()))
        fpsText = GameRenderer.INFO_FONT.render(fps, 1, GameRenderer.FPS_TEXT_COLOR, BLACK)
        self.screen.blit(fpsText, (10, 0))

    def __drawMoveMsg__(self):
        """Draw the explanation message of the previous move on the screen."""
        GameRenderer.MOVE_MSG_SURFACE.fill(BLACK)

        prevMove = self.game.peekPrevMove()

        if prevMove is not None:
            side = self.game.sides[prevMove.sideId]
            prevMoveStr = prevMove.msg
            if prevMoveStr is not None:
                displayStr = f"{prevMoveStr}  {str(side)}"
                text = GameRenderer.INFO_FONT.render(displayStr, 1, WHITE)
                GameRenderer.MOVE_MSG_SURFACE.blit(text, (0, 0))
        self.screen.blit(GameRenderer.MOVE_MSG_SURFACE, (10, 80))

    def __drawClickedCellCoords__(self):
        """Draw the clicked cell coordinates."""
        if self.game.clickedCell is not None:
            text = GameRenderer.INFO_FONT.render(str(self.game.clickedCell),
                                                 1, GameRenderer.INFO_TEXT_COLOR, BLACK)
            self.game.prevClickedCell = self.game.clickedCell
            self.game.clickedCell = None
            self.screen.blit(text, (10, 30))

    ################################################################################
    # DRAW SIDES
    ################################################################################

    @staticmethod
    def __drawActiveSide__(side, surface):
        """Draw the ACTIVE side."""

        # The coordinates of the endpoints
        ep1 = side.endpoints[0].coords.get()
        ep2 = side.endpoints[1].coords.get()

        color = SIDE_COLORS[side.colorIdx % len(SIDE_COLORS)]
        pygame.draw.line(surface, color, ep1, ep2, GameRenderer.ACTIVE_LINE_WIDTH)

    @staticmethod
    def __drawBlankSide__(side, surface):
        """Draw the BLANK side."""

        # The coordinates of the endpoints
        ep1 = side.endpoints[0].coords.get()
        ep2 = side.endpoints[1].coords.get()

        # First erase the underlying UNSET line (in the BASE surface)
        # by drawing a black line
        pygame.draw.line(surface, BLACK, ep1, ep2, GameRenderer.ACTIVE_LINE_WIDTH)
        # Then draw the BLANK side
        GameRenderer.__drawDashedLine__(surface, GameRenderer.BLANK_LINE_COLOR, ep1, ep2,
                                        GameRenderer.BLANK_LINE_WIDTH)

    @staticmethod
    def __drawUnsetSide__(side, surface):
        """Draw the UNSET side on the given surface."""
        # The coordinates of the endpoints
        ep1 = side.endpoints[0].coords.get()
        ep2 = side.endpoints[1].coords.get()

        GameRenderer.__drawDashedLine__(surface, GameRenderer.UNSET_LINE_COLOR,
                                        ep1, ep2, GameRenderer.UNSET_LINE_WIDTH)

    @staticmethod
    def __drawDashedLine__(surface, color, ep1, ep2, width):
        """Draw a dashed line on the window.

        Args:
            color (3-tuple): The line color.
            ep1 (2-tuple): The coordinates of one endpoint.
            ep2 (2-tuple): The coordinates of the other endpoint.

        Returns:
            pygame.Rect: The rect of the dashed line.
        """
        origin = Point(ep1)
        target = Point(ep2)
        displacement = target - origin
        length = len(displacement)
        slope = Point((displacement.x / length, displacement.y / length))
        dashLength = GameRenderer.DASH_LENGTH

        # Draw the dashes
        for index in range(0, length // dashLength, 2):
            start = origin + (slope * index * dashLength)
            end = origin + (slope * (index + 1) * dashLength)
            pygame.draw.line(surface, color, start.get(), end.get(), width)

    ################################################################################
    # DRAW TEXT
    ################################################################################

    @staticmethod
    def drawText(surface, text, coords, font, color):
        """
        Draw the text on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on.
            text (string): The text to display.
            coords (Point): The center coordinates of the text rect.
            font (pygame.font): The font to be used.
            color (3-tuple): The text color.

        Returns:
            pygame.Rect: The rect of the drawn text.
        """
        fontSurface = font.render(str(text), True, color)
        rect = fontSurface.get_rect(center=coords.get())
        surface.blit(fontSurface, rect)
        return rect
