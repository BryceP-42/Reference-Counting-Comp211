# Example 2: alias vs copy vs deepcopy

## demonstrates how many references are createed with an alias, copy, and deepcopy.
import copy
import sys


class Thing:
    pass


inner = Thing()
a = [inner]
print("a = [inner]           ->", sys.getrefcount(inner) - 1)

b = a
print("b = a                 ->", sys.getrefcount(inner) - 1)

c = a.copy()
print("c = a.copy()          ->", sys.getrefcount(inner) - 1)

d = copy.deepcopy(a)
print("d = copy.deepcopy(a)  ->", sys.getrefcount(inner) - 1)
print("Is d[0] the same object as inner?", d[0] is inner)


