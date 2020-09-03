"""The Hexagon Slitherlink Game"""


from hex_side import HexSide
from side_status import SideStatus
from hex_game_move import HexGameMove
from hex_dir import HexSideDir, HexVertexDir
from hex_cell import HexCell
from hex_vertex import HexVertex
from point import Point

import helpers as helper


class HexGame:
    """The Hexagon Slitherlink class."""

    def __init__(self, center, cellSideWidth, rows, cellDataStr=None):
        """Create a HexGame.

        Args:
            center (2-tuple): The center coordinates of the board.
            cellSideWidth (int): The width of the side of the cell.
            rows (int): The number of rows of the board. Must be an odd number greater than 3.
            cellDataStr (string): The string containing the required sides of each cell. Optional.

        Raises:
            ValueError: If the rows or cell data is invalid.
        """

        self.rows = rows
        self.cellSideWidth = cellSideWidth
        self.cellDataStr = cellDataStr
        self.center = Point(center)
        self.moveHistory = []

        # Validate and initialize the data
        self.validateInputData()
        self.init()

    def init(self):
        """Initialize the board. Can be called again to reset board."""
        self.midRow = self.rows // 2
        self.board = [[] for _ in range(self.rows)]
        self.cells = []
        self.reqCells = []  # Cells that have a required number of sides
        self.sides = []
        self.vertices = []

        # For displaying the clicked cell coordinates
        self.clickedCell = None

        # Populate the cells
        cellIdx = 0
        for row in range(self.rows):
            for col in range(self.getNumOfCols(row)):
                reqSides = self.cellDataStr[cellIdx] if self.cellDataStr is not None else "."
                reqSides = None if reqSides == "." else int(reqSides)
                cell = HexCell(row, col, self.cellSideWidth, reqSides)
                cell.calcCoords(self.center, self.rows)
                self.board[row].append(cell)
                cellIdx += 1
                # Append the cells to the list
                self.cells.append(cell)
                if reqSides is not None:
                    self.reqCells.append(cell)

        self._registerAdjacentCells()
        self._registerVertices()
        self._registerSides()
        self._registerLimbs()

    def _registerAdjacentCells(self):
        """Register the adjacent cells of each cell."""
        for cell in self.cells:
            for sideDir in HexSideDir:
                adjCell = self.getAdjCellAtDir(cell, sideDir)
                cell.adjCells[sideDir] = adjCell

    def _registerVertices(self):
        """Register the vertices of each cell."""

        def registerVertexAtNeighbor(neighborCell, direction, vertex):
            if neighborCell is not None:
                neighborCell.vertices[direction] = vertex

        for cell in self.cells:
            for vtxDir in HexVertexDir:
                if cell.vertices[vtxDir] is None:
                    vertex = HexVertex(len(self.vertices))
                    vertex.calcCoords(cell.center, cell.sideLength, vtxDir)
                    cell.vertices[vtxDir] = vertex

                    # Add this vertex to the list of all vertices
                    self.vertices.append(vertex)

                    # Also register this vertex to the neighbors
                    if vtxDir == HexVertexDir.T:
                        adjCell1 = self.getAdjCellAtDir(cell, HexSideDir.UL)
                        registerVertexAtNeighbor(adjCell1, HexVertexDir.LR, vertex)
                        adjCell2 = self.getAdjCellAtDir(cell, HexSideDir.UR)
                        registerVertexAtNeighbor(adjCell2, HexVertexDir.LL, vertex)
                    elif vtxDir == HexVertexDir.UR:
                        adjCell1 = self.getAdjCellAtDir(cell, HexSideDir.UR)
                        registerVertexAtNeighbor(adjCell1, HexVertexDir.B, vertex)
                        adjCell2 = self.getAdjCellAtDir(cell, HexSideDir.R)
                        registerVertexAtNeighbor(adjCell2, HexVertexDir.UL, vertex)
                    elif vtxDir == HexVertexDir.LR:
                        adjCell1 = self.getAdjCellAtDir(cell, HexSideDir.R)
                        registerVertexAtNeighbor(adjCell1, HexVertexDir.LL, vertex)
                        adjCell2 = self.getAdjCellAtDir(cell, HexSideDir.LR)
                        registerVertexAtNeighbor(adjCell2, HexVertexDir.T, vertex)
                    elif vtxDir == HexVertexDir.B:
                        adjCell1 = self.getAdjCellAtDir(cell, HexSideDir.LL)
                        registerVertexAtNeighbor(adjCell1, HexVertexDir.UR, vertex)
                        adjCell2 = self.getAdjCellAtDir(cell, HexSideDir.LR)
                        registerVertexAtNeighbor(adjCell2, HexVertexDir.UL, vertex)
                    elif vtxDir == HexVertexDir.LL:
                        adjCell1 = self.getAdjCellAtDir(cell, HexSideDir.L)
                        registerVertexAtNeighbor(adjCell1, HexVertexDir.LR, vertex)
                        adjCell2 = self.getAdjCellAtDir(cell, HexSideDir.LL)
                        registerVertexAtNeighbor(adjCell2, HexVertexDir.T, vertex)
                    elif vtxDir == HexVertexDir.UL:
                        adjCell1 = self.getAdjCellAtDir(cell, HexSideDir.UL)
                        registerVertexAtNeighbor(adjCell1, HexVertexDir.B, vertex)
                        adjCell2 = self.getAdjCellAtDir(cell, HexSideDir.L)
                        registerVertexAtNeighbor(adjCell2, HexVertexDir.UR, vertex)
                    else:
                        raise AssertionError(f"Invalid vertex direction: {vtxDir}")

    def _registerSides(self):
        """Register the sides of each cell."""
        for cell in self.cells:
            for sideDir in HexSideDir:
                if cell.sides[sideDir] is None:
                    # Get the vertices for this side
                    vtxDir1, vtxDir2 = sideDir.connectedVertexDirs()
                    vtx1 = cell.vertices[vtxDir1]
                    vtx2 = cell.vertices[vtxDir2]

                    # Create the Side
                    side = HexSide(len(self.sides), vtx1, vtx2, self.cellSideWidth)
                    # Register the Side to the Cell
                    cell.sides[sideDir] = side
                    # Register the Cell as an adjacent cell of the Side
                    side.adjCells[sideDir] = cell
                    # Add this side to the list of all sides
                    self.sides.append(side)

                    # Look at the adjacent cell of this cell.
                    # If it is not None, also register it to the Side.
                    adjCell = cell.adjCells[sideDir]
                    if adjCell is not None:
                        adjCell.sides[sideDir.opposite()] = side
                        side.adjCells[sideDir.opposite()] = adjCell

    def _registerLimbs(self):
        """Register the limbs of each cell. A limb is a `HexSide` which is not part
        of the `HexCell` itself but connected to one of the cell's vertices."""

        def getLimb(cell, vtxDir):
            """Get the limb of a cell at a particular vertex direction."""
            vtx = cell.vertices[vtxDir]
            for limbCandidate in vtx.sides:
                # Check if the limbCandidate is not a part of the cell
                if limbCandidate not in cell.sides:
                    return limbCandidate
            # Cells at the edge of the board have no limbs at some vertices
            return None

        for cell in self.cells:
            for vtxDir in HexVertexDir:
                limb = getLimb(cell, vtxDir)
                cell.limbs[vtxDir] = limb
                if limb is not None:
                    limb.connCells[vtxDir] = cell

    def validateInputData(self):
        """Validates the initialization input.

        Args:
            rows (int): The number of rows of the board. Must be an odd number greater than 3.
            cellDataStr (string): The string containing the required sides of each cell.

        Raises:
            ValueError: If the rows or cell data is invalid.
        """

        if self.rows < 3 or self.rows % 2 == 0:
            raise ValueError("The number of rows must be an odd number greater than 1.")

        if self.cellDataStr is None:
            return

        # Get the total number of cells
        totalCells = 0
        numOfColsInRow = self.rows
        for row in range(self.rows // 2, -1, -1):
            totalCells += numOfColsInRow if row == self.rows // 2 else numOfColsInRow * 2
            numOfColsInRow -= 1

        if totalCells != len(self.cellDataStr):
            raise ValueError(f"The given data string has invalid length ({len(self.cellDataStr)}).")

        for c in self.cellDataStr:
            if c != "." and not c.isnumeric():
                raise ValueError(f"The given data string contains an invalid character ({c}).")

    def toggleSideStatus(self, side):
        """Toggle the given Side's status from `UNSET` to `ACTIVE` to `BLANK`."""
        if side.status == SideStatus.UNSET:
            move = HexGameMove(side.id, SideStatus.ACTIVE, None, SideStatus.UNSET)
        elif side.status == SideStatus.ACTIVE:
            move = HexGameMove(side.id, SideStatus.BLANK, None, SideStatus.ACTIVE)
        elif side.status == SideStatus.BLANK:
            move = HexGameMove(side.id, SideStatus.UNSET, None, SideStatus.BLANK)
        else:
            raise AssertionError(f"Invalid side status: {side.status}")
        self.setSideStatus(move)

    def setSideStatus(self, gameMove):
        """Set the status of a side, then recalculate stuff.

        Args:
            gameMove (HexGameMove): The move to be set.
        """

        side = self.sides[gameMove.sideId]
        newStatus = gameMove.newStatus
        prevStatus = gameMove.prevStatus

        # Do nothing if the current status is equal to the new status
        if side.status == newStatus:
            return

        # Do nothing if the move object's prevStatus does not equal to the current status
        if prevStatus is not None and prevStatus != side.status:
            return

        self.moveHistory.append(gameMove)

        if newStatus == SideStatus.ACTIVE:
            self._setSideActive(side)
        elif newStatus == SideStatus.BLANK:
            self._setSideBlank(side)
        elif newStatus == SideStatus.UNSET:
            side.setStatus(newStatus)
        else:
            raise AssertionError(f"Invalid side status: {newStatus}")

    def _setSideActive(self, side):
        """Set the side status to `ACTIVE`, then recalculate stuff.

        Calculates what color the `Side` will become, which depends on the connected links.

        Args:
            side (HexSide): The side to be set to active.
        """

        # Get the enpoints/vertices
        vtx1 = side.endpoints[0]
        vtx2 = side.endpoints[1]

        # Get the active sides at each endpoint
        activeSides1 = vtx1.getActiveSidesExcept(side.id)
        activeSides2 = vtx2.getActiveSidesExcept(side.id)

        if len(activeSides1) == 0 and len(activeSides2) == 0:
            # If both vtx1 and vtx2 have NO active sides
            nextColorIdx = helper.getLeastUsedColor(self.sides)
            side.setColorIdx(nextColorIdx)

        if len(activeSides1) > 0 and len(activeSides2) == 0:
            # If vtx1 has active sides but vtx2 does not
            side.setColorIdx(activeSides1[0].colorIdx)

        elif len(activeSides1) == 0 and len(activeSides2) > 0:
            # If vtx2 has active sides but vtx1 does not
            side.setColorIdx(activeSides2[0].colorIdx)

        elif len(activeSides1) > 0 and len(activeSides2) > 0:
            # If both have active sides
            link1 = helper.getLinkItems(activeSides1[0])
            link2 = helper.getLinkItems(activeSides2[0])
            if len(link1) >= len(link2):
                newColorIdx = self.sides[link1.pop()].colorIdx
                side.setColorIdx(newColorIdx)
                while len(link2) > 0:
                    self.sides[link2.pop()].setColorIdx(newColorIdx)
            else:
                newColorIdx = self.sides[link2.pop()].colorIdx
                side.setColorIdx(newColorIdx)
                while len(link1) > 0:
                    self.sides[link1.pop()].setColorIdx(newColorIdx)

        # Finally, set the status of the actual side
        side.setStatus(SideStatus.ACTIVE)

    def _setSideBlank(self, side):
        """Set the side status to `BLANK`, then recalculate stuff.

        Calculates what color the `Side` will become, which depends on the connected links.

        Args:
            side (HexSide): The side to be set to active.
        """

        # Make sure to set it to BLANK so that it will not be included in the link
        side.setStatus(SideStatus.BLANK)

        # Get the enpoints/vertices
        vtx1 = side.endpoints[0]
        vtx2 = side.endpoints[1]

        # Get the active sides at each endpoint
        activeSides1 = vtx1.getActiveSidesExcept(side.id)
        activeSides2 = vtx2.getActiveSidesExcept(side.id)

        # If both endpoints have active sides, then recalculate color of one endpoint.
        # However, if at least one endpoint has no active side, no need to do anything.
        if len(activeSides1) > 0 and len(activeSides2) > 0:
            link1 = helper.getLinkItems(activeSides1[0])
            link2 = helper.getLinkItems(activeSides2[0])

            if len(link1) >= len(link2):
                # If link1 is bigger, re-color link2
                exceptColorIdx = self.sides[link1.pop()].colorIdx
                newColorIdx = helper.getLeastUsedColor(self.sides, exceptColorIdx)
                while len(link2) > 0:
                    linkElem = self.sides[link2.pop()]
                    linkElem.setColorIdx(newColorIdx)

            else:
                # If link2 is bigger, re-color link1
                exceptColorIdx = self.sides[link2.pop()].colorIdx
                newColorIdx = helper.getLeastUsedColor(self.sides, exceptColorIdx)
                while len(link1) > 0:
                    linkElem = self.sides[link1.pop()]
                    linkElem.setColorIdx(newColorIdx)

    def getCell(self, row, col):
        """Get the cell at the specified row and column of the board. Returns None if not found."""
        if row < 0 or row >= self.rows:
            return None
        if col < 0 or col >= len(self.board[row]):
            return None
        return self.board[row][col]

    def getNumOfCols(self, row):
        """Returns how many columns a given row has.

        Args:
            row (int): The row number.

        Returns:
            int: The number of columns in the given row.

        Raises:
            ValueError: If the given row is invalid.
        """

        if row < 0 or row >= self.rows:
            raise ValueError(f"Invalid row number ({self.rows}).")

        if row == self.midRow:
            return self.rows
        if row < self.midRow:
            return self.rows - (self.midRow - row)

        return self.rows - (row - self.midRow)

    def getAdjCellAtDir(self, cell, direction):
        """Get the adjacent cell at a direction of a cell.

        Args:
            cell (HexCell): The cell to check.
            direction (HexSideDir): The direction of the adjacency.

        Returns:
            HexCell: The adjacent cell. Returns None if there is no adjacent cell.
        """

        if direction == HexSideDir.UL:
            if cell.row <= self.midRow:
                ret = self.getCell(cell.row - 1, cell.col - 1)
            else:
                ret = self.getCell(cell.row - 1, cell.col)

        elif direction == HexSideDir.UR:
            if cell.row <= self.midRow:
                ret = self.getCell(cell.row - 1, cell.col)
            else:
                ret = self.getCell(cell.row - 1, cell.col + 1)

        elif direction == HexSideDir.R:
            ret = self.getCell(cell.row, cell.col + 1)

        elif direction == HexSideDir.LR:
            if cell.row < self.midRow:
                ret = self.getCell(cell.row + 1, cell.col + 1)
            else:
                ret = self.getCell(cell.row + 1, cell.col)

        elif direction == HexSideDir.LL:
            if cell.row < self.midRow:
                ret = self.getCell(cell.row + 1, cell.col)
            else:
                ret = self.getCell(cell.row + 1, cell.col - 1)

        elif direction == HexSideDir.L:
            ret = self.getCell(cell.row, cell.col - 1)

        return ret
