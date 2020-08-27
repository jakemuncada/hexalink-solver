"""Solver for HexGame."""

from side_status import SideStatus
from hex_dir import HexSideDir


class HexSolver:
    """A solver for HexGame."""

    def __init__(self, game):
        self.game = game
        self.nextMoveList = []
        self.processedSides = set()

        self.initialBoardInspection()

    def initialBoardInspection(self):
        """Inspect the board and register one-time obvious moves into the `nextMoveList`.

        One-time obvious moves are those that need to be checked only once,
        like the 5-and-5 adjacent cells, or the 1-and-5 adjacent cells, or zero-cells.
        """
        for cell in self.game.cells:
            if cell.reqSides == 0:
                # Remove all sides and limbs of zero-cells
                for cellSide in cell.sides:
                    self.addNextMove(cellSide, SideStatus.BLANK)
                for limb in cell.getLimbs():
                    self.addNextMove(limb, SideStatus.BLANK)

            if cell.reqSides == 1:
                for sideDir in HexSideDir:
                    adjCell = cell.adjCells[sideDir]
                    if adjCell is not None:
                        if adjCell.reqSides == 5:
                            # Boundary of 1-and-5 is ACTIVE
                            self.addNextMove(cell.sides[sideDir], SideStatus.ACTIVE)

                        if adjCell.reqSides == 1:
                            # Boundary of 1-and-1 is BLANK
                            self.addNextMove(cell.sides[sideDir], SideStatus.BLANK)

            if cell.reqSides == 5:
                for sideDir in HexSideDir:
                    adjCell = cell.adjCells[sideDir]
                    if adjCell is not None:
                        if adjCell.reqSides == 5:
                            # Boundary of 5-and-5 is ACTIVE, then cap the opposite ends
                            self.addNextMove(cell.sides[sideDir], SideStatus.ACTIVE)
                            caps = cell.getCap(sideDir.opposite()) + adjCell.getCap(sideDir)
                            self.addNextMoves(caps, SideStatus.ACTIVE)
                            # Also, the limbs of the cap should be BLANK
                            # TODO

    def addNextMove(self, side, newStatus):
        """Add a `HexGameMove` to the `nextMoveList`.
        Only `UNSET` sides can be added to the `nextMoveList`."""
        if side.isUnset() and newStatus != SideStatus.UNSET:
            move = HexGameMove(side.id, newStatus)
            self.nextMoveList.append(move)

    def addNextMoves(self, sides, newStatus):
        """Add multiple `HexGameMoves` to the `nextMoveList`."""
        for side in sides:
            self.addNextMove(side, newStatus)

    def getNextMove(self):
        """Get the next correct move.

        Returns:
            GameMove: The next correct move.
        """

        # Reset processed sides set
        self.processedSides = set()

        self.validateMoveList()

        ret = None
        if len(self.nextMoveList) > 0:
            ret = self.nextMoveList.pop()

        return ret

    def validateMoveList(self):
        """Check if the `HexGameMoves` in the `nextMoveList` are still correct/valid.
        Remove all the incorrect moves.
        """
        # TODO


class HexGameMove:
    """There are two kinds of moves: a PastMove and a FutureMove. PastMoves are moves
    that have been applied to the board. FutureMoves are moves that have not yet been applied.

    PastMoves have their previous status recorded, while FutureMoves don't have a `prevStatus`.
    """

    def __init__(self, sideId, newStatus, prevStatus=None):
        """Create a HexGameMove.

        Args:
            sideId (int): The id of the side.
            newStatus (SideStatus): The new status.
            prevStatus (SideStatus): The previous status. Optional.
                Only set when Move has been applied to board.
        """
        self.sideId = sideId
        self.newStatus = newStatus
        self.prevStatus = prevStatus
