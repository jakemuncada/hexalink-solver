"""Solver for HexGame."""

from side_status import SideStatus
from hex_game_move import HexGameMove
from hex_dir import HexSideDir
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
        # self.solveAll()

    def solveAll(self):
        """Solve the whole board."""
        while True:
            nextMove = self.getNextMove()
            if nextMove is None:
                break
            side = self.game.sides[nextMove.sideId]
            self.game.setSideStatus(nextMove)
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
                    self.addNextMove(cellSide, BLANK, "Remove sides of zero-cell.")
                for limb in cell.getLimbs():
                    self.addNextMove(limb, BLANK, "Remove limbs of zero-cell.")

            elif cell.reqSides == 1:
                for sideDir in HexSideDir:
                    adjCell = cell.adjCells[sideDir]
                    if adjCell is not None:
                        ###  1-AND-5  ###
                        if adjCell.reqSides == 5:
                            # Set boundary to ACTIVE
                            boundary = cell.sides[sideDir]
                            self.addNextMove(boundary, ACTIVE, "Set boundary of 1-and-5 to active.")
                            # Which means that the 1-Cell is solved, but it will be handled later

                        ###  1-AND-4  ###
                        elif adjCell.reqSides == 4:
                            # Remove the cap of 1
                            cap, limbs = cell.getCap(sideDir.opposite())
                            msg = "Remove cap of 1-Cell at direction opposite the adjacent 4-Cell."
                            self.addNextMoves(cap, BLANK, msg)
                            self.addNextMoves(limbs, BLANK, msg)

                        ###  1-AND-2  ###
                        elif adjCell.reqSides == 2:
                            # Set boundary to BLANK
                            msg = "Set the boundary of 1-and-2 to blank."
                            self.addNextMove(cell.sides[sideDir], BLANK, msg)

                        ###  1-AND-1  ###
                        elif adjCell.reqSides == 1:
                            # Set boundary to BLANK
                            msg = "Set the boundary of 1-and-1 to blank."
                            self.addNextMove(cell.sides[sideDir], BLANK, msg)

            elif cell.reqSides == 5:
                for sideDir in HexSideDir:
                    adjCell = cell.adjCells[sideDir]
                    if adjCell is not None:
                        ###  5-AND-5  ###
                        if adjCell.reqSides == 5:
                            # Set boundary to ACTIVE, then cap the opposite ends,
                            # the remove the limbs of the cap
                            msg = "Set boundary of 5-and-5 to active."
                            self.addNextMove(cell.sides[sideDir], ACTIVE, msg)
                            cap1, limbs1 = cell.getCap(sideDir.opposite())
                            cap2, limbs2 = adjCell.getCap(sideDir)
                            msg = "Activate the cap of both 5-and-5 cells."
                            self.addNextMoves(cap1 + cap2, ACTIVE, msg)
                            msg = "Remove dead limbs of both 5-and-5 cells."
                            self.addNextMoves(limbs1 + limbs2, BLANK, msg)

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
            self.addNextMove(side, BLANK, "Remove hanging side.")

    def inspectConnectingToIntersection(self, side):
        """Set an UNSET side to BLANK if it is connecting to an intersection."""
        vtx1, vtx2 = side.endpoints
        if side.isUnset() and (vtx1.isIntersection() or vtx2.isIntersection()):
            self.addNextMove(side, BLANK, "Remove side connecting to intersection.")

    def inspectContinueActiveLink(self, side):
        """Set an UNSET side to ACTIVE if it is a continuation of an active link."""
        for connSide in side.getAllActiveConnectedSides():
            if side.isLinkedTo(connSide, ignoreStatus=True):
                self.addNextMove(side, ACTIVE, "Activate the link continuation.")

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
                        self.addNextMove(side, BLANK, "Remove link which creates a loop.")

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
                    msg = "Cell already has correct number of active sides, \
                        so remove the other unset sides."
                    self.addNextMoves(cell.getUnsetSides(), BLANK, msg)

                # If already has correct number of BLANK sides, set others to ACTIVE
                elif cell.countBlankSides() == cell.requiredBlanks():
                    msg = "Cell already has enough blank sides, so activate the other unset sides."
                    self.addNextMoves(cell.getUnsetSides(), ACTIVE, msg)

                # Otherwise, check other clues
                else:
                    self.inspectSymmetrical3Cell(cell)
                    self.inspectUnsetSideLinks(cell)
                    self.inspectTheoreticals(cell)
                    self.inspectClosedOff5Cell(cell)
                    self.inspectOpen5Cell(cell)

            # Then, check each side individually, even for cells that have no required sides.
            for side in cell.sides:
                if side.isUnset():
                    self.inspectObviousSide(side)

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
                    msg = "Set the limbs at endpoints of symmetrical 3-Cell to active."
                    self.addNextMove(limb1, ACTIVE, msg)
                    self.addNextMove(limb2, ACTIVE, msg)
                    # Set all other limbs to BLANK
                    for limb in cell.getLimbs():
                        if limb != limb1 and limb != limb2:
                            msg = "Remove all other limbs of symmetrical 3-Cell."
                            self.addNextMove(limb, BLANK, msg)

    def inspectUnsetSideLinks(self, cell):
        """
        Inspects the cell's side groups if there are deducible `ACTIVE` or `BLANK` groups.
        Does not process non-required cells.
        """

        # Don't process non-required cells
        if cell.reqSides is not None and not cell.isFullySet():
            unsetGroups = cell.getUnsetSideLinks()

            # Get the actual count and the theoretical count of ACTIVE and BLANK sides
            actualActiveCount = cell.countActiveSides()
            actualBlankCount = cell.countBlankSides()
            theoreticalCount, theoreticalSides = cell.getTheoreticalBlanks()
            totalBlankCount = theoreticalCount + actualBlankCount
            totalActiveCount = theoreticalCount + actualActiveCount

            for group in unsetGroups:
                groupSize = len(group)

                # Check if the group should be active
                if groupSize > cell.requiredBlanks() - actualBlankCount:
                    self.addNextMoves(group, ACTIVE, "Side group should be active.")

                # Check if the group should be blank
                elif groupSize > cell.reqSides - actualActiveCount:
                    self.addNextMoves(group, BLANK, "Side group should be blank.")

                # # Check if all member sides of the group are not part of the theoretical sides
                # elif all(side not in theoreticalSides for side in group):
                #     if groupSize > 1:
                #         if groupSize > cell.requiredBlanks() - totalBlankCount:
                #             self.addNextMoves(group, ACTIVE, "Side group should be active.")
                #         elif groupSize > cell.reqSides - totalActiveCount:
                #             self.addNextMoves(group, BLANK, "Side group should be blank.")

    def inspectTheoreticals(self, cell):
        """
        Inspect the cell's theoretical blanks and theoretical actives if they provide a clue.\n
        If enough BLANK sides have been deduced, the remaining UNSET sides can be set to ACTIVE.\n
        If enough ACTIVE sides have been deduced, the remaining UNSET sides can be set to BLANK.
        """

        if cell.reqSides is not None and not cell.isFullySet():
            # Get the number of actual blank sides and actual active sides
            actualBlankCount = cell.countBlankSides()
            actualActiveCount = cell.countActiveSides()
            setSidesCount = actualActiveCount + actualBlankCount

            theoreticalCount, theoreticalSides = cell.getTheoreticalBlanks()
            theoreticalBlankCount = theoreticalCount
            theoreticalActiveCount = theoreticalCount

            # If we have enough blanks, the unsure sides are deduced to be ACTIVE
            if theoreticalBlankCount + actualBlankCount == cell.requiredBlanks():
                for side in cell.sides:
                    if side is not None and side.isUnset() and side not in theoreticalSides:
                        msg = "Theoretical blanks plus actual blanks are enough. " + \
                            "Set other sides to active."
                        self.addNextMove(side, ACTIVE, msg)

            # If we have enough actives, the unsure sides are deduced to be BLANK
            if theoreticalActiveCount + actualActiveCount == cell.reqSides:
                for side in cell.sides:
                    if side is not None and side.isUnset() and side not in theoreticalSides:
                        msg = "Theoretical actives plus actual actives are enough. " + \
                            "Set other sides to blank."
                        self.addNextMove(side, BLANK, msg)

            # If we need just 1 more active side
            elif theoreticalActiveCount + actualActiveCount == cell.reqSides - 1:
                # If there are only 2 remaining unsure sides
                if len(theoreticalSides) + setSidesCount == len(cell.sides) - 2:
                    # Check the remaining sides
                    remainingUnsureDirs = []
                    remainingUnsureSides = []
                    for sideDir in HexSideDir:
                        side = cell.sides[sideDir]
                        if side is not None and side.isUnset() and side not in theoreticalSides:
                            remainingUnsureDirs.append(sideDir)
                            remainingUnsureSides.append(side)

                    assert(len(remainingUnsureSides) == 2), \
                        "Expected only 2 remaining unsure sides."

                    # And if they are adjacent to each other, set the bisecting limb to ACTIVE
                    if remainingUnsureDirs[0].isAdjacent(remainingUnsureDirs[1]):
                        vtx = remainingUnsureSides[0].getConnectionVertex(
                            remainingUnsureSides[1])
                        limb = cell.getLimbAt(vtx)
                        self.addNextMove(limb, ACTIVE, "Bisect the remaining 2 unsure sides.")

    def inspectClosedOff5Cell(self, cell):
        """
        Inspect a 5-Cell if it is valid to close off its adjacent cells.

        A 5-Cell "closes off" an adjacent cell when all 3 sides
        connected to the adjacent cell are ACTIVE.
        """

        if cell.reqSides == 5 and not cell.isFullySet():

            def isValidToCloseOff(adjCell, sideDir):
                """Returns true if the given cell (the cell adjacent to the 5-Cell)
                is fine with being closed off."""

                # If the adjCell has no required sides, then it is okay to close this off
                if adjCell.reqSides is None:
                    return True

                countBlank = adjCell.countBlankSides()

                # The side bordering the adjCell and the 5-Cell (will become active)
                borderSide = adjCell.sides[sideDir]

                # The other sides of the adjCell that will become blank
                otherSides = adjCell.getAllCellSidesConnectedToSide(borderSide)
                for otherSide in otherSides:
                    # If the otherSide is already active, it is invalid to close off this adjCell.
                    if otherSide.isActive():
                        return False

                    if otherSide.isUnset():
                        countBlank += 1

                        # Consider the linked sides
                        # (the link is sure to be UNSET because otherSide is UNSET)
                        linkedSides = otherSide.getAllLinkedSides()
                        for linkedSide in linkedSides:
                            if linkedSide in adjCell.sides:
                                countBlank += 1

                # If we have exceeded the number of required blank sides
                if countBlank > adjCell.requiredBlanks():
                    return False

                return True

            for sideDir in HexSideDir:
                adjCell = cell.adjCells[sideDir]
                if adjCell is not None:
                    if not isValidToCloseOff(adjCell, sideDir.opposite()):
                        cap, limbs = cell.getCap(sideDir.opposite())
                        msg = f"The 5-Cell cannot close off the {str(sideDir)} direction."
                        self.addNextMoves(cap, ACTIVE, msg)
                        self.addNextMoves(limbs, BLANK, msg)

    def inspectOpen5Cell(self, cell):
        """
        Inspect a 5-Cell if it is valid to set a side to BLANK.

        Checks if the cell adjacent to the 5-Cell in the direction of the BLANK
        is still valid after gaining two ACTIVE sides.
        """

        if cell.reqSides == 5 and not cell.isFullySet():

            def isValidToOpen(adjCell, sideDir):
                """Returns true if the given cell (the cell adjacent to the 5-Cell)
                is fine with being opened to the 5-Cell."""

                # If the adjCell has no required sides, then it is valid
                if adjCell.reqSides is None:
                    return True

                countActive = adjCell.countActiveSides()

                # The side bordering the adjCell and the 5-Cell (will become blank).
                # If it is already active, then obviously it cannot be opened.
                borderSide = adjCell.sides[sideDir]
                if borderSide.isActive():
                    return False

                # The other sides of the adjCell that will become active
                otherSides = adjCell.getAllCellSidesConnectedToSide(borderSide)
                for otherSide in otherSides:
                    # If the otherSide is already blank, it is invalid to open to this adjCell.
                    if otherSide.isBlank():
                        return False

                    if otherSide.isUnset():
                        countActive += 1

                        # Consider the linked sides
                        # (the link is sure to be UNSET because otherSide is UNSET)
                        linkedSides = otherSide.getAllLinkedSides()
                        for linkedSide in linkedSides:
                            if linkedSide in adjCell.sides:
                                countActive += 1

                # If we have exceeded the number of required active sides
                if countActive > adjCell.reqSides:
                    return False

                return True

            for sideDir in HexSideDir:
                adjCell = cell.adjCells[sideDir]
                if adjCell is not None:
                    if not isValidToOpen(adjCell, sideDir.opposite()):
                        side = cell.sides[sideDir]
                        msg = f"The 5-Cell cannot be open in the {str(sideDir)} direction."
                        self.addNextMove(side, ACTIVE, msg)

    ###########################################################################
    # ADD NEXT MOVE
    ###########################################################################

    def addNextMove(self, side, newStatus, msg):
        """Add a `HexGameMove` to the `nextMoveList`.
        Only `UNSET` sides can be added to the `nextMoveList`.

        Args:
            side (HexSide): The side to be set.
            newStatus (SideStatus): The new status of the side.
            msg (string): The explanation message of the move.
        """
        if side is not None and side.isUnset() and newStatus != UNSET and \
                side.id not in self.processedSideIds:
            move = HexGameMove(side.id, newStatus, UNSET, msg=msg, fromSolver=True)
            self.nextMoveList.append(move)
            self.processedSideIds.add(side.id)

    def addNextMoves(self, sides, newStatus, msg):
        """Add multiple `HexGameMoves` to the `nextMoveList`.
        Uses `addNextMove(side, newStatus)` under the hood.

        Args:
            sides ([HexSide]): The list of sides to be set.
            newStatus (SideStatus): The new status of all the sides in the list.
            msg (string): The explanation message of the moves.
        """
        for side in sides:
            self.addNextMove(side, newStatus, msg)

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

        def getFromMoveList():
            if len(self.nextMoveList) > 0:
                return self.nextMoveList.pop(0)
            return None

        # Get next move from list, but disregard if the side is not UNSET
        while True:
            nextMove = getFromMoveList()
            if nextMove is None:
                break
            if self.game.sides[nextMove.sideId].isUnset():
                return nextMove

        # If there are no next moves,
        # check everything and try to get next move again
        if nextMove is None:
            self.inspectEverything()
            return getFromMoveList()

        return None
