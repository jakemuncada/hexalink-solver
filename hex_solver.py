"""Solver for HexGame."""

from side_status import SideStatus
from hex_game_move import HexGameMove, MovePriority
from cell_faction import CellFaction
from hex_dir import HexSideDir
from side_link import SideLink
from helpers import measureStart, measureEnd

# Define SideStatus members
BLANK = SideStatus.BLANK
ACTIVE = SideStatus.ACTIVE
UNSET = SideStatus.UNSET

# Define MovePriority members
HIGHEST = MovePriority.HIGHEST
HIGH = MovePriority.HIGH
NORMAL = MovePriority.NORMAL
LOW = MovePriority.LOW
LOWEST = MovePriority.LOWEST


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

        print("Solving the whole board...")
        measureStart("SolveAll")
        countSidesSet = 0

        while True:
            nextMove = self.getNextMove(doSort=False)
            if nextMove is None:
                break
            countSidesSet += 1
            side = self.game.sides[nextMove.sideId]
            self.game.setSideStatus(nextMove)
            self.inspectObviousVicinity(side)

        perfTime = measureEnd("SolveAll")
        print("Number of sides set:", countSidesSet)
        print("Time to solve: {:.3f}ms".format(perfTime))

    def initialBoardInspection(self):
        """Inspect the board and register one-time obvious moves into the `nextMoveList`.

        One-time obvious moves are those that need to be checked only once,
        like the 5-and-5 adjacent cells, or the 1-and-5 adjacent cells, or zero-cells.
        """
        for cell in self.game.reqCells:
            if cell.reqSides == 0:
                # Remove all sides and limbs of zero-cells
                for cellSide in cell.sides:
                    self.addNextMove(cellSide, BLANK, HIGH, "Remove sides of zero-cell.")
                for limb in cell.getLimbs():
                    self.addNextMove(limb, BLANK, HIGH, "Remove limbs of zero-cell.")

            elif cell.reqSides == 1:
                for sideDir in HexSideDir:
                    adjCell = cell.adjCells[sideDir]
                    if adjCell is not None:
                        ###  1-AND-5  ###
                        if adjCell.reqSides == 5:
                            # Set boundary to ACTIVE
                            boundary = cell.sides[sideDir]
                            msg = "Set boundary of 1-and-5 to active."
                            self.addNextMove(boundary, ACTIVE, HIGH, msg)
                            # Which means that the 1-Cell is solved, but it will be handled later

                        ###  1-AND-4  ###
                        elif adjCell.reqSides == 4:
                            # Remove the cap of 1
                            cap, limbs = cell.getCap(sideDir.opposite())
                            msg = "Remove cap of 1-Cell at direction opposite the adjacent 4-Cell."
                            self.addNextMoves(cap, BLANK, HIGH, msg)
                            self.addNextMoves(limbs, BLANK, HIGH, msg)

                        ###  1-AND-2  ###
                        elif adjCell.reqSides == 2:
                            # Set boundary to BLANK
                            msg = "Set the boundary of 1-and-2 to blank."
                            self.addNextMove(cell.sides[sideDir], BLANK, HIGH, msg)

                        ###  1-AND-1  ###
                        elif adjCell.reqSides == 1:
                            # Set boundary to BLANK
                            msg = "Set the boundary of 1-and-1 to blank."
                            self.addNextMove(cell.sides[sideDir], BLANK, HIGH, msg)

            elif cell.reqSides == 5:
                for sideDir in HexSideDir:
                    adjCell = cell.adjCells[sideDir]
                    if adjCell is not None:
                        ###  5-AND-5  ###
                        if adjCell.reqSides == 5:
                            # Set boundary to ACTIVE, then cap the opposite ends,
                            # the remove the limbs of the cap
                            msg = "Set boundary of 5-and-5 to active."
                            self.addNextMove(cell.sides[sideDir], ACTIVE, HIGH, msg)
                            cap1, limbs1 = cell.getCap(sideDir.opposite())
                            cap2, limbs2 = adjCell.getCap(sideDir)
                            msg = "Activate the cap of both 5-and-5 cells."
                            self.addNextMoves(cap1 + cap2, ACTIVE, HIGH, msg)
                            msg = "Remove dead limbs of both 5-and-5 cells."
                            self.addNextMoves(limbs1 + limbs2, BLANK, HIGH, msg)

    def inspectEverything(self):
        """Inspect all cells and all sides."""
        for cell in self.game.reqCells:
            self.inspectObviousCellClues(cell)
            self.inspectLessObviousCellClues(cell)

        for side in self.game.sides:
            self.inspectObviousSideClues(side)

        # If there are still no moves
        if len(self.nextMoveList) == 0:
            self.inspectFactions()

    def inspectObviousVicinity(self, side):
        """Inspect the connected sides and adjacent cells of a given `HexSide`
        for obvious clues. Adds the obvious moves to the `nextMoveList`."""
        # Inspect the sides that are connected to this side
        for connSide in side.getAllConnectedSides():
            self.inspectObviousSideClues(connSide)
        # Inspect the cells this side is connected to
        for adjCell in side.getAdjCells():
            self.inspectObviousCellClues(adjCell)
        # Inspect the cells for whom this side is a limb of
        for connCell in side.getConnectedCells():
            self.inspectObviousCellClues(connCell)

    ###########################################################################
    # INSPECT SIDE
    ###########################################################################

    def inspectObviousSideClues(self, side):
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
            # Also include the continuation of its link, if any
            hangingLink = SideLink.fromSide(side)
            msg = "Remove hanging side."
            self.addNextMoves(hangingLink, BLANK, HIGHEST, msg=msg)

    def inspectConnectingToIntersection(self, side):
        """Set an UNSET side to BLANK if it is connecting to an intersection."""
        vtx1, vtx2 = side.endpoints
        if side.isUnset() and (vtx1.isIntersection() or vtx2.isIntersection()):
            # Also include the continuation of its link, if any
            hangingLink = SideLink.fromSide(side)
            msg = "Remove side connecting to intersection."
            self.addNextMoves(hangingLink, BLANK, HIGHEST, msg=msg)

    def inspectContinueActiveLink(self, side):
        """Set an UNSET side to ACTIVE if it is a continuation of an active link."""
        for connSide in side.getAllActiveConnectedSides():
            if side.isLinkedTo(connSide, ignoreStatus=True):
                fullLink = SideLink.fromSide(side)
                msg = "Activate the link continuation."
                self.addNextMoves(fullLink, ACTIVE, HIGHEST, msg=msg)

    def inspectLoopMaker(self, side):
        """Inspect a side if setting it to ACTIVE will create a loop. If so, set it to BLANK."""

        # Only process UNSET sides
        if side.isUnset():

            # Get the whole link
            link = SideLink.fromSide(side)

            # Get the connected sides on each endpoint
            connActiveSides1 = link.endpoints[0].getActiveSidesExcept(link.endLink[0])
            connActiveSides2 = link.endpoints[1].getActiveSidesExcept(link.endLink[1])

            # If both endpoints have an active side
            if len(connActiveSides1) > 0 and len(connActiveSides2) > 0:
                activeSide1 = connActiveSides1[0]
                activeSide2 = connActiveSides2[0]

                if activeSide1.colorIdx == activeSide2.colorIdx:
                    if SideLink.isSameLink(activeSide1, activeSide2):
                        self.addNextMove(side, BLANK, LOW, "Remove link which creates a loop.")

    ###########################################################################
    # INSPECT CELL
    ###########################################################################

    def inspectObviousCellClues(self, cell):
        """Inspect a given cell for obvious clues."""
        if not cell.isFullySet():
            if cell.reqSides is not None:
                # If already has correct number of ACTIVE sides, set others to BLANK
                if cell.countActiveSides() == cell.reqSides:
                    msg = "Cell already has correct number of active sides, " + \
                        "so remove the other unset sides."
                    self.addNextMoves(cell.getUnsetSides(), BLANK, HIGHEST, msg)

                # If already has correct number of BLANK sides, set others to ACTIVE
                elif cell.countBlankSides() == cell.requiredBlanks():
                    msg = "Cell already has enough blank sides, so activate the other unset sides."
                    self.addNextMoves(cell.getUnsetSides(), ACTIVE, HIGHEST, msg)

            # Then, check each side individually, even for cells that have no required sides.
            for side in cell.sides:
                if side.isUnset():
                    self.inspectObviousSideClues(side)

            # Also, check each limb
            for side in cell.limbs:
                if side is not None and side.isUnset():
                    self.inspectObviousSideClues(side)

    def inspectLessObviousCellClues(self, cell):
        """Inspect a given cell for less obvious clues."""
        if not cell.isFullySet():
            if len(self.nextMoveList) == 0:
                self.inspectSymmetrical3Cell(cell)
            if len(self.nextMoveList) == 0:
                self.inspectUnsetSideLinks(cell)
            if len(self.nextMoveList) == 0:
                self.inspectTheoreticals(cell)
            if len(self.nextMoveList) == 0:
                self.inspectClosedOff5Cell(cell)
            if len(self.nextMoveList) == 0:
                self.inspectOpen5Cell(cell)
            if len(self.nextMoveList) == 0:
                self.inspectRemaining2Group(cell)

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
                    self.addNextMove(limb1, ACTIVE, LOW, msg)
                    self.addNextMove(limb2, ACTIVE, LOW, msg)
                    # Set all other limbs to BLANK
                    for limb in cell.getLimbs():
                        if limb != limb1 and limb != limb2:
                            msg = "Remove all other limbs of symmetrical 3-Cell."
                            self.addNextMove(limb, BLANK, LOW, msg)

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
            theoreticalCount, theoreticalSidesList = cell.getTheoreticalBlanks()
            totalBlankCount = theoreticalCount + actualBlankCount
            totalActiveCount = theoreticalCount + actualActiveCount

            for theoreticalSides in theoreticalSidesList:

                for group in unsetGroups:
                    groupSize = len(group)

                    # Check if the group should be active
                    if groupSize > cell.requiredBlanks() - actualBlankCount:
                        msg = "Side group (size: {}) of {}-Cell should be active.".format(
                            groupSize, cell.reqSides)
                        self.addNextMoves(group, ACTIVE, NORMAL, msg)

                    # Check if the group should be blank
                    elif groupSize > cell.reqSides - actualActiveCount:
                        msg = "Side group (size: {}) of {}-Cell should be blank.".format(
                            groupSize, cell.reqSides)
                        self.addNextMoves(group, BLANK, NORMAL, msg)

                    # Check if all member sides of the group are not part of the theoretical sides
                    elif all(side not in theoreticalSides for side in group):
                        if groupSize > 1:
                            # Check the number of blanks/actives while considering theoreticals
                            if groupSize > cell.requiredBlanks() - totalBlankCount:
                                msg = f"Side group of {cell.reqSides}-Cell should be active " + \
                                    "(using theoretical clues)."
                                self.addNextMoves(group, ACTIVE, NORMAL, msg)
                            elif groupSize > cell.reqSides - totalActiveCount:
                                msg = f"Side group of {cell.reqSides}-Cell should be blank " + \
                                    "(using theoretical clues)."
                                self.addNextMoves(group, BLANK, NORMAL, msg)

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

            theoreticalCount, theoreticalSidesList = cell.getTheoreticalBlanks()
            theoreticalBlankCount = theoreticalCount
            theoreticalActiveCount = theoreticalCount

            for theoreticalSides in theoreticalSidesList:

                # If we have enough blanks, the unsure sides are deduced to be ACTIVE
                if theoreticalBlankCount + actualBlankCount == cell.requiredBlanks():
                    for side in cell.sides:
                        if side is not None and side.isUnset() and side not in theoreticalSides:
                            msg = "Theoretical blanks plus actual blanks are enough. " + \
                                "Set other sides to active."
                            self.addNextMove(side, ACTIVE, LOW, msg)

                # If we have enough actives, the unsure sides are deduced to be BLANK
                if theoreticalActiveCount + actualActiveCount == cell.reqSides:
                    for side in cell.sides:
                        if side is not None and side.isUnset() and side not in theoreticalSides:
                            msg = "Theoretical actives plus actual actives are enough. " + \
                                "Set other sides to blank."
                            self.addNextMove(side, BLANK, LOW, msg)

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
                            self.addNextMove(limb, ACTIVE, LOW,
                                             "Bisect the remaining 2 unsure sides.")

    def inspectRemaining2Group(self, cell):
        """
        Inspect a cell if it only need 2 more active sides. Check if the remaining unset sides
        should be grouped into a 2-link SideLink.
        """

        # If the cell needs 2 more active sides
        if cell.remainingReqs() == 2:

            unsetSideLinks = cell.getUnsetSideLinks()

            links1 = []  # Links with size 1
            links2 = []  # Links with size 2
            otherLinks = []  # Links with size > 2

            for sideLink in unsetSideLinks:
                if len(sideLink) == 1:
                    links1.append(sideLink)
                elif len(sideLink) == 2:
                    links2.append(sideLink)
                else:
                    otherLinks.append(sideLink)

            # If there are of links whose size is greater than 2, they should be blank
            if len(otherLinks) > 0:
                for link in otherLinks:
                    msg = f"Side group of {cell.reqSides}-Cell should be blank " + \
                        "(using theoretical clues)."
                    self.addNextMoves(link, BLANK, NORMAL, msg)

            # If there are two links with size of 1 and they are adjacent each other,
            # they should be connected.
            elif len(links1) == 2 and links1[0].getConnectionVertex(links1[1]) is not None:
                vertex = links1[0].getConnectionVertex(links1[1])
                limb = cell.getLimbAt(vertex)
                msg = "Remaining required sides of {}-Cell is 2, so fuse the two together.".format(
                    cell.reqSides)
                self.addNextMove(limb, BLANK, LOW, msg)

            # If there are two links with size of 2 and they are adjacent each other,
            # they should be bisected
            elif len(links2) == 2 and links2[0].getConnectionVertex(links2[1]) is not None:
                vertex = links2[0].getConnectionVertex(links2[1])
                limb = cell.getLimbAt(vertex)
                msg = "Remaining required sides of {}-Cell is 2, so bisect the two links.".format(
                    cell.reqSides)
                self.addNextMove(limb, ACTIVE, LOW, msg)

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
                        self.addNextMoves(cap, ACTIVE, LOW, msg)
                        self.addNextMoves(limbs, BLANK, LOW, msg)

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
                        self.addNextMove(side, ACTIVE, LOW, msg)

    ###########################################################################
    # FACTIONS
    ###########################################################################

    def inspectFactions(self):
        """Inspect each cell's faction for clues."""

        self.recalculateFactions()

        for cell in self.game.cells:
            # If faction is unknown, do nothing
            if not cell.isFactionUnknown():
                # Look at each side
                for sideDir in HexSideDir:
                    side = cell.sides[sideDir]
                    # If this side is unset, try to see if we can find out using faction clues
                    if side.isUnset():
                        adjCell = cell.adjCells[sideDir]
                        sideFaction = CellFaction.OUTSIDE if adjCell is None else adjCell.faction
                        # If own faction and the adjacent cell's faction is different,
                        # set the side to ACTIVE
                        if sideFaction != CellFaction.UNKNOWN and sideFaction != cell.faction:
                            msg = "The cell at {} is {} so we separate it from {}.".format(
                                str(cell), str(cell.faction),
                                "the outside" if adjCell is None else str(adjCell))
                            self.addNextMove(side, ACTIVE, LOWEST, msg)
                        # If own faction and the adjacent cell's faction is the same,
                        # set the side to BLANK
                        elif sideFaction != CellFaction.UNKNOWN and sideFaction == cell.faction:
                            msg = "The cell at {} is {} so we merge it with {}.".format(
                                str(cell), str(cell.faction),
                                "the outside" if adjCell is None else str(adjCell))
                            self.addNextMove(side, BLANK, LOWEST, msg)

    def resetFactions(self):
        """Reset all the factions to None."""
        for cell in self.game.cells:
            cell.setFactionUnknown()

    def recalculateFactions(self):
        """Calculate each cell's faction."""

        self.resetFactions()

        def setFaction(cell, newFaction):
            """Sets the faction of the given cell, then recursively inform its
            adjacent cells to update."""

            if cell.faction != newFaction and cell.isFactionUnknown():
                cell.setFaction(newFaction)

                # Notify its adjacent cells
                for sideDir in HexSideDir:
                    adjCell = cell.adjCells[sideDir]
                    # If the side is BLANK, set the adjacent cell to be the same
                    if cell.sides[sideDir].isBlank() and adjCell is not None:
                        setFaction(adjCell, newFaction)
                    # If the side is ACTIVE, set the adjacent cell to be the opposite
                    if cell.sides[sideDir].isActive() and adjCell is not None:
                        setFaction(adjCell, newFaction.opposite())

        def processEdgeCell(cell):
            """Given a cell on the edge of the game board,
            determine if it has an outer edge that is BLANK or ACTIVE.
            If so, we know its faction."""

            # If cell's faction is not unknown, it has already been processed
            # so do nothing else.
            if not cell.isFactionUnknown():
                return

            for sideDir in HexSideDir:
                adjCell = cell.adjCells[sideDir]
                # If adjacent cell is None, it is the outside of the board
                if adjCell is None:
                    # If the side to the outside is BLANK, the cell is OUTSIDE
                    if cell.sides[sideDir].isBlank():
                        setFaction(cell, CellFaction.OUTSIDE)
                    # If the side to the outside is ACTIVE, the cell is INSIDE
                    elif cell.sides[sideDir].isActive():
                        setFaction(cell, CellFaction.INSIDE)
                elif not adjCell.isFactionUnknown():
                    if cell.sides[sideDir].isBlank():
                        setFaction(cell, adjCell.faction)
                    elif cell.sides[sideDir].isActive():
                        setFaction(cell, adjCell.faction.opposite())

        rows = self.game.rows
        for row in range(rows):
            rowArr = self.game.board[row]

            if row == 0 or row == rows - 1:
                for cell in rowArr:
                    processEdgeCell(cell)
            else:
                processEdgeCell(rowArr[0])
                processEdgeCell(rowArr[len(rowArr) - 1])

    ###########################################################################
    # ADD NEXT MOVE
    ###########################################################################

    def addNextMove(self, side, newStatus, priority, msg):
        """Add a `HexGameMove` to the `nextMoveList`.
        Only `UNSET` sides can be added to the `nextMoveList`.

        Args:
            side (HexSide): The side to be set.
            newStatus (SideStatus): The new status of the side.
            priority (MovePriority): The priority of the move.
            msg (string): The explanation message of the move.
        """
        if side is not None and side.isUnset() and newStatus != UNSET and \
                side.id not in self.processedSideIds:
            move = HexGameMove(side.id, newStatus, UNSET, priority, msg=msg, fromSolver=True)
            self.nextMoveList.append(move)
            self.processedSideIds.add(side.id)

    def addNextMoves(self, sides, newStatus, priority, msg):
        """Add multiple `HexGameMoves` to the `nextMoveList`.
        Uses `addNextMove(side, newStatus)` under the hood.

        Args:
            sides ([HexSide]): The list of sides to be set.
            newStatus (SideStatus): The new status of all the sides in the list.
            priority (MovePriority): The priority of the move.
            msg (string): The explanation message of the moves.
        """
        for side in sides:
            self.addNextMove(side, newStatus, priority, msg)

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

    def getNextMove(self, prevCoords=None, doSort=True):
        """
        Get the next correct move.

        Args:
            doSort (bool): If true, sort the list before returning the next move.
            prevCoords (Point): The coordinates of the previous move.

        Returns:
            GameMove: The next correct move.
        """

        def sortKey(move):
            sideCoords = self.game.sides[move.sideId].midpoint
            dist = sideCoords.dist(prevCoords) if prevCoords is not None else 1
            return (move.priority, dist)

        def getFromMoveList():
            if len(self.nextMoveList) > 0:
                if doSort:
                    self.nextMoveList.sort(key=sortKey)
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
