"""HexGameMove file."""


class HexGameMove:
    """There are two kinds of moves: a PastMove and a FutureMove. PastMoves are moves
    that have been applied to the board. FutureMoves are moves that have not yet been applied.

    PastMoves have their previous status recorded, while FutureMoves don't have a `prevStatus`.
    """

    def __init__(self, sideId, newStatus, prevStatus, msg=None, fromSolver=False):
        """Create a HexGameMove.

        Args:
            sideId (int): The id of the side.
            newStatus (SideStatus): The new status.
            prevStatus (SideStatus): The previous status. Optional.
                Only set when Move has been applied to board.
            msg (string): An explanation of the move. Optional.
            fromSolver (bool): True if the move was created by the solver.
        """
        assert(newStatus is not None), "The new status cannot be None"
        assert(prevStatus is not None), "The previous status cannot be None"

        self.sideId = sideId
        self.newStatus = newStatus
        self.prevStatus = prevStatus
        self.msg = msg
        self.fromSolver = fromSolver

    def reverse(self):
        """Returns the reverse of this move."""
        return HexGameMove(self.sideId, self.prevStatus, self.newStatus, self.msg, self.fromSolver)

    def __eq__(self, other):
        return isinstance(other, HexGameMove) and \
            self.sideId == other.sideId and \
            self.newStatus == other.newStatus and \
            self.prevStatus == other.prevStatus
