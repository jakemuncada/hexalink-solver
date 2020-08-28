"""A file for testing stuff."""

CONST_INT_A = 123


def testCustomClassInSet():
    """Test adding and removing custom classes to/from sets."""
    mySet = set()

    print("Test to add/remove custom classes to/from sets.")

    print("FINDINGS:")
    print("   1.) CustomClass.__hash__(self) is required in order ")
    print("       to be able to add objects to the set.")
    print("   2.) Implementing __hash__ will allow you to add objects to the set,")
    print("       but if you don't implement __eq__, the equality will be based on")
    print("       actual object instance equality.")
    print()

    obj1 = CustomClass(1, 3, "a", "b")
    obj2 = CustomClass(1, 4, "a", "b")  # Equal to obj1
    obj3 = CustomClass(2, 2, "a", "b")
    obj4 = CustomClass(3, 2, "a", "b")
    obj5 = CustomClass(3, 2, "b", "b")
    obj6 = CustomClass(4, 2, "c", "b")
    obj7 = CustomClass(3, 4, "a", "x")  # Equal to obj4

    mySet.add(obj1)
    mySet.add(obj2)
    mySet.add(obj3)
    mySet.add(obj4)
    mySet.add(obj5)
    mySet.add(obj6)
    mySet.add(obj7)

    print(f"Expected length of mySet is 5. Actual size of mySet is {len(mySet)}.")
    for obj in mySet:
        print(obj)

###############################
# CLASSES
###############################


class CustomClass:
    """A custom class for testing.

    Equality Check:
        Two objects are equal if their intA and strA are equal.
        intB and strB are not checked.
    """

    def __init__(self, intA, intB, strA, strB):
        self.intA = intA
        self.intB = intB
        self.strA = strA
        self.strB = strB

    def __eq__(self, other):
        return isinstance(other, CustomClass) and self.intA == other.intA \
            and self.strA == other.strA

    def __hash__(self):
        return hash((self.intA, self.strA))

    def __str__(self):
        return f"{self.intA} {self.intB} {self.strA} {self.strB}"


###############################
# MAIN
###############################
if __name__ == "__main__":
    testCustomClassInSet()
