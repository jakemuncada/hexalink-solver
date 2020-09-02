"""Solver for HexGame."""

from side_status import SideStatus
from hex_game_move import HexGameMove
from hex_dir import HexSideDir, HexVertexDir
from side_link import SideLink

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
        self.currMoveSequence = None

        self.initialBoardInspection()
        self.solveAll()

    def solveAll(self):
        """Solve the whole board."""
        while True:
            nextMove = self.getNextMove()
            if nextMove is None:
                break
            side = self.game.sides[nextMove.sideId]
            self.game.setSideStatus(side, nextMove.newStatus)
            self.inspectObviousVicinity(side)
            # print(f"Side {side} was set to {nextMove.newStatus}.")

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
                            polish = adjCell.getAllCellSidesConnectedToSide(boundary)
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

    def inspectEverything(self):
        """Inspect all cells and all sides."""
        for cell in self.game.reqCells:
            self.inspectObviousCell(cell)
        for side in self.game.sides:
            self.inspectObviousSide(side)

    def inspectObviousVicinity(self, side):
        """Inspect the connected sides and adjacent cells of a given `HexSide`
        for obvious clues. Adds the obvious moves to the `nextMoveList`."""
        # Inspect the sides that are connected to this side
        for connSide in side.getAllConnectedSides():
            self.inspectObviousSide(connSide)
        # Inspect the cells this side is connected to
        for adjCell in side.getAdjCells():
            self.inspectObviousCell(adjCell)
        # Inspect the cells for whom this side is a limb of
        for connCell in side.getConnectedCells():
            self.inspectObviousCell(connCell)

    ###########################################################################
    # INSPECT SIDE
    ###########################################################################

    def inspectObviousSide(self, side):
        """Inspect a given `HexSide` for obvious clues. Does not process non-`UNSET` sides."""

        # Do not process non-`UNSET` sides.
        if not side.isUnset():
            return

        self.inspectHangingSide(side)
        self.inspectConnectingToIntersection(side)
        self.inspectContinueActiveLink(side)
        self.inspectLoopMaker(side)

    def inspectHangingSide(self, side):
        """Set side to BLANK if it is hanging."""
        if side.isHanging():
            self.addNextMove(side, BLANK)

    def inspectConnectingToIntersection(self, side):
        """Set an UNSET side to BLANK if it is connecting to an intersection."""
        vtx1, vtx2 = side.endpoints
        if side.isUnset() and (vtx1.isIntersection() or vtx2.isIntersection()):
            self.addNextMove(side, BLANK)

    def inspectContinueActiveLink(self, side):
        """Set an UNSET side to ACTIVE if it is a continuation of an active link."""
        for connSide in side.getAllActiveConnectedSides():
            if side.isLinkedTo(connSide, ignoreStatus=True):
                self.addNextMove(side, ACTIVE)

    def inspectLoopMaker(self, side):
        """Inspect a side if setting it to ACTIVE will create a loop. If so, set it to BLANK."""

        # Only process UNSET sides
        if side.isUnset():

            # Get the connected sides on each endpoint
            connActiveSides1 = side.endpoints[0].getActiveSidesExcept(side.id)
            connActiveSides2 = side.endpoints[1].getActiveSidesExcept(side.id)

            # If both endpoints have an active side
            if len(connActiveSides1) > 0 and len(connActiveSides2) > 0:
                activeSide1 = connActiveSides1[0]
                activeSide2 = connActiveSides2[0]

                if activeSide1.colorIdx == activeSide2.colorIdx:
                    if SideLink.isSameLink(activeSide1, activeSide2):
                        self.addNextMove(side, BLANK)

    ###########################################################################
    # INSPECT CELL
    ###########################################################################

    def inspectObviousCell(self, cell):
        """Inspect a given cell for obvious clues.

        Some obvious clues include:
            ・If the cell already has the correct number of ACTIVE or BLANK sides.
        """
        if not cell.isFullySet():
            if cell.reqSides is not None:
                # If already has correct number of ACTIVE sides, set others to BLANK
                if cell.countActiveSides() == cell.reqSides:
                    self.addNextMoves(cell.getUnsetSides(), BLANK)

                # If already has correct number of BLANK sides, set others to ACTIVE
                elif cell.countBlankSides() == cell.requiredBlanks():
                    self.addNextMoves(cell.getUnsetSides(), ACTIVE)

                # Otherwise, check other clues
                else:
                    self.inspectSymmetrical3Cell(cell)
                    # self.inspect4CellGroupOpposite5Cell(cell)
                    self.inspectForBisectorOfRemainingTwo(cell)
                    self.inspectUnsetSideLinks(cell)
                    self.inspectTheoreticalBlanks(cell)

            # Then, check each side individually, even for cells that have no required sides.
            for side in cell.sides:
                if side.isUnset():
                    self.inspectObviousSide(side)

    def inspectForBisectorOfRemainingTwo(self, cell):
        """If the given cell only has one remaining requirement and has
        two adjacent `UNSET` sides, bisect these with an `ACTIVE` limb."""
        if cell.remainingReqs() == 1 and cell.countUnsetSides() == 2:
            unsetSides = cell.getUnsetSides()
            if unsetSides[0].isConnectedTo(unsetSides[1]):
                for vtxDir in HexVertexDir:
                    vtx = cell.vertices[vtxDir]
                    if unsetSides[0] in vtx.sides and unsetSides[1] in vtx.sides:
                        limb = cell.limbs[vtxDir]
                        if limb is not None:
                            self.addNextMove(limb, ACTIVE)
                        return

    def inspectSymmetrical3Cell(self, cell):
        """
        Inspects if the 3-Cell fits the symmetrical pattern, which is the case where
        all 3 active sides are linked.
        """
        if cell.reqSides == 3 and not cell.isFullySet():
            sideLinks = cell.getUnsetSideLinks()
            for sideLink in sideLinks:
                # If a SideLink with len of 3 exists,
                if len(sideLink) == 3:
                    # Get the limbs at the two endpoints
                    limb1 = cell.getLimbAt(sideLink.endpoints[0])
                    limb2 = cell.getLimbAt(sideLink.endpoints[1])
                    # Set the limb at its endpoints to ACTIVE
                    self.addNextMove(limb1, ACTIVE)
                    self.addNextMove(limb2, ACTIVE)
                    # Set all other limbs to BLANK
                    for limb in cell.getLimbs():
                        if limb != limb1 and limb != limb2:
                            self.addNextMove(limb, BLANK)

    # def inspect4CellGroupOpposite5Cell(self, fourCell):
    #     """
    #     Inspect a 4-Cell if it has an UNSET group opposite of a 5-Cell.
    #     If so, set that group to ACTIVE.
    #     """

    #     if fourCell.reqSides == 4 and not fourCell.isFullySet():
    #         for cellDir in HexSideDir:
    #             if fourCell.adjCell[cellDir].reqSides == 5:
    #                 fiveCell = fourCell.adjCell[cellDir]
    #                 links = fourCell.getUnsetSideLinks()
    #                 for link in links:
    #                     if len(link) > 2:
    #                         self.addNextMoves(link, ACTIVE)
    #                     elif len(link) == 2:
    #                         for side in link:

    def inspectUnsetSideLinks(self, cell):
        """
        Inspects the cell's side groups if there are deducible `ACTIVE` or `BLANK` groups.
        Does not process non-required cells.
        """

        # Don't process non-required cells
        if cell.reqSides is not None:
            unsetGroups = cell.getUnsetSideLinks()

            for group in unsetGroups:
                # Check if the group should be active
                if len(group) > cell.requiredBlanks() - cell.countBlankSides():
                    self.addNextMoves(group, ACTIVE)

                # Check if the group should be blank
                elif len(group) > cell.reqSides - cell.countActiveSides():
                    self.addNextMoves(group, BLANK)

    def inspectTheoreticalBlanks(self, cell):
        """
        Inspect the cell's theoretical blanks if they provide a clue.\n
        If enough blanks have been created, the remaining UNSET sides can be deduced to be ACTIVE.
        """

        if cell.reqSides is not None and not cell.isFullySet():
            # Get the number of theoretical blank sides
            theoreticalBlankCount, theoreticalSides = cell.getTheoreticalBlanks()

            if theoreticalBlankCount == cell.requiredBlanks():
                for side in cell.sides:
                    if side is not None and side.isUnset() and side not in theoreticalSides:
                        print(f"Theoretically active: {str(side)}")
                        self.addNextMove(side, ACTIVE)

    ###########################################################################
    # ADD NEXT MOVE
    ###########################################################################

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

    ###########################################################################
    # GET NEXT MOVE
    ###########################################################################

    def getNextMove(self):
        """Get the next correct move.

        Returns:
            GameMove: The next correct move.
        """

        ret = None
        if len(self.nextMoveList) > 0:
            ret = self.nextMoveList.pop(0)
        else:
            self.inspectEverything()
            ret = None if len(self.nextMoveList) == 0 else self.nextMoveList.pop(0)

        return ret


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
