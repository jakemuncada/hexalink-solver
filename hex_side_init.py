"""HexSide Initializer"""


class HexSideInitializer:
    """A class responsible for initializing stuff in HexSide."""

    @staticmethod
    def getAllConnectedSides(side):
        """Returns all the connected sides of a given HexSide."""
        ret = []
        for connSide in side.endpoints[0].getAllSidesExcept(side.id):
            ret.append(connSide)
        for connSide in side.endpoints[1].getAllSidesExcept(side.id):
            ret.append(connSide)
        return ret

    @staticmethod
    def getConnectedSidesByVertex(side):
        """Returns the connected sides sorted by vertex."""
        connSidesAtVtx1 = side.endpoints[0].getAllSidesExcept(side.id)
        connSidesAtVtx2 = side.endpoints[1].getAllSidesExcept(side.id)
        return (connSidesAtVtx1, connSidesAtVtx2)

    @staticmethod
    def getConnectionVertices(side):
        """Returns a dictionary containing the common vertex between
        the given side and its connected sides."""
        connVertexDict = {}
        for connSide in HexSideInitializer.getAllConnectedSides(side):
            if side.endpoints[0] in connSide.endpoints:
                connVertexDict[connSide.id] = side.endpoints[0]
            elif side.endpoints[1] in connSide.endpoints:
                connVertexDict[connSide.id] = side.endpoints[1]
        return connVertexDict

    @staticmethod
    def getOtherConnectedSidesMemo(side):
        """Returns a dictionary containing the other Sides commonly connected to
        both the given side and another Side."""
        ret = {}
        for connSide in HexSideInitializer.getAllConnectedSides(side):
            tmp = []
            # Get common vertex
            commonVertex = side.getConnectionVertex(connSide)
            # Get all other sides which share the common vertex
            for commonSide in commonVertex.sides:
                if commonSide != side and commonSide != connSide:
                    tmp.append(commonSide)
            ret[connSide.id] = tmp
        return ret
