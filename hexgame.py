"""The Hexagon Slitherlink Game"""


from hexside import HexSide
from sidestatus import SideStatus
from hexdir import HexSideDir, HexVertexDir
from hexcell import HexCell
from hexvertex import HexVertex
from constants import SIDE_COLORS
from point import Point
import helpers


class HexGame:
    """The Hexagon Slitherlink class."""

    def __init__(self, center, cellSideWidth, rows, cellData=None):
        """Create a HexGame.

        Args:
            center (2-tuple): The center coordinates of the board.
            cellSideWidth (int): The width of the side of the cell.
            rows (int): The number of rows of the board. Must be an odd number greater than 3.
            cellData (string): The string containing the required sides of each cell. Optional.

        Raises:
            ValueError: If the rows or cell data is invalid.
        """

        self.rows = rows
        self.cellSideWidth = cellSideWidth
        self.cellData = cellData
        self.center = Point(center)

        # Validate and initialize the data
        self.validateInputData()
        self.init()

    def init(self):
        """Initialize the board. Can be called again to reset board."""
        self.midRow = self.rows // 2
        self.board = [[] for _ in range(self.rows)]
        self.cells = []
        self.sides = []
        self.vertices = []

        # Populate the cells
        cellIdx = 0
        for row in range(self.rows):
            for col in range(self.getNumOfCols(row)):
                reqSides = self.cellData[cellIdx] if self.cellData is not None else "."
                reqSides = None if reqSides == "." else int(reqSides)
                cell = HexCell(row, col, self.cellSideWidth, reqSides)
                cell.calcCoords(self.center, self.rows)
                self.board[row].append(cell)
                self.cells.append(cell)
                cellIdx += 1

        self._registerAdjacentCells()
        self._registerVertices()
        self._registerSides()
        # self._registerSideConnectivity()

    def _registerAdjacentCells(self):
        """Register the adjacent cells of each cell."""
        for rowArr in self.board:
            for cell in rowArr:
                for sideDir in HexSideDir:
                    adjCell = self.getAdjCellAtDir(cell, sideDir)
                    cell.adjCells[sideDir] = adjCell

    def _registerVertices(self):
        """Register the vertices of each cell."""

        def registerVertexAtNeighbor(neighborCell, direction, vertex):
            if neighborCell is not None:
                neighborCell.vertices[direction] = vertex

        for rowArr in self.board:
            for cell in rowArr:
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
        for rowArr in self.board:
            for cell in rowArr:
                for sideDir in HexSideDir:
                    if cell.sides[sideDir] is None:
                        # Get the vertices for this side
                        vtxDir1, vtxDir2 = sideDir.connectedVertex()
                        vtx1 = cell.vertices[vtxDir1]
                        vtx2 = cell.vertices[vtxDir2]

                        # Create the Side
                        side = HexSide(len(self.sides), vtx1, vtx2, self.cellSideWidth)
                        # Register the Side to the Cell
                        cell.sides[sideDir] = side
                        # Register the Cell as an adjacent cell of the Side
                        side.registerAdjacentCell(cell, sideDir)
                        # Add this side to the list of all sides
                        self.sides.append(side)

                        # Look at the adjacent cell of this cell.
                        # If it is not None, also register it to the Side.
                        adjCell = cell.adjCells[sideDir]
                        if adjCell is not None:
                            adjCell.sides[sideDir.opposite()] = side
                            side.registerAdjacentCell(adjCell, sideDir.opposite())

    def validateInputData(self):
        """Validates the initialization input.

        Args:
            rows (int): The number of rows of the board. Must be an odd number greater than 3.
            cellData (string): The string containing the required sides of each cell.

        Raises:
            ValueError: If the rows or cell data is invalid.
        """

        if self.rows < 3 or self.rows % 2 == 0:
            raise ValueError("The number of rows must be an odd number greater than 1.")

        if self.cellData is None:
            return

        # Get the total number of cells
        totalCells = 0
        numOfColsInRow = self.rows
        for row in range(self.rows // 2, -1, -1):
            totalCells += numOfColsInRow if row == self.rows // 2 else numOfColsInRow * 2
            numOfColsInRow -= 1

        if totalCells != len(self.cellData):
            raise ValueError(f"The given data string has invalid length ({len(self.cellData)}).")

        for c in self.cellData:
            if c != "." and not c.isnumeric():
                raise ValueError(f"The given data string contains an invalid character ({c}).")

    def toggleSideStatus(self, side):
        """Toggle the given Side's status from `UNSET` to `ACTIVE` to `BLANK`."""
        if side.status == SideStatus.UNSET:
            self.setSideStatus(side, SideStatus.ACTIVE)
        elif side.status == SideStatus.ACTIVE:
            self.setSideStatus(side, SideStatus.BLANK)
        elif side.status == SideStatus.BLANK:
            self.setSideStatus(side, SideStatus.UNSET)
        else:
            raise AssertionError(f"Invalid side status: {side.status}")

    def setSideStatus(self, side, newStatus):
        """Set the status of a side, then recalculate stuff.

        Args:
            side (HexSide): The side whose status is to be set.
            newStatus (SideStatus): The new status.
        """

        if side.status == newStatus:
            return

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
            nextColorIdx = helpers.getLeastUsedColor(self.sides)
            side.setColorIdx(nextColorIdx)

        if len(activeSides1) > 0 and len(activeSides2) == 0:
            # If vtx1 has active sides but vtx2 does not
            side.setColorIdx(activeSides1[0].colorIdx)

        elif len(activeSides1) == 0 and len(activeSides2) > 0:
            # If vtx2 has active sides but vtx1 does not
            side.setColorIdx(activeSides2[0].colorIdx)

        elif len(activeSides1) > 0 and len(activeSides2) > 0:
            # If both have active sides
            link1 = helpers.getLinkItems(activeSides1[0])
            link2 = helpers.getLinkItems(activeSides2[0])
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
            link1 = helpers.getLinkItems(activeSides1[0])
            link2 = helpers.getLinkItems(activeSides2[0])

            if len(link1) >= len(link2):
                # If link1 is bigger, re-color link2
                exceptColorIdx = self.sides[link1.pop()].colorIdx
                newColorIdx = helpers.getLeastUsedColor(self.sides, exceptColorIdx)
                while len(link2) > 0:
                    linkElem = self.sides[link2.pop()]
                    linkElem.setColorIdx(newColorIdx)

            else:
                # If link2 is bigger, re-color link1
                exceptColorIdx = self.sides[link2.pop()].colorIdx
                newColorIdx = helpers.getLeastUsedColor(self.sides, exceptColorIdx)
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

    def getNearestSide(self, point):
        """Get the nearest side from a point.

        Args:
            point (Point): The reference point.

        Returns:
            (HexSide, float): The nearest side and its distance from the point.
        """

        minDist = 999999999.0
        nearestSide = None

        for side in self.sides:
            endPt1 = side.endpoints[0].coords
            endPt2 = side.endpoints[1].coords
            dist = helpers.pointToLineDist(endPt1, endPt2, point)
            if dist < minDist:
                minDist = dist
                nearestSide = side

        return nearestSide, minDist
