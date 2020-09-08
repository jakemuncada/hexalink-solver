"""Side Link"""

from hex_side import HexSide


class SideLink:
    """
    A set of Sides that are linked. A link cannot have a BLANK side.

    A side is linked with another side if:
        1. Both sides are UNSET or ACTIVE. (Neither side is BLANK.)
        2. Both sides share a common vertex.
        3. All other Sides which also share the common vertex are BLANK.
    """

    __createKey = object()

    def __init__(self, createKey, sides, linkVertices, endpoints, endLinks):
        """
        Instantiate a SideLink. Cannot be used directly. Please use `fromSide` or `fromList`.

        Args:
            sides ([HexSide]): The list of sides that compose the link.
            linkVertices ([HexVertex]): The vertices on that connects each individual link member.
                                        Does not include the endpoints.
            endpoints (HexVertex, HexVertex): The endpoints of the link.
            endLinks (HexSide, HexSide): The sides of the link connected to each endpoint.
        """

        assert(createKey == self.__createKey), \
            "Please use class method 'fromSide' or 'fromList' to instantiate a SideLink."
        self.sides = sides
        self.linkVertices = linkVertices
        self.endpoints = endpoints
        self.endLink = endLinks

    @classmethod
    def fromList(cls, sides):
        """
        Creates a link given a list/set of sides. Also, the `linkVertices` and the `endpoints`
        are calculated and stored.

        Raises:
            AssertionError: If the sides do not form a valid link or if all the sides
                do not have the same status.
        """
        isValid, linkVertices, endpoints, endLinks = cls._validate(sides)

        if isValid:
            return cls(cls.__createKey, sides, linkVertices, endpoints, endLinks)
        return None

    @classmethod
    def fromSide(cls, side, filterFxn=None):
        """
        Create a link from a given side. All sides will have the same status.\n
        Can optionally include a filter function to check if a particular side should be included.

        Returns None if the created link is invalid. For example:
            1. When the given side is BLANK.
            2. When the side is ACTIVE and contains a loop.
        """
        # Blank sides cannot form a link
        if side.isBlank():
            return None

        # If the given side doesn't even pass the filter function, return None
        if filterFxn is not None and not filterFxn(side):
            return None

        def getLink(side, groupSet):
            """Returns set of all the sides that are part of the same link as a given Side."""

            # Recursion base case
            if side in groupSet:
                return groupSet

            # If the side does not pass the filter function, don't include it
            if filterFxn is not None and not filterFxn(side):
                return groupSet

            groupSet.add(side)

            linkedSides = side.getAllLinkedSides()
            for linkedSide in linkedSides:
                allLinks = getLink(linkedSide, groupSet)
                groupSet.update(allLinks)

            return groupSet

        sides = getLink(side, set())
        isValid, linkVertices, endpoints, endLinks = cls._validate(sides)

        if isValid:
            return cls(cls.__createKey, sides, linkVertices, endpoints, endLinks)
        return None

    @staticmethod
    def _validate(sides):
        """
        Checks if the given Side list is a valid SideLink.

        Returns:
            (isValid, linkVertices, endpoints)
            isValid (bool): True if the given list is valid.
            linkVertices (HexVertex): The list of vertices that connect the link sides.
                                      None if the list isn't valid.
            endpoints (HexVertex, HexVertex): A tuple of the two endpoints of the link.
                                              None if the list isn't valid.
            endLinks (HexSide, HexSide): The sides of the link connected to each endpoint.
        """
        if sides is None or len(sides) <= 0:
            return False, None, None, None

        sides = list(sides)

        # Check if the sides[0] is BLANK.
        # The other sides should be equal to sides[0].
        if sides[0].isBlank():
            return False, None, None, None

        linkVertices = []

        # The count of sides connected to each vertex
        vertexConnCount = {}

        for side in sides:
            if side.status != sides[0].status:
                return False, None, None, None
            for vtx in side.endpoints:
                if vtx not in vertexConnCount:
                    vertexConnCount[vtx] = 1
                else:
                    vertexConnCount[vtx] += 1

        endpoints = []
        for vtx in vertexConnCount:
            count = vertexConnCount[vtx]

            # If only one side connects to the vertex, it is an endpoint
            if count == 1:
                endpoints.append(vtx)
            # If two sides connect to the vertex, it is a linkVertex
            elif count == 2:
                linkVertices.append(vtx)
            # Else if the vertex has 3 or more sides connecting to it, the SideLink is invalid
            else:
                return False, None, None, None

        # Check that the number of endpoints and linkVertices are valid
        if len(endpoints) != 2:
            return False, None, None, None
        if len(linkVertices) != len(sides) - 1:
            return False, None, None, None

        endLinks = []
        for endpoint in endpoints:
            for side in sides:
                if endpoint in side.endpoints:
                    endLinks.append(side)
                    break
        assert(len(endLinks) == 2), "Expected there to be only 2 endlinks"

        return True, linkVertices, tuple(endpoints), tuple(endLinks)

    @staticmethod
    def isSameLink(side1, side2):
        """
        Returns true if the two sides are part of the same link.

        This implementation is possibly faster than getting the entire link
        because it will return true as soon as the target is found.
        """

        # False if either side is None or Blank
        if side1 is None or side2 is None or side1.isBlank() or side2.isBlank():
            return False

        # False if they are not the same status
        if side1.status != side2.status:
            return False

        def findSideInLink(side, target, groupSet):
            """Returns true if the target is part of the same link of a given side."""

            # Recursion base cases
            if side == target:
                return True
            if side in groupSet:
                return False

            groupSet.add(side)

            linkedSides = side.getAllLinkedSides()
            for linkedSide in linkedSides:
                found = findSideInLink(linkedSide, target, groupSet)
                if found:
                    return True

            return False

        return findSideInLink(side1, side2, set())

    def isUnset(self):
        """Returns true if all the sides in the link are unset. False otherwise."""
        for side in self.sides:
            if not side.isUnset():
                return False
        return True

    def isActive(self):
        """Returns true if all the sides in the link are active. False otherwise."""
        for side in self.sides:
            if not side.isActive():
                return False
        return True

    def isBlank(self):
        """Returns true if all the sides in the link are blank. False otherwise."""
        for side in self.sides:
            if not side.isBlank():
                return False
        return True

    def getConnectionVertex(self, other):
        """
        Get the vertex that is common between this SideLink and a given SideLink or Side.\n
        Returns None if the two aren't connected.

        Args:
            other (SideLink or HexSide): The other sidelink or side.

        Returns:
            HexVertex: The common vertex. None if not connected.
        """

        if other.endpoints[0] in self.endpoints:
            return other.endpoints[0]
        elif other.endpoints[1] in self.endpoints:
            return other.endpoints[1]
        return None

    def __len__(self):
        return len(self.sides)

    def __iter__(self):
        return self.sides.__iter__()
