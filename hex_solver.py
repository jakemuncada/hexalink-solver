"""Solver for HexGame."""

from side_status import SideStatus
from hex_game_move import HexGameMove
from hex_dir import HexSideDir

# Define SideStatus members
BLANK = SideStatus.BLANK
ACTIVE = SideStatus.ACTIVE
UNSET = SideStatus.UNSET


class HexSolver:
    """A solver for HexGame."""

    def __init__(self, game):
        self.game = game
        self.nextMoveList = []
        self.processedSideIds = set()

        self.initialBoardInspection()

    def initialBoardInspection(self):
        """Inspect the board and register one-time obvious moves into the `nextMoveList`.

        One-time obvious moves are those that need to be checked only once,
        like the 5-and-5 adjacent cells, or the 1-and-5 adjacent cells, or zero-cells.
        """
        for cell in self.game.reqCells:
            if cell.reqSides == 0:
                # Remove all sides and limbs of zero-cells
                for cellSide in cell.sides:
                    self.addNextMove(cellSide, BLANK)
                for limb in cell.getLimbs():
                    self.addNextMove(limb, BLANK)

            elif cell.reqSides == 1:
                for sideDir in HexSideDir:
                    adjCell = cell.adjCells[sideDir]
                    if adjCell is not None:
                        ###  1-AND-5  ###
                        if adjCell.reqSides == 5:
                            # Set boundary to ACTIVE
                            boundary = cell.sides[sideDir]
                            self.addNextMove(boundary, ACTIVE)
                            # Which means that the 1-Cell is solved
                            moves = completeCell1(cell, sideDir)
                            self.extendNextMoves(moves)
                            # Lastly, polish off the 5-Cell
                            polish = adjCell.getAllSidesConnectedTo(boundary)
                            self.addNextMoves(polish, ACTIVE)

                        ###  1-AND-1  ###
                        if adjCell.reqSides == 1:
                            # Set boundary to BLANK
                            self.addNextMove(cell.sides[sideDir], BLANK)

            elif cell.reqSides == 5:
                for sideDir in HexSideDir:
                    adjCell = cell.adjCells[sideDir]
                    if adjCell is not None:
                        ###  5-AND-5  ###
                        if adjCell.reqSides == 5:
                            # Set boundary to ACTIVE, then cap the opposite ends,
                            # the remove the limbs of the cap
                            self.addNextMove(cell.sides[sideDir], ACTIVE)
                            cap1, limbs1 = cell.getCap(sideDir.opposite())
                            cap2, limbs2 = adjCell.getCap(sideDir)
                            self.addNextMoves(cap1 + cap2, ACTIVE)
                            self.addNextMoves(limbs1 + limbs2, BLANK)

    def inspectObviousVicinity(self, side):
        """Inspect the connected sides and adjacent cells of a given `HexSide`
        for obvious clues. Adds the obvious moves to the `nextMoveList`."""
        for connSide in side.getAllConnectedSides():
            self.inspectObviousSide(connSide)
        for adjCell in side.getAdjCells():
            self.inspectObviousCell(adjCell)

    def inspectObviousSide(self, side):
        """Inspect a given `HexSide` for obvious clues. Does not process non-`UNSET` sides.

        Some obvious clues include:
            ・If the Side is hanging.
            ・If the Side is connected to an existing intersection.
            ・If the Side is connected to an active Side which has nowhere else to go.
        """
        # Check if the side is hanging
        if side.isHanging():
            self.addNextMove(side, BLANK)

    def inspectObviousCell(self, cell):
        """Inspect a given cell for obvious clues.

        Some obvious clues include:
            ・If the cell already has the correct number of ACTIVE or BLANK sides.
        """
        if cell.reqSides is not None:
            if cell.countActiveSides() == cell.reqSides:
                self.addNextMoves(cell.getUnsetSides(), BLANK)

            elif cell.countBlankSides() == cell.requiredBlanks():
                self.addNextMoves(cell.getUnsetSides(), ACTIVE)

    def addNextMove(self, side, newStatus):
        """Add a `HexGameMove` to the `nextMoveList`.
        Only `UNSET` sides can be added to the `nextMoveList`.

        Args:
            side (HexSide): The side to be set.
            newStatus (SideStatus): The new status of the side.
        """
        if side.isUnset() and newStatus != UNSET and side.id not in self.processedSideIds:
            move = HexGameMove(side.id, newStatus)
            self.nextMoveList.append(move)
            self.processedSideIds.add(side.id)

    def addNextMoves(self, sides, newStatus):
        """Add multiple `HexGameMoves` to the `nextMoveList`.
        Uses `addNextMove(side, newStatus)` under the hood.

        Args:
            sides ([HexSide]): The list of sides to be set.
            newStatus (SideStatus): The new status of all the sides in the list.
        """
        for side in sides:
            self.addNextMove(side, newStatus)

    def extendNextMoves(self, moves):
        """Add multiple `HexGameMoves` to the `nextMoveList`.

        Args:
            moves ([HexGameMove]): The list of moves to be added to the nextMoveList.
        """
        for move in moves:
            side = self.game.sides[move.sideId]
            if side.isUnset() and move.newStatus != UNSET:
                if side.id not in self.processedSideIds:
                    self.nextMoveList.append(move)
                    self.processedSideIds.add(side.id)

    def getNextMove(self):
        """Get the next correct move.

        Returns:
            GameMove: The next correct move.
        """

        self.validateMoveList()

        ret = None
        if len(self.nextMoveList) > 0:
            ret = self.nextMoveList.pop(0)

        return ret

    def validateMoveList(self):
        """Check if the `HexGameMoves` in the `nextMoveList` are still correct/valid.
        Remove all the incorrect moves.
        """
        # TODO implement validateMoveList


#################################################################
# CELL COMPLETIONS
#################################################################

def completeCell1(cell, activeDir):
    """Returns the cells to be set to `ACTIVE` and `BLANK` after solving the 1-Cell.

    Args:
        cell (HexCell): The 1-Cell that has been solved.
        activeDir: The direction of the 1-Cell's single ACTIVE side.

    Returns:
        [HexGameMove]: A list of Moves that sets the corresponding ACTIVE and BLANK states.
    """
    # First, set the ACTIVE side
    activeSide = cell.sides[activeDir]
    moves = [HexGameMove(activeSide.id, ACTIVE)]
    # Then get all the other sides of the 1-Cell and set them to BLANK
    allOtherSides = cell.getAllSidesExcept(activeSide)
    moves.extend([HexGameMove(side.id, BLANK) for side in allOtherSides])
    # Then get all the hanging limbs connected to the 1-Cell
    hangingLimbs = list(filter(lambda limb: not limb.isConnectedTo(activeSide), cell.getLimbs()))
    moves.extend([HexGameMove(hangingLimb.id, BLANK) for hangingLimb in hangingLimbs])

    return moves
